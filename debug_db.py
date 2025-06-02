import sqlite3

def debug_db():
    try:
        # Connect to database
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
        schema = cursor.fetchone()
        print("Table Schema:")
        print(schema[0])
        print("\nSample Data:")
        
        # Get sample data
        cursor.execute("SELECT * FROM products LIMIT 1")
        columns = [description[0] for description in cursor.description]
        print("Columns:", columns)
        
        data = cursor.fetchone()
        print("Data:", data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_db() 