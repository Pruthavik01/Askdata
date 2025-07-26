# AskDB 📊 – Natural Language to SQL Query Engine

**AskDB** is an AI-powered data exploration tool that allows non-technical users to ask natural language questions and automatically get SQL queries, answers, and charts—without writing code.

Built with Gemini AI, it supports:
- 📁 CSV / Excel file uploads
- 🛢️ Live MySQL database connections
- 🤖 Natural language question to SQL conversion
- 📈 Visual data insights using Chart.js

---

## 🚀 Features

- 🔁 **Switch between File and MySQL Data Sources**
- 📤 **Upload CSV/XLSX Files**
- 🛢️ **Connect to MySQL Databases** and browse databases/tables
- 🤖 **Gemini API Integration** for generating SQL queries from questions
- 📄 **Schema Preview & SQL Output**
- 📊 **Auto-render Charts** from query results

---

## 🧰 Tech Stack

| Layer      | Tools / Libraries                           |
|------------|---------------------------------------------|
| Frontend   | HTML, CSS, JavaScript, Chart.js             |
| Backend    | Flask (Python), Pandas, MySQL Connector     |
| AI Engine  | Google Generative AI (`gemini-1.5-flash`)   |
| Database   | MySQL (remote or local)                     |

---
## 📷Images
![127 0 0 1_5000_(iPhone XR)](https://github.com/user-attachments/assets/e900303c-62bc-4dde-a37a-d0e916ffa210)


## ⚙️ Requirements

Install the following tools before running:

- Python 3.8+
- MySQL Server (optional if using only CSV/XLSX)
- Node.js (if using additional build tools)

Install Python dependencies:
```bash
pip install -r requirements.txt

