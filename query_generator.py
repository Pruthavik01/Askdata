
import google.generativeai as genai

def generate_sql(question: str, schema: str) -> str:
    genai.configure(api_key='GEMINI_API_KEY')

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
You are an expert SQL query generator.

Given the following database schema:
{schema}

Translate the following natural language question into an equivalent SQL query:
"{question}"

Requirements:
- Use the actual table and column names as defined in the schema.
- If the data source is a CSV or Excel file, assume the table is named 'df'.
- Do not include any explanations, comments, or additional text.
- Output only the raw SQL query.

SQL Query:
"""

    response = model.generate_content(prompt)
    return response.text.strip()
