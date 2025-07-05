# 🤖 AI Agentic Web Application

A sophisticated full-stack AI-powered web application that understands natural language questions and intelligently queries structured data using Microsoft Semantic Kernel and Azure OpenAI.

## 🌟 Features

### 🧠 AI-Powered Intelligence
- **Natural Language Processing**: Ask questions in plain English
- **Semantic Kernel Integration**: Advanced AI reasoning and planning
- **Azure OpenAI GPT-4o**: State-of-the-art language model
- **Context-Aware Responses**: Maintains conversation context
- **Multi-Step Query Planning**: Handles complex analytical requests

### 📊 Database Capabilities
- **10 Relational Tables**: Comprehensive business dataset
- **Automated CSV Loading**: Downloads and processes data automatically
- **SQLite Performance**: Optimized with indexes for fast queries
- **Cross-Table Analysis**: AI can reason across multiple tables
- **Data Integrity**: Proper relationships and constraints

### 🎨 Futuristic UI/UX
- **Cyberpunk Theme**: Dark mode with neon accents
- **Terminal-Style Interface**: Professional hacker aesthetic
- **Real-Time Chat**: Smooth messaging experience
- **Animated Elements**: Glowing effects and smooth transitions
- **Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection (for CSV downloads)
- Modern web browser

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Setup the database**:
   \`\`\`bash
   python database_setup.py
   \`\`\`
   This will:
   - Download all 10 CSV files from the provided URLs
   - Create SQLite database with optimized tables
   - Set up indexes for better performance

4. **Start the application**:
   \`\`\`bash
   python app.py
   \`\`\`

5. **Open your browser** and navigate to:
   \`\`\`
   http://localhost:5000
   \`\`\`

## 📁 Project Structure

\`\`\`
ai-agentic-webapp/
├── app.py                 # Flask backend with AI logic
├── database_setup.py      # CSV download and database creation
├── templates/
│   └── index.html        # Single-file frontend
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── business_data.db      # SQLite database (created automatically)
\`\`\`

## 🗃️ Database Schema

The application automatically loads 10 CSV files into the following tables:

| Table | Description | Key Columns |
|-------|-------------|-------------|
| **customers** | Customer information | CustomerID, CompanyName, Country |
| **orders** | Order records | OrderID, CustomerID, OrderDate |
| **order_details** | Order line items | OrderID, ProductID, Quantity |
| **products** | Product catalog | ProductID, ProductName, UnitPrice |
| **categories** | Product categories | CategoryID, CategoryName |
| **suppliers** | Supplier information | SupplierID, CompanyName, Country |
| **employees** | Employee records | EmployeeID, FirstName, LastName |
| **shippers** | Shipping companies | ShipperID, CompanyName |
| **region** | Regional data | RegionID, RegionDescription |
| **employee_territory** | Employee territories | EmployeeID, TerritoryID |

## 💬 Example Queries

Try asking these natural language questions:

### 📈 Sales Analysis
- "Show me the top 10 best-selling products"
- "What are the total sales by category?"
- "Which customers have the highest order values?"
- "Show sales trends by month"

### 🌍 Geographic Analysis
- "List customers by country"
- "Which regions have the highest sales?"
- "Show suppliers from different countries"

### 👥 Employee Performance
- "Which employees have processed the most orders?"
- "Show employee sales performance"
- "List employees by region"

### 📦 Inventory Management
- "Show products that are low in stock"
- "List discontinued products"
- "Which products need reordering?"

### 🚚 Shipping Analysis
- "What are the most popular shipping companies?"
- "Show average shipping costs by region"
- "Which orders are still pending shipment?"

## 🔧 Configuration

### Azure OpenAI Settings

The application is pre-configured with Azure OpenAI credentials. If you need to update them, modify these values in `app.py`:

```python
client = AzureOpenAI(
    api_key="your-api-key-here",
    api_version="2024-06-01",
    azure_endpoint="your-endpoint-here"
)
deployment_name = "gpt-4o"
