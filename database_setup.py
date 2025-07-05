import sqlite3
import pandas as pd
import requests
from io import StringIO
import os

# Database configuration
DATABASE_PATH = "business_data.db"

# CSV file URLs and their corresponding table names
CSV_FILES = {
    "suppliers": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/suppliers-I8lmFbGJ9zwuVa6oIsUEEPuwvQPgKh.csv",
    "region": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/region-lhFJcpXUrJB3mFEqJjesKQTqmFm8Au.csv",
    "shippers": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/shippers-ngsXPYQhoeJYAymKGNdP4oh46kdOrz.csv",
    "products": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/products-4Mm12pB2wuM84QLZ8KhFGo94ChBav7.csv",
    "categories": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/categories-GQSrYmCeZrwZEQq6gepZ9Ero90hvuY.csv",
    "employees": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/employees-cE2BN5wGh4WtEBNixwTVvIXkzCl4el.csv",
    "order_details": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/order_details-2cQuu9tYvGpXfwhTwKgULXgaA9R2tQ.csv",
    "customers": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/customers-2JukdKBfh5MyNCF6LxtLhDA9gLx6vR.csv",
    "employee_territory": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/employee_territory-E6cVsJ7jko2qSEwbGBVSe6rwKwuNPm.csv",
    "orders": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/orders-9JtFjBCFyPWLxQbvjOJ6ihZ8aS2rMc.csv"
}

def download_csv(url):
    """Download CSV content from URL"""
    try:
        print(f"📥 Downloading: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return StringIO(response.text)
    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return None

def clean_column_names(df):
    """Clean column names to be SQL-friendly"""
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('-', '_')
    df.columns = df.columns.str.replace('(', '')
    df.columns = df.columns.str.replace(')', '')
    return df

def setup_database():
    """Download CSV files and create SQLite database"""
    print("🚀 Setting up database...")
    
    # Remove existing database
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print("🗑️  Removed existing database")
    
    # Create new database connection
    conn = sqlite3.connect(DATABASE_PATH)
    
    successful_tables = 0
    
    for table_name, url in CSV_FILES.items():
        try:
            print(f"\n📊 Processing table: {table_name}")
            
            # Download CSV
            csv_content = download_csv(url)
            if csv_content is None:
                continue
            
            # Read CSV into DataFrame
            df = pd.read_csv(csv_content)
            print(f"   📈 Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Clean column names
            df = clean_column_names(df)
            
            # Handle missing values
            df = df.fillna('')
            
            # Convert data types appropriately
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        # Try to convert to numeric if possible
                        pd.to_numeric(df[col], errors='raise')
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    except:
                        # Keep as string
                        df[col] = df[col].astype(str)
            
            # Save to SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"   ✅ Successfully created table: {table_name}")
            successful_tables += 1
            
            # Show sample data
            print(f"   📋 Sample data:")
            print(f"      Columns: {list(df.columns)}")
            if len(df) > 0:
                print(f"      First row: {df.iloc[0].to_dict()}")
            
        except Exception as e:
            print(f"   ❌ Error processing {table_name}: {str(e)}")
            continue
    
    # Create indexes for better performance
    print(f"\n🔧 Creating database indexes...")
    try:
        cursor = conn.cursor()
        
        # Create indexes on common foreign key columns
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(SupplierID)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(CategoryID)",
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(CustomerID)",
            "CREATE INDEX IF NOT EXISTS idx_orders_employee ON orders(EmployeeID)",
            "CREATE INDEX IF NOT EXISTS idx_order_details_order ON order_details(OrderID)",
            "CREATE INDEX IF NOT EXISTS idx_order_details_product ON order_details(ProductID)",
            "CREATE INDEX IF NOT EXISTS idx_employees_territory ON employee_territory(EmployeeID)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        print("   ✅ Indexes created successfully")
        
    except Exception as e:
        print(f"   ⚠️  Warning: Could not create some indexes: {str(e)}")
    
    # Display database summary
    print(f"\n📊 Database Summary:")
    print(f"   📁 Database file: {DATABASE_PATH}")
    print(f"   📋 Tables created: {successful_tables}/{len(CSV_FILES)}")
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    total_rows = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        total_rows += row_count
        print(f"   📊 {table_name}: {row_count} rows")
    
    print(f"   📈 Total rows: {total_rows}")
    
    conn.close()
    print(f"\n🎉 Database setup complete!")
    return successful_tables == len(CSV_FILES)

if __name__ == "__main__":
    print("🔧 AI Agentic Web App - Database Setup")
    print("=" * 50)
    
    success = setup_database()
    
    if success:
        print("\n✅ All CSV files loaded successfully!")
        print("🚀 You can now run: python app.py")
    else:
        print("\n⚠️  Some files failed to load. Check the errors above.")
        print("🔄 You can still run the app, but some queries might not work.")
