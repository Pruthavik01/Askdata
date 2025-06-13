let currentFile = null;
let currentDataSource = 'file'; // 'file' or 'mysql'
let currentMysqlSchema = null;

// Source selection event listeners
document.getElementById('fileBtn').addEventListener('click', function() {
    switchDataSource('file');
});

document.getElementById('mysqlBtn').addEventListener('click', function() {
    switchDataSource('mysql');
});

function switchDataSource(source) {
    currentDataSource = source;
    
    // Update buttons
    document.querySelectorAll('.source-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    if (source === 'file') {
        document.getElementById('fileBtn').classList.add('active');
        document.getElementById('fileUploadSection').style.display = 'block';
        document.getElementById('mysqlSection').style.display = 'none';
    } else {
        document.getElementById('mysqlBtn').classList.add('active');
        document.getElementById('fileUploadSection').style.display = 'none';
        document.getElementById('mysqlSection').style.display = 'block';
    }
    
    // Clear any previous data
    document.getElementById('dataPreview').innerHTML = '';
    document.getElementById('sqlSection').innerHTML = '';
    document.getElementById('answerSection').innerHTML = '';
}

// FILE UPLOAD FUNCTIONALITY
async function handleUpload(file) {
    if (!file) return; // Prevent errors if no file is selected

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        currentFile = result;
        document.getElementById('dataPreview').innerHTML = result.preview;
    } catch (error) {
        console.error("Upload failed:", error);
    }
}

// Automatically upload when file is selected
document.getElementById('fileInput').addEventListener('change', function () {
    handleUpload(this.files[0]);
});

// Drag and drop functionality
const dropArea = document.getElementById("dropArea");

dropArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropArea.classList.add("active");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("active");
});

dropArea.addEventListener("drop", (event) => {
    event.preventDefault();
    dropArea.classList.remove("active");

    let files = event.dataTransfer.files;
    if (files.length > 0) {
        handleUpload(files[0]);
    }
});

// MYSQL FUNCTIONALITY
document.getElementById('connectBtn').addEventListener('click', async function() {
    const host = document.getElementById('host').value;
    const port = document.getElementById('port').value;
    const user = document.getElementById('user').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/connect_mysql', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ host, port, user, password })
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert(`Connection failed: ${result.error}`);
            return;
        }
        
        // Populate database dropdown
        const databaseSelect = document.getElementById('databaseSelect');
        databaseSelect.innerHTML = '';
        
        result.databases.forEach(db => {
            const option = document.createElement('option');
            option.value = db;
            option.textContent = db;
            databaseSelect.appendChild(option);
        });
        
        // Show database selection
        document.getElementById('dbTableSelection').style.display = 'block';
        
    } catch (error) {
        console.error("MySQL connection failed:", error);
        alert("Failed to connect to MySQL server. Please check your credentials.");
    }
});

// When database is selected, fetch tables
document.getElementById('databaseSelect').addEventListener('change', async function() {
    const database = this.value;
    
    try {
        const response = await fetch('/get_tables', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ database })
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert(`Failed to get tables: ${result.error}`);
            return;
        }
        
        // Populate table dropdown
        const tableSelect = document.getElementById('tableSelect');
        tableSelect.innerHTML = '';
        
        result.tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.textContent = table;
            tableSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error("Failed to fetch tables:", error);
    }
});

// Load selected table
document.getElementById('loadTableBtn').addEventListener('click', async function() {
    const database = document.getElementById('databaseSelect').value;
    const table = document.getElementById('tableSelect').value;
    
    if (!database || !table) {
        alert("Please select both database and table");
        return;
    }
    
    try {
        const response = await fetch('/load_table', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ database, table })
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert(`Failed to load table: ${result.error}`);
            return;
        }
        
        // Save schema and display preview
        currentMysqlSchema = result.schema;
        document.getElementById('dataPreview').innerHTML = result.preview;
        
    } catch (error) {
        console.error("Failed to load table:", error);
    }
});

// QUERY SUBMISSION
async function submitQuestion() {
    const question = document.getElementById('questionInput').value;
    
    if (!question) {
        alert("Please enter a question");
        return;
    }
    
    // Check if we have data to query
    if (currentDataSource === 'file' && !currentFile) {
        alert("Please upload a file first");
        return;
    } else if (currentDataSource === 'mysql' && !currentMysqlSchema) {
        alert("Please select and load a table first");
        return;
    }
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question: question,
                schema: currentDataSource === 'file' ? currentFile.schema : currentMysqlSchema,
                source: currentDataSource,
                database: currentDataSource === 'mysql' ? document.getElementById('databaseSelect').value : null,
                table: currentDataSource === 'mysql' ? document.getElementById('tableSelect').value : null
            })
        });

        const result = await response.json();
        
        if (result.error) {
            alert(`Query failed: ${result.error}`);
            return;
        }
        
        document.getElementById('answerSection').innerHTML = result.answer;
        document.getElementById('sqlSection').innerHTML = `<pre>${result.sql}</pre>`;
        
        if(result.chart_data) {
            renderChart(result.chart_data);
        }
    } catch (error) {
        console.error("Query failed:", error);
        alert("Failed to process your question");
    }
}