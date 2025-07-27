from flask import Flask, render_template, request, jsonify, session
import os
from data_processor import process_data
from query_generator import generate_sql

import pandas as pd
import sqlite3
from pandasql import sqldf
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Required for session management

# Store MySQL connection info in session
@app.route('/')
def index():
    return render_template('index.html')

uploaded_file_path = None  # Global variable to store the file path

@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_file_path  # Use global variable

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(uploaded_file_path)

    # Process data and get schema
    df, schema = process_data(uploaded_file_path)
    return jsonify({'schema': schema, 'preview': df.head(10).to_html()})

# MySQL Connection Endpoints
@app.route('/connect_mysql', methods=['POST'])
def connect_mysql():
    data = request.json
    host = data.get('host', 'localhost')
    port = data.get('port', 3306)
    user = data.get('user')
    password = data.get('password')
    
    try:
        # Establish connection
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            # Get list of databases
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall() if not db[0].startswith('information_schema')]
            cursor.close()
            
            # Store connection info in session
            session['mysql'] = {
                'host': host,
                'port': port,
                'user': user,
                'password': password
            }
            
            return jsonify({'success': True, 'databases': databases})
    
    except Error as e:
        return jsonify({'error': str(e)})
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/get_tables', methods=['POST'])
def get_tables():
    data = request.json
    database = data.get('database')
    
    if not database:
        return jsonify({'error': 'No database specified'})
    
    if 'mysql' not in session:
        return jsonify({'error': 'No MySQL connection information found. Please reconnect.'})
    
    conn_info = session['mysql']
    
    try:
        # Connect to the specified database
        connection = mysql.connector.connect(
            host=conn_info['host'],
            port=conn_info['port'],
            user=conn_info['user'],
            password=conn_info['password'],
            database=database
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            
            # Store selected database in session
            session['mysql']['database'] = database
            
            return jsonify({'success': True, 'tables': tables})
    
    except Error as e:
        return jsonify({'error': str(e)})
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/load_table', methods=['POST'])
def load_table():
    data = request.json
    database = data.get('database')
    table = data.get('table')
    
    if not database or not table:
        return jsonify({'error': 'Database and table must be specified'})
    
    if 'mysql' not in session:
        return jsonify({'error': 'No MySQL connection information found. Please reconnect.'})
    
    conn_info = session['mysql']
    
    try:
        # Connect to the specified database
        connection = mysql.connector.connect(
            host=conn_info['host'],
            port=conn_info['port'],
            user=conn_info['user'],
            password=conn_info['password'],
            database=database
        )
        
        if connection.is_connected():
            # Get schema information
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            schema = []
            for col in columns:
                schema.append(f"{col['Field']} ({col['Type']})")
            
            # Get a preview of the data
            cursor.execute(f"SELECT * FROM {table} LIMIT 10")
            rows = cursor.fetchall()
            
            # Convert to DataFrame for HTML preview
            df = pd.DataFrame(rows)
            
            # Store selected table in session
            session['mysql']['table'] = table
            
            return jsonify({
                'success': True, 
                'schema': '\n'.join(schema), 
                'preview': df.to_html()
            })
    
    except Error as e:
        return jsonify({'error': str(e)})
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def process_chart_data(result, question):
    """Processes DataFrame into chart data format."""
    if result.empty:
        return {'labels': [], 'values': {}, 'title': f"Overall Data - {question}"}

    # Dynamically selecting column names
    label_column = result.columns[0]  # First column as labels
    numeric_columns = result.select_dtypes(include=['number']).columns.tolist()  # Numeric columns
    
    if not numeric_columns and len(result.columns) > 1:
        # If no numeric columns, try to convert some columns to numeric if possible
        for col in result.columns[1:]:  # Skip first column (labels)
            try:
                result[col] = pd.to_numeric(result[col])
                numeric_columns.append(col)
            except:
                continue

    return {
        'labels': result[label_column].astype(str).tolist(),
        'values': {col: result[col].fillna(0).tolist() for col in numeric_columns},
        'title': f"Data for: {question}"
    }

@app.route('/ask', methods=['POST'])
def handle_question():
    global uploaded_file_path  # Use global variable

    data = request.json
    question = data['question']
    schema = data['schema']
    source = data.get('source', 'file')
    
    # Generate SQL using Generative AI
    sql_query = generate_sql(question, schema).strip("```sql").strip("```").strip()
    
    # Different execution based on source
    if source == 'file':
        if not uploaded_file_path:
            return jsonify({'error': 'No file uploaded yet'}), 400
        
        # Execute query using the stored file path
        result = execute_query_from_file(sql_query, uploaded_file_path)
    else:  # MySQL
        database = data.get('database')
        table = data.get('table')
        
        if not database or not table:
            return jsonify({'error': 'Database and table must be specified'}), 400
        
        if 'mysql' not in session:
            return jsonify({'error': 'No MySQL connection information found. Please reconnect.'}), 400
        
        # Execute query from MySQL
        result = execute_query_from_mysql(sql_query, database, table)
    
    if isinstance(result, str):  # Error message
        return jsonify({'error': result}), 400

    # Convert the result DataFrame to an HTML table
    table_html = result.to_html(classes='table table-striped', index=False)

    # Process chart data separately
    chart_data = process_chart_data(result, question)

    return jsonify({
        'answer': table_html,
        'sql': sql_query,
        'chart_data': chart_data,
    })

def execute_query_from_file(sql_query, filepath):
    """
    Executes an SQL query on a CSV file stored in the uploads folder.
    :param sql_query: The SQL query to execute.
    :param filepath: Path to the uploaded CSV file.
    :return: Query result as a Pandas DataFrame or error string.
    """
    try:
        # Load the CSV file into a Pandas DataFrame
        df = pd.read_csv(filepath)

        # Ensure the query does NOT contain Markdown-style formatting
        sql_query = sql_query.strip()  # Remove unnecessary spaces/newlines

        # Execute the SQL query using pandasql
        result = sqldf(sql_query, locals())
        return result
    except Exception as e:
        return str(e)

def execute_query_from_mysql(sql_query, database, table):
    """
    Executes an SQL query on a MySQL database.
    :param sql_query: The SQL query to execute.
    :param database: Database name.
    :param table: Table name (used for validation).
    :return: Query result as a Pandas DataFrame or error string.
    """
    if 'mysql' not in session:
        return "MySQL connection information not found"
    
    conn_info = session['mysql']
    
    try:
        # Replace the DataFrame reference (df) with the actual table name in the query
        adjusted_query = sql_query.replace("df", table)
        
        # Connect to database
        connection = mysql.connector.connect(
            host=conn_info['host'],
            port=conn_info['port'],
            user=conn_info['user'],
            password=conn_info['password'],
            database=database
        )
        
        if connection.is_connected():
            # Execute query and fetch results
            result = pd.read_sql(adjusted_query, connection)
            return result
        
    except Error as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error executing query: {str(e)}"
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    port = int(os.environ.get("PORT", 5000))  # Use PORT from Render
    app.run(host="0.0.0.0", port=port, debug=True)  # Bind to 0.0.0.0
