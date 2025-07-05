from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import json
import traceback
from openai import AzureOpenAI
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
#from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore
import asyncio
import re

app = Flask(__name__)
app.secret_key = "7c0d2e2f35e020ec485f18271ca26451"

# Azure OpenAI Configuration
client = AzureOpenAI(
    api_key="99pNnIIEnYGr7klUx9lre5slwp1AJ2WvjJJrtQsAHlvTBpQF7vZBJQQJ99BFACHYHv6XJ3w3AAAAACOG6WvB",
    api_version="2024-06-01",
    azure_endpoint="https://deepi-mbm2wweg-eastus2.cognitiveservices.azure.com"
)
deployment_name = "gpt-4o"

# Database Configuration
DATABASE_PATH = "business_data.db"

# Initialize Semantic Kernel
kernel = sk.Kernel()

# Add Azure OpenAI service to kernel
kernel.add_service(AzureChatCompletion(
    deployment_name=deployment_name,
    endpoint="https://deepi-mbm2wweg-eastus2.cognitiveservices.azure.com",
    api_key="99pNnIIEnYGr7klUx9lre5slwp1AJ2WvjJJrtQsAHlvTBpQF7vZBJQQJ99BFACHYHv6XJ3w3AAAAACOG6WvB",
    api_version="2024-06-01"
))

class DatabaseAgent:
    def __init__(self, db_path):
        self.db_path = db_path
        self.schema_info = self.get_database_schema()
    
    def get_database_schema(self):
        """Get database schema information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema[table_name] = [{"name": col[1], "type": col[2]} for col in columns]
        
        conn.close()
        return schema
    
    def execute_query(self, query):
        """Execute SQL query safely"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Basic SQL injection protection
            if any(keyword in query.upper() for keyword in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']):
                return {"error": "Only SELECT queries are allowed"}
            
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            conn.close()
            
            return {
                "success": True,
                "data": results,
                "columns": columns,
                "row_count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

class AIQueryAgent:
    def __init__(self, db_agent):
        self.db_agent = db_agent
        self.client = client
    
    def generate_sql_query(self, user_question):
        """Generate SQL query from natural language"""
        schema_text = self.format_schema_for_prompt()
        
        prompt = f"""
        You are an expert SQL query generator. Given a natural language question, generate a precise SQL query.
        
        Database Schema:
        {schema_text}
        
        Important Rules:
        1. Only use SELECT statements
        2. Use proper table and column names from the schema
        3. Use appropriate JOINs when needed
        4. Include LIMIT clauses for large result sets
        5. Use proper date formatting and filtering
        6. Return only the SQL query, no explanations
        
        User Question: {user_question}
        
        SQL Query:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Clean up the response
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            return sql_query
        except Exception as e:
            return f"Error generating query: {str(e)}"
    
    def format_schema_for_prompt(self):
        """Format database schema for AI prompt"""
        schema_text = ""
        for table_name, columns in self.db_agent.schema_info.items():
            schema_text += f"\nTable: {table_name}\n"
            for col in columns:
                schema_text += f"  - {col['name']} ({col['type']})\n"
        return schema_text
    
    def generate_natural_response(self, user_question, sql_query, query_results):
        """Generate natural language response from query results"""
        if "error" in query_results:
            return f"I encountered an error: {query_results['error']}"
        
        # Format results for the prompt
        results_text = ""
        if query_results["data"]:
            results_text = f"Columns: {', '.join(query_results['columns'])}\n"
            results_text += f"Row count: {query_results['row_count']}\n"
            results_text += "Sample data:\n"
            for i, row in enumerate(query_results["data"][:5]):  # Show first 5 rows
                results_text += f"Row {i+1}: {row}\n"
        else:
            results_text = "No data found"
        
        prompt = f"""
        You are an AI data analyst. Provide a clear, natural language response to the user's question based on the SQL query results.
        
        User Question: {user_question}
        SQL Query Used: {sql_query}
        Query Results: {results_text}
        
        Provide a helpful, conversational response that:
        1. Directly answers the user's question
        2. Highlights key insights from the data
        3. Uses natural language, not technical jargon
        4. Mentions specific numbers and details when relevant
        
        Response:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"

# Initialize agents
db_agent = DatabaseAgent(DATABASE_PATH)
ai_agent = AIQueryAgent(db_agent)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({"error": "Please provide a question"})
        
        # Generate SQL query
        sql_query = ai_agent.generate_sql_query(user_question)
        
        if sql_query.startswith("Error"):
            return jsonify({"error": sql_query})
        
        # Execute query
        query_results = db_agent.execute_query(sql_query)
        
        # Generate natural language response
        natural_response = ai_agent.generate_natural_response(
            user_question, sql_query, query_results
        )
        
        return jsonify({
            "success": True,
            "question": user_question,
            "sql_query": sql_query,
            "response": natural_response,
            "data": query_results.get("data", [])[:10],  # Limit to 10 rows for display
            "columns": query_results.get("columns", []),
            "total_rows": query_results.get("row_count", 0)
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"})

@app.route('/api/schema')
def get_schema():
    """Get database schema information"""
    return jsonify(db_agent.schema_info)

@app.route('/api/suggestions')
def get_suggestions():
    """Get sample questions"""
    suggestions = [
        "List the top 10 best-selling products",
        "Show customers from the United States",
        "What are the total sales by category?",
        "Which employees have processed the most orders?",
        "Show products that are low in stock",
        "List orders from the last 30 days",
        "What are the most popular shipping companies?",
        "Show suppliers by country",
        "Which regions have the highest sales?",
        "List discontinued products"
    ]
    return jsonify(suggestions)

if __name__ == '__main__':
    print("🚀 Starting AI Agentic Web Application...")
    print("📊 Database:", DATABASE_PATH)
    print("🤖 AI Model:", deployment_name)
    print("🌐 Server: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
