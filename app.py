import os
from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

print("Starting SQL Query Generator...")

def parse_schema(schema):
    """Parse schema text into a structured format"""
    tables = {}
    current_table = None
    for line in schema.split('\n'):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        if line.startswith('Table:'):
            current_table = line.replace('Table:', '').strip()
            tables[current_table] = []
        elif line.startswith('-') and current_table:
            parts = line.replace('-', '').split('(')
            col = parts[0].strip()
            col_type = parts[1].replace(')', '').strip() if len(parts) > 1 else ''
            tables[current_table].append({
                'name': col,
                'type': col_type,
                'is_key': 'primary key' in col_type.lower() or 'foreign key' in col_type.lower()
            })
    return tables

def find_foreign_key_relationship(tables, source_table, target_table):
    """Find foreign key relationship between two tables"""
    if source_table not in tables or target_table not in tables:
        return None
    
    # Look for foreign key in source table referencing target table
    for col in tables[source_table]:
        if ('foreign key' in col['type'].lower() and 
            target_table.lower().rstrip('s') in col['name'].lower()):
            return {
                'source_col': col['name'],
                'target_col': 'id'  # Assuming primary key is always 'id'
            }
    return None

def english_to_sql(prompt, schema):
    try:
        prompt = prompt.lower()
        print(f"Processing prompt: {prompt}")
        
        # Parse schema
        tables = parse_schema(schema)
        print(f"Parsed tables:", tables)
        
        # Check for username-based query
        username_match = re.search(r"username\s*[=']?\s*'([^']*)'", prompt)
        if username_match:
            username = username_match.group(1)
            print(f"Found username: {username}")
            
            # Determine the main table (looking for 'customer' or similar in prompt)
            main_table = None
            for table_name in tables:
                if table_name.lower() in prompt:
                    main_table = table_name
                    break
            
            if not main_table and 'customers' in tables:
                main_table = 'customers'
            
            if main_table and 'users' in tables:
                # Find relationship between tables
                relationship = find_foreign_key_relationship(tables, main_table, 'users')
                
                if relationship:
                    # Get non-key columns from main table
                    columns = [col['name'] for col in tables[main_table] 
                             if not col['is_key'] and 'foreign key' not in col['type'].lower()]
                    
                    # Build the query
                    columns_str = ', '.join(f"t1.{col}" for col in columns)
                    sql = f"""SELECT {columns_str}
FROM {main_table} t1
JOIN users t2 ON t1.{relationship['source_col']} = t2.{relationship['target_col']}
WHERE t2.username = '{username}'"""
                    
                    print(f"Generated SQL: {sql}")
                    return sql
        
        return "Error: Could not generate appropriate SQL query. Please check the schema and try again."
        
    except Exception as e:
        print(f"Error generating SQL: {str(e)}")
        return f"Error: Could not generate SQL query - {str(e)}"

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SQL Query Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 900px; margin: 0 auto; }
            textarea { width: 100%; margin: 10px 0; padding: 10px; }
            button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; margin: 5px; }
            .result { margin-top: 20px; padding: 10px; background-color: #f5f5f5; }
            .table-container { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .table-header { display: flex; justify-content: space-between; align-items: center; }
            .remove-btn { background-color: #ff4444; }
            .schema-area { margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SQL Query Generator</h1>
            
            <div id="tables-container">
                <h3>Database Schema:</h3>
                <div id="table-list">
                    <div class="table-container">
                        <div class="table-header">
                            <input type="text" placeholder="Table Name" value="users" style="padding: 5px;">
                            <button class="remove-btn" onclick="removeTable(this)">Remove Table</button>
                        </div>
                        <div class="schema-area">
                            <textarea rows="5" placeholder="Enter columns (one per line)">- id (int, primary key)
- username (varchar)
- email (varchar)
- created_at (timestamp)</textarea>
                        </div>
                    </div>
                </div>
                <button onclick="addNewTable()">Add New Table</button>
            </div>
            
            <h3>English Query:</h3>
            <textarea id="prompt" rows="3" placeholder="Enter your query in English"></textarea>
            
            <button onclick="generateSQL()">Generate SQL</button>
            
            <div class="result">
                <h3>SQL Query:</h3>
                <pre id="sql-result"></pre>
            </div>
        </div>

        <script>
        function addNewTable() {
            const tableContainer = document.createElement('div');
            tableContainer.className = 'table-container';
            tableContainer.innerHTML = `
                <div class="table-header">
                    <input type="text" placeholder="Table Name" style="padding: 5px;">
                    <button class="remove-btn" onclick="removeTable(this)">Remove Table</button>
                </div>
                <div class="schema-area">
                    <textarea rows="5" placeholder="Enter columns (one per line)"></textarea>
                </div>
            `;
            document.getElementById('table-list').appendChild(tableContainer);
        }

        function removeTable(button) {
            const tableContainer = button.closest('.table-container');
            if (document.getElementsByClassName('table-container').length > 1) {
                tableContainer.remove();
            } else {
                alert('You must have at least one table!');
            }
        }

        function collectSchemaData() {
            const tables = document.getElementsByClassName('table-container');
            let schema = '';
            
            for (let table of tables) {
                const tableName = table.querySelector('input').value.trim();
                const columns = table.querySelector('textarea').value.trim();
                
                if (tableName && columns) {
                    schema += `Table: ${tableName}\n${columns}\n\n`;
                }
            }
            return schema;
        }

        async function generateSQL() {
            const prompt = document.getElementById('prompt').value;
            const schema = collectSchemaData();
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ prompt, schema })
                });
                
                const data = await response.json();
                document.getElementById('sql-result').textContent = data.sql;
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('sql-result').textContent = 'Error generating SQL query';
            }
        }
        </script>
    </body>
    </html>
    ''')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        schema = data.get('schema', '')
        
        print("Received request:")
        print("Prompt:", prompt)
        print("Schema:", schema)
        
        sql = english_to_sql(prompt, schema)
        return jsonify({'sql': sql})
    except Exception as e:
        print(f"Error in generate endpoint: {str(e)}")
        return jsonify({'sql': f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)