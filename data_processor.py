# import pandas as pd

# def process_data(filepath: str):
#     # Read file
#     if filepath.endswith('.csv'):
#         df = pd.read_csv(filepath)
#     elif filepath.endswith('.xlsx'):
#         df = pd.read_excel(filepath)
    
#     # Generate schema description
#     schema = []
#     for col, dtype in zip(df.columns, df.dtypes):
#         schema.append(f"{col} ({dtype})")
    
#     return df, "\n".join(schema)


import pandas as pd
import mysql.connector

def process_data(filepath: str):
    # Read file
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)

    # Generate schema description
    schema = []
    for col, dtype in zip(df.columns, df.dtypes):
        schema.append(f"{col} ({dtype})")

    return df, "\n".join(schema)

def process_mysql_data(host: str, user: str, password: str, database: str, table: str, port='3307'):
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )
        
        # Query database structure
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table}")
        columns_info = cursor.fetchall()
        
        # Query data
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, connection)
        
        # Generate schema description
        schema = []
        for col_info in columns_info:
            col_name = col_info[0]
            col_type = col_info[1]
            schema.append(f"{col_name} ({col_type})")
        
        connection.close()
        
        return df, "\n".join(schema)
    except Exception as e:
        raise Exception(f"Error processing MySQL data: {str(e)}")