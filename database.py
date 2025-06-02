import sqlite3
import os
import shutil
from datetime import datetime
import sys

class Database:
    def __init__(self):
        try:
            # تحديد المسار المطلق لقاعدة البيانات
            if getattr(sys, 'frozen', False):
                # إذا كان التطبيق مجمع (exe)
                application_path = os.path.dirname(sys.executable)
            else:
                # إذا كان التطبيق يعمل من الكود المصدري
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            db_path = os.path.join(application_path, 'sales_inventory.db')
            backup_dir = os.path.join(application_path, 'backups')
            
            # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            print(f"محاولة الاتصال بقاعدة البيانات في المسار: {db_path}")
            
            # إنشاء نسخة احتياطية من قاعدة البيانات الحالية
            self.backup_database(db_path)
            
            # التحقق من وجود قاعدة البيانات
            if not os.path.exists(db_path):
                print("تحذير: لم يتم العثور على قاعدة البيانات. سيتم إنشاء قاعدة بيانات جديدة.")
            else:
                print("تم العثور على قاعدة البيانات.")
                db_size = os.path.getsize(db_path)
                print(f"حجم قاعدة البيانات: {db_size} بايت")
            
            # محاولة الاتصال بقاعدة البيانات
            print("محاولة الاتصال بقاعدة البيانات...")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            print("تم الاتصال بقاعدة البيانات بنجاح")
            
            # تفعيل دعم المفاتيح الخارجية
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # تعيين الترميز
            self.conn.execute("PRAGMA encoding = 'UTF-8'")
            
            # التحقق من الجداول الموجودة
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            print(f"الجداول الموجودة في قاعدة البيانات: {[table[0] for table in tables]}")
            
            self.create_tables()
            
        except sqlite3.Error as e:
            print(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
            print("يرجى التأكد من:")
            print("1. تثبيت SQLite على نظام التشغيل")
            print("2. وجود صلاحيات الكتابة في المجلد")
            print("3. عدم استخدام قاعدة البيانات من قبل برنامج آخر")
            print(f"المسار الحالي: {os.getcwd()}")
            print(f"مسار التطبيق: {application_path}")
            print(f"مسار قاعدة البيانات: {db_path}")
            if os.path.exists(db_path):
                print(f"صلاحيات المجلد: {oct(os.stat(os.path.dirname(db_path)).st_mode)[-3:]}")
            sys.exit(1)
        except Exception as e:
            print(f"خطأ غير متوقع: {str(e)}")
            print(f"نوع الخطأ: {type(e).__name__}")
            sys.exit(1)

    def backup_database(self, db_path):
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            if os.path.exists(db_path):
                # إنشاء مجلد للنسخ الاحتياطية إذا لم يكن موجوداً
                backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                # إنشاء اسم للنسخة الاحتياطية مع التاريخ والوقت
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(backup_dir, f'sales_inventory_{timestamp}.db')
                
                # نسخ قاعدة البيانات
                shutil.copy2(db_path, backup_path)
                print(f"تم إنشاء نسخة احتياطية في: {backup_path}")
                
                # الاحتفاظ فقط بآخر 5 نسخ احتياطية
                backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('sales_inventory_')])
                if len(backups) > 5:
                    for old_backup in backups[:-5]:
                        os.remove(os.path.join(backup_dir, old_backup))
                        print(f"تم حذف النسخة الاحتياطية القديمة: {old_backup}")
        except Exception as e:
            print(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")

    def restore_from_backup(self, backup_path=None):
        """استعادة قاعدة البيانات من نسخة احتياطية"""
        try:
            if not backup_path:
                # البحث عن أحدث نسخة احتياطية
                backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
                if not os.path.exists(backup_dir):
                    print("لم يتم العثور على مجلد النسخ الاحتياطية")
                    return False
                
                backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('sales_inventory_')])
                if not backups:
                    print("لم يتم العثور على نسخ احتياطية")
                    return False
                
                backup_path = os.path.join(backup_dir, backups[-1])
            
            # إغلاق الاتصال الحالي
            if self.conn:
                self.conn.close()
            
            # نسخ النسخة الاحتياطية إلى قاعدة البيانات الحالية
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sales_inventory.db')
            shutil.copy2(backup_path, db_path)
            
            # إعادة الاتصال بقاعدة البيانات
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            print(f"تم استعادة قاعدة البيانات من: {backup_path}")
            return True
            
        except Exception as e:
            print(f"خطأ في استعادة قاعدة البيانات: {str(e)}")
            return False

    def create_tables(self):
        """إنشاء الجداول إذا لم تكن موجودة"""
        # جدول المستخدمين
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            work_days TEXT,
            start_hour TEXT,
            end_hour TEXT
        )
        """)
        
        # جدول المنتجات
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            purchase_price REAL,
            quantity REAL DEFAULT 0,
            weight REAL DEFAULT 0,
            sell_by TEXT DEFAULT 'quantity',
            price_type TEXT DEFAULT 'unit',
            safe_limit REAL DEFAULT 0,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # جدول الفواتير
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            customer_id TEXT,
            cashier_username TEXT,
            total REAL NOT NULL,
            discount REAL DEFAULT 0,
            net_total REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cashier_username) REFERENCES users (username)
        )
        """)
        
        # جدول عناصر الفاتورة
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT NOT NULL,
            product_code TEXT NOT NULL,
            price REAL NOT NULL,
            quantity REAL,
            weight REAL,
            total_price REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id),
            FOREIGN KEY (product_code) REFERENCES products (code)
        )
        """)
        
        # جدول تسليم وتسلم الدرج
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_drawer_handovers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            delivered_by TEXT NOT NULL,
            received_by TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (delivered_by) REFERENCES users (username),
            FOREIGN KEY (received_by) REFERENCES users (username)
        )
        """)
        
        # جدول سجل الحضور والانصراف
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            check_in_time TEXT,
            check_out_time TEXT,
            status TEXT DEFAULT 'present',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users (username)
        )
        """)
        
        self.update_user_table_structure()
        
        # إضافة مستخدم admin افتراضي إذا لم يكن موجوداً
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            # إضافة مستخدم admin بكلمة مرور admin
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                               ('admin', 'admin', 'admin'))
            self.conn.commit()
            
        self.conn.commit()
        print("تم إنشاء الجداول بنجاح")
        return True

    def update_user_table_structure(self):
        """تحديث هيكل جدول المستخدمين وإضافة الأعمدة الجديدة إذا لم تكن موجودة"""
        try:
            # التحقق من وجود عمود work_days
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # إضافة عمود work_days إذا لم يكن موجوداً
            if 'work_days' not in columns:
                print("إضافة عمود work_days إلى جدول المستخدمين...")
                self.cursor.execute('''
                    ALTER TABLE users 
                    ADD COLUMN work_days TEXT DEFAULT 'السبت,الأحد,الإثنين,الثلاثاء,الأربعاء,الخميس'
                ''')
            
            # إضافة عمود start_hour إذا لم يكن موجوداً
            if 'start_hour' not in columns:
                print("إضافة عمود start_hour إلى جدول المستخدمين...")
                self.cursor.execute('''
                    ALTER TABLE users 
                    ADD COLUMN start_hour TEXT DEFAULT '08:00'
                ''')
            
            # إضافة عمود end_hour إذا لم يكن موجوداً
            if 'end_hour' not in columns:
                print("إضافة عمود end_hour إلى جدول المستخدمين...")
                self.cursor.execute('''
                    ALTER TABLE users 
                    ADD COLUMN end_hour TEXT DEFAULT '20:00'
                ''')
            
            self.conn.commit()
            print("تم تحديث هيكل جدول المستخدمين بنجاح")
            return True
        except Exception as e:
            print(f"خطأ في تحديث هيكل جدول المستخدمين: {str(e)}")
            self.conn.rollback()
            return False

    # Product operations
    def add_product(self, code, name, price, purchase_price, quantity, weight=0, sell_by='quantity', price_type='السعر للقطعة', safe_limit=0):
        """إضافة منتج جديد"""
        try:
            self.cursor.execute('''INSERT INTO products 
                               (code, name, price, purchase_price, quantity, weight, sell_by, price_type, safe_limit)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (code, name, price, purchase_price, quantity, weight, sell_by, price_type, safe_limit))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"خطأ في إضافة المنتج: {str(e)}")
            return False

    def get_product(self, code):
        """Get a product by its code"""
        try:
            self.cursor.execute("SELECT * FROM products WHERE code = ?", (code,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting product: {e}")
            return None

    def get_product_by_barcode(self, barcode):
        """Get a product using its barcode from scanner"""
        try:
            # First try exact match (primary method)
            self.cursor.execute("SELECT * FROM products WHERE code = ?", (barcode,))
            product = self.cursor.fetchone()
            
            # If product not found and barcode is numeric, try with leading zeros or without them
            if not product and barcode.isdigit():
                # Try adding leading zeros (some scanners might strip them)
                padded_code = barcode.zfill(13)  # EAN-13 standard length
                self.cursor.execute("SELECT * FROM products WHERE code = ?", (padded_code,))
                product = self.cursor.fetchone()
                
                # If still not found, try removing leading zeros
                if not product:
                    stripped_code = barcode.lstrip('0')
                    self.cursor.execute("SELECT * FROM products WHERE code = ?", (stripped_code,))
                    product = self.cursor.fetchone()
            
            return product
        except Exception as e:
            print(f"Error getting product by barcode: {e}")
            return None

    def get_all_products(self):
        """Get all products ordered by name"""
        try:
            self.cursor.execute("SELECT * FROM products ORDER BY name")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []

    def update_product(self, code, name, price, purchase_price, quantity, weight=None, sell_by=None, price_type=None, safe_limit=None):
        """تحديث بيانات منتج"""
        try:
            # جمع البيانات الحالية للمنتج
            self.cursor.execute("SELECT * FROM products WHERE code = ?", (code,))
            current_data = self.cursor.fetchone()
            
            if not current_data:
                return False
                
            # استخدام القيم الحالية إذا لم يتم تحديد قيم جديدة
            weight = weight if weight is not None else current_data[4]
            sell_by = sell_by if sell_by is not None else current_data[5]
            price_type = price_type if price_type is not None else current_data[6]
            safe_limit = safe_limit if safe_limit is not None else current_data[7]
            
            self.cursor.execute('''UPDATE products 
                               SET name = ?, price = ?, purchase_price = ?, quantity = ?, 
                                   weight = ?, sell_by = ?, price_type = ?, safe_limit = ?
                               WHERE code = ?''',
                              (name, price, purchase_price, quantity, weight, sell_by, price_type, safe_limit, code))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"خطأ في تحديث المنتج: {str(e)}")
            return False

    def update_product_quantity(self, code, quantity_change):
        """Update product quantity with change value (positive or negative)"""
        try:
            # First check current quantity
            product = self.get_product(code)
            if not product:
                print(f"Product with code {code} not found")
                return False
                
            current_qty = product[3]
            new_qty = current_qty + quantity_change
            
            if new_qty < 0:
                print(f"Cannot update quantity below 0 for product {code}")
                return False
                
            self.cursor.execute("UPDATE products SET quantity = ? WHERE code = ?",
                              (new_qty, code))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating product quantity: {e}")
            self.conn.rollback()
            return False

    # Invoice operations
    def save_invoice(self, invoice_id, date, customer_id, total, discount, net_total, items, cashier_username=None):
        """Save invoice and update product quantities in a transaction"""
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
            # Save invoice
            self.cursor.execute('''INSERT INTO invoices 
                                (invoice_id, date, customer_id, cashier_username, total, discount, net_total)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                              (invoice_id, date, customer_id, cashier_username, total, discount, net_total))
            
            # Save invoice items and update quantities
            for item in items:
                # Get weight value if exists, otherwise use 0
                weight = item.get('weight', 0)
                
                # Save invoice item
                self.cursor.execute('''INSERT INTO invoice_items 
                                    (invoice_id, product_code, product_name, price, quantity, weight, total_price)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                  (invoice_id, item['code'], item['name'], 
                                   item['price'], item['quantity'], weight, item['total_price']))
                
                # Update product quantity
                if not self.update_product_quantity(item['code'], -item['quantity']):
                    raise Exception(f"Failed to update quantity for product {item['code']}")
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving invoice: {e}")
            self.conn.rollback()
            return False

    def get_invoices_by_date(self, date):
        """Get invoices for a specific date"""
        try:
            # Fix: Use more flexible date matching
            query = '''SELECT * FROM invoices 
                    WHERE date LIKE ?
                    ORDER BY date DESC'''
            date_pattern = f"{date}%"  # This will match the date part regardless of time
            self.cursor.execute(query, (date_pattern,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting invoices by date: {e}")
            return []
            
    def get_invoices_by_date_range(self, start_date, end_date):
        """Get invoices between two dates with profit information"""
        try:
            print(f"Fetching invoices from DB between {start_date} and {end_date}")
            
            # أولاً نحسب إجمالي المبيعات والربح للفترة المحددة
            total_query = """
                SELECT 
                    COALESCE(SUM(i.net_total), 0) as total_sales,
                    COALESCE(SUM(
                        CASE 
                            WHEN p.purchase_price > 0 
                            THEN (ii.total_price - (p.purchase_price * ii.quantity))
                            ELSE 0 
                        END
                    ), 0) as total_profit
                FROM invoices i
                LEFT JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
                LEFT JOIN products p ON ii.product_code = p.code
                WHERE date(substr(i.date, 1, 10)) BETWEEN date(?) AND date(?)
            """
            
            self.cursor.execute(total_query, (start_date, end_date))
            total_result = self.cursor.fetchone()
            total_sales, total_profit = total_result if total_result else (0, 0)
            print(f"Total sales: {total_sales}, Total profit: {total_profit}")
            
            # ثم نجلب تفاصيل الفواتير
            invoice_query = """
                SELECT 
                    i.invoice_id,
                    i.date,
                    i.customer_id,
                    i.cashier_username,
                    i.total,
                    i.discount,
                    i.net_total,
                    COALESCE(SUM(
                        CASE 
                            WHEN p.purchase_price > 0 
                            THEN (ii.total_price - (p.purchase_price * ii.quantity))
                            ELSE 0 
                        END
                    ), 0) as invoice_profit
                FROM invoices i
                LEFT JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
                LEFT JOIN products p ON ii.product_code = p.code
                WHERE date(substr(i.date, 1, 10)) BETWEEN date(?) AND date(?)
                GROUP BY i.invoice_id, i.date, i.customer_id, i.cashier_username, i.total, i.discount, i.net_total
                ORDER BY i.date DESC
            """
            
            self.cursor.execute(invoice_query, (start_date, end_date))
            invoices = self.cursor.fetchall()
            
            # نضيف إجمالي المبيعات والربح إلى النتيجة
            result = {
                'total_sales': total_sales,
                'total_profit': total_profit,
                'invoices': invoices
            }
            
            print(f"Found {len(invoices)} invoices with total sales: {total_sales} and total profit: {total_profit}")
            return result
            
        except Exception as e:
            print(f"Error getting invoices by date range: {e}")
            return {'total_sales': 0, 'total_profit': 0, 'invoices': []}

    def get_invoice_items(self, invoice_id):
        """Get all items for a specific invoice"""
        try:
            self.cursor.execute('''SELECT product_name, price, quantity, weight, total_price 
                                FROM invoice_items 
                                WHERE invoice_id = ?''', (invoice_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting invoice items: {e}")
            return []

    def get_daily_sales(self, date):
        """Get sales details for a specific date with profit information"""
        try:
            query = '''
                SELECT 
                    i.invoice_id,
                    i.date,
                    p.name,
                    ii.quantity,
                    ii.weight,
                    ii.price,
                    ii.total_price,
                    (ii.total_price - (p.purchase_price * ii.quantity)) as profit
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.invoice_id
                JOIN products p ON ii.product_code = p.code
                WHERE i.date LIKE ?
                ORDER BY i.date DESC
            '''
            date_pattern = f"{date}%"
            self.cursor.execute(query, (date_pattern,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting daily sales: {e}")
            return []

    def get_top_products(self, start_date, end_date, min_quantity=50, min_weight=100, min_sales=500):
        """الحصول على المنتجات الأكثر مبيعاً مع تطبيق معايير التصفية"""
        try:
            query = """
                WITH sales_data AS (
                    SELECT 
                        p.code as product_code,
                        p.name,
                        p.sell_by,
                        COALESCE(SUM(ii.quantity), 0) as quantity_sold,
                        COALESCE(SUM(ii.weight), 0) as weight_sold,
                        COALESCE(SUM(ii.total_price), 0) as total_sales,
                        COALESCE(SUM(
                            CASE 
                                WHEN p.purchase_price > 0 
                                THEN (ii.total_price - (p.purchase_price * ii.quantity))
                                ELSE 0 
                            END
                        ), 0) as total_profit
                    FROM products p
                    LEFT JOIN invoice_items ii ON p.code = ii.product_code
                    LEFT JOIN invoices i ON ii.invoice_id = i.invoice_id 
                        AND date(substr(i.date, 1, 10)) BETWEEN date(?) AND date(?)
                    GROUP BY p.code, p.name, p.sell_by
                )
                SELECT *
                FROM sales_data
                WHERE 
                    (sell_by = 'quantity' AND quantity_sold >= ?) OR
                    (sell_by = 'weight' AND weight_sold >= ?) OR
                    total_sales >= ?
                ORDER BY total_sales DESC
            """
            
            self.cursor.execute(query, (start_date, end_date, min_quantity, min_weight, min_sales))
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"Error in get_top_products: {str(e)}")
            return []

    def get_low_selling_products(self, start_date, end_date, min_quantity=20, min_weight=500, min_sales=500):
        """الحصول على المنتجات الأقل مبيعاً حسب الشروط الجديدة"""
        try:
            query = """
                WITH sales_data AS (
                    SELECT 
                        p.code as product_code,
                        p.name,
                        p.sell_by,
                        COALESCE(SUM(ii.quantity), 0) as quantity_sold,
                        COALESCE(SUM(ii.weight), 0) as weight_sold,
                        COALESCE(SUM(ii.total_price), 0) as total_sales,
                        COALESCE(SUM(
                            CASE 
                                WHEN p.purchase_price > 0 
                                THEN (ii.total_price - (p.purchase_price * ii.quantity))
                                ELSE 0 
                            END
                        ), 0) as total_profit,
                        COUNT(DISTINCT i.invoice_id) as sales_count
                    FROM products p
                    LEFT JOIN invoice_items ii ON p.code = ii.product_code
                    LEFT JOIN invoices i ON ii.invoice_id = i.invoice_id 
                        AND date(substr(i.date, 1, 10)) BETWEEN date(?) AND date(?)
                    GROUP BY p.code, p.name, p.sell_by
                )
                SELECT product_code, name, sell_by, quantity_sold, weight_sold, total_sales, total_profit, sales_count
                FROM sales_data
                WHERE 
                    (
                        (sell_by = 'quantity' AND quantity_sold < ?) OR
                        (sell_by = 'weight' AND weight_sold < ?) OR
                        total_sales < ?
                    )
                ORDER BY total_sales ASC
            """
            self.cursor.execute(query, (start_date, end_date, min_quantity, min_weight, min_sales))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error in get_low_selling_products: {str(e)}")
            return []

    def get_low_stock_products(self, threshold=5):
        """Get products with low stock"""
        try:
            self.cursor.execute('''SELECT * FROM products 
                                WHERE quantity <= ?
                                ORDER BY quantity ASC''', (threshold,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting low stock products: {e}")
            return []
            
    # Scanner configuration methods
    def save_scanner_config(self, device_path, vendor_id=None, product_id=None):
        """Save or update scanner configuration"""
        try:
            now = datetime.now().isoformat()
            # Check if device already exists
            self.cursor.execute("SELECT id FROM scanner_config WHERE device_path = ?", (device_path,))
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing configuration
                self.cursor.execute('''UPDATE scanner_config 
                                    SET is_active = 1, last_used = ?,
                                    vendor_id = COALESCE(?, vendor_id),
                                    product_id = COALESCE(?, product_id)
                                    WHERE device_path = ?''', 
                                  (now, vendor_id, product_id, device_path))
            else:
                # Create new configuration
                self.cursor.execute('''INSERT INTO scanner_config 
                                    (device_path, vendor_id, product_id, last_used)
                                    VALUES (?, ?, ?, ?)''', 
                                  (device_path, vendor_id, product_id, now))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving scanner configuration: {e}")
            self.conn.rollback()
            return False
    
    def get_active_scanner(self):
        """Get the active scanner configuration"""
        try:
            self.cursor.execute('''SELECT device_path, vendor_id, product_id
                                FROM scanner_config 
                                WHERE is_active = 1
                                ORDER BY last_used DESC
                                LIMIT 1''')
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting active scanner: {e}")
            return None
    
    def get_all_scanners(self):
        """Get all configured scanners"""
        try:
            self.cursor.execute('''SELECT device_path, vendor_id, product_id, is_active, last_used
                                FROM scanner_config
                                ORDER BY last_used DESC''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all scanners: {e}")
            return []

    # New methods for report window functionality
    def get_popular_products(self, start_date, end_date, limit=50):
        """Get most sold products within a date range"""
        try:
            query = """
                SELECT ii.product_code, p.name, SUM(ii.quantity) as total_sold, 
                       COUNT(DISTINCT ii.invoice_id) as sales_count,
                       AVG(ii.quantity) as avg_quantity_per_sale,
                       p.weight
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.invoice_id
                JOIN products p ON ii.product_code = p.code
                WHERE substr(i.date, 1, 10) >= ? AND substr(i.date, 1, 10) <= ?
                GROUP BY ii.product_code
                ORDER BY total_sold DESC
                LIMIT ?
            """
            self.cursor.execute(query, (start_date, end_date, limit))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting popular products: {e}")
            return []

    def get_low_demand_products(self, start_date, end_date, threshold=5, limit=50):
        """Get products with low demand within a date range with profit information"""
        try:
            query = """
                SELECT 
                    p.code, 
                    p.name,
                    COALESCE(SUM(ii.quantity), 0) as total_sold,
                    COUNT(DISTINCT ii.invoice_id) as sales_count,
                    MAX(i.date) as last_sale_date,
                    p.weight,
                    COALESCE(SUM(ii.total_price), 0) as total_sales,
                    COALESCE(SUM(ii.total_price - (p.purchase_price * ii.quantity)), 0) as total_profit
                FROM products p
                LEFT JOIN invoice_items ii ON p.code = ii.product_code
                LEFT JOIN invoices i ON ii.invoice_id = i.invoice_id AND substr(i.date, 1, 10) >= ? AND substr(i.date, 1, 10) <= ?
                GROUP BY p.code
                HAVING total_sold < ? OR total_sold IS NULL
                ORDER BY total_sold ASC, last_sale_date ASC
                LIMIT ?
            """
            self.cursor.execute(query, (start_date, end_date, threshold, limit))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting low demand products: {e}")
            return []

    def check_database_status(self):
        """التحقق من حالة قاعدة البيانات"""
        try:
            print("\n=== حالة قاعدة البيانات ===")
            
            # التحقق من الاتصال
            if not self.conn:
                print("❌ لا يوجد اتصال بقاعدة البيانات")
                return False
                
            # التحقق من الجداول
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            print(f"✅ عدد الجداول: {len(tables)}")
            print(f"📋 الجداول: {[table[0] for table in tables]}")
            
            # التحقق من جدول المنتجات
            try:
                self.cursor.execute("SELECT COUNT(*) FROM products")
                product_count = self.cursor.fetchone()[0]
                print(f"✅ عدد المنتجات: {product_count}")
            except sqlite3.OperationalError:
                print("❌ جدول المنتجات غير موجود")
            
            # التحقق من جدول الفواتير
            try:
                self.cursor.execute("SELECT COUNT(*) FROM invoices")
                invoice_count = self.cursor.fetchone()[0]
                print(f"✅ عدد الفواتير: {invoice_count}")
            except sqlite3.OperationalError:
                print("❌ جدول الفواتير غير موجود")
            
            # التحقق من الترميز
            self.cursor.execute("PRAGMA encoding")
            encoding = self.cursor.fetchone()[0]
            print(f"✅ ترميز قاعدة البيانات: {encoding}")
            
            # التحقق من المفاتيح الخارجية
            self.cursor.execute("PRAGMA foreign_keys")
            foreign_keys = self.cursor.fetchone()[0]
            print(f"✅ دعم المفاتيح الخارجية: {'مفعل' if foreign_keys else 'معطل'}")
            
            print("========================\n")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في التحقق من حالة قاعدة البيانات: {str(e)}")
            return False

    def close(self):
        """Close the database connection"""
        try:
            if self.conn:
                self.conn.close()
                print("تم إغلاق الاتصال بقاعدة البيانات")
        except Exception as e:
            print(f"خطأ في إغلاق قاعدة البيانات: {e}")

    def check_product_safety(self, code):
        """التحقق من مستوى المخزون مقارنة بالحد الأمن"""
        try:
            self.cursor.execute('''SELECT quantity, safe_limit, name 
                               FROM products 
                               WHERE code = ?''', (code,))
            result = self.cursor.fetchone()
            
            if result:
                quantity, safe_limit, name = result
                if quantity <= safe_limit:
                    return {
                        'is_safe': False,
                        'current_quantity': quantity,
                        'safe_limit': safe_limit,
                        'name': name
                    }
            return {'is_safe': True}
        except Exception as e:
            print(f"خطأ في التحقق من الحد الأمن: {str(e)}")
            return {'is_safe': True}  # نفترض أنه آمن في حالة الخطأ

    def get_user(self, username):
        """الحصول على بيانات المستخدم"""
        try:
            self.cursor.execute("SELECT username, role, created_at FROM users WHERE username = ?",
                              (username,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"خطأ في الحصول على بيانات المستخدم: {str(e)}")
            return None

    def get_user_with_schedule(self, username):
        """الحصول على بيانات المستخدم مع جدول العمل"""
        try:
            self.cursor.execute("SELECT username, role, created_at, work_days, start_hour, end_hour FROM users WHERE username = ?",
                              (username,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"خطأ في الحصول على بيانات المستخدم: {str(e)}")
            return None

    def get_user_schedule(self, username):
        """الحصول على جدول عمل المستخدم"""
        try:
            self.cursor.execute("SELECT start_hour, end_hour FROM users WHERE username = ?", (username,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"خطأ في الحصول على جدول عمل المستخدم: {str(e)}")
            return None

    def add_user(self, username, password, role):
        """إضافة مستخدم جديد"""
        try:
            # التحقق من وجود المستخدم
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            user_exists = self.cursor.fetchone()[0]
            
            if user_exists:
                return False
                
            # إضافة المستخدم
            self.cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, password, role))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المستخدم: {str(e)}")
            return False

    def add_user_with_schedule(self, username, password, role, work_days, start_hour, end_hour):
        """إضافة مستخدم جديد مع جدول العمل"""
        try:
            # التحقق من وجود المستخدم
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            user_exists = self.cursor.fetchone()[0]
            
            if user_exists:
                return False
                
            # إضافة المستخدم
            self.cursor.execute("""
                INSERT INTO users (username, password, role, work_days, start_hour, end_hour)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password, role, work_days, start_hour, end_hour))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المستخدم: {str(e)}")
            return False

    def update_user(self, username, password, role, work_days, start_hour, end_hour):
        """تحديث بيانات مستخدم مع تغيير كلمة المرور"""
        try:
            # التحقق من وجود المستخدم
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            user_exists = self.cursor.fetchone()[0]
            
            if not user_exists:
                return False
                
            # تحديث بيانات المستخدم مع كلمة المرور
            self.cursor.execute("""
                UPDATE users SET 
                    password = ?, 
                    role = ?, 
                    work_days = ?, 
                    start_hour = ?, 
                    end_hour = ?
                WHERE username = ?
            """, (password, role, work_days, start_hour, end_hour, username))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في تحديث بيانات المستخدم: {str(e)}")
            self.conn.rollback()
            return False

    def update_user_without_password(self, username, role, work_days, start_hour, end_hour):
        """تحديث بيانات مستخدم بدون تغيير كلمة المرور"""
        try:
            # التحقق من وجود المستخدم
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            user_exists = self.cursor.fetchone()[0]
            
            if not user_exists:
                return False
                
            # تحديث بيانات المستخدم بدون كلمة المرور
            self.cursor.execute("""
                UPDATE users SET 
                    role = ?, 
                    work_days = ?, 
                    start_hour = ?, 
                    end_hour = ?
                WHERE username = ?
            """, (role, work_days, start_hour, end_hour, username))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في تحديث بيانات المستخدم: {str(e)}")
            self.conn.rollback()
            return False

    def delete_user(self, username):
        """حذف مستخدم"""
        try:
            # لا يمكن حذف المستخدم admin
            if username == 'admin':
                return False
                
            # حذف المستخدم
            self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في حذف المستخدم: {str(e)}")
            return False

    def get_all_users(self):
        """الحصول على قائمة المستخدمين"""
        self.cursor.execute("""
            SELECT username, role, created_at, work_days, start_hour, end_hour
            FROM users
            ORDER BY CASE 
                WHEN username = 'admin' THEN 0 
                ELSE 1 
            END, username
        """)
        return self.cursor.fetchall()

    def check_product_usage(self, code):
        """التحقق مما إذا كان المنتج مستخدماً في أي فواتير"""
        try:
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM invoice_items 
                WHERE product_code = ?
            """, (code,))
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"خطأ في التحقق من استخدام المنتج: {str(e)}")
            return True  # نفترض أنه مستخدم في حالة الخطأ للأمان

    def get_product_sales_info(self, code):
        """الحصول على معلومات مبيعات المنتج"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT invoice_id) as invoices_count,
                    MAX(invoice_id) as last_invoice,
                    MAX(substr(invoice_id, 1, 10)) as last_date
                FROM invoice_items 
                WHERE product_code = ?
            """, (code,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"خطأ في الحصول على معلومات المبيعات: {str(e)}")
            return None

    def save_cash_drawer_handover(self, delivered_by, received_by, amount, notes=""):
        """تسجيل عملية تسليم وتسلم الدرج (الكاش)"""
        try:
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")
            
            self.cursor.execute('''
                INSERT INTO cash_drawer_handovers 
                (date, time, delivered_by, received_by, amount, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (current_date, current_time, delivered_by, received_by, amount, notes))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"خطأ في تسجيل عملية تسليم الدرج: {str(e)}")
            self.conn.rollback()
            return False
            
    def get_cash_drawer_handovers(self, start_date=None, end_date=None):
        """الحصول على سجل عمليات تسليم وتسلم الدرج"""
        try:
            query = '''
                SELECT 
                    id, date, time, 
                    delivered_by, received_by, amount, notes 
                FROM cash_drawer_handovers
            '''
            
            params = []
            if start_date and end_date:
                query += " WHERE date BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            query += " ORDER BY date DESC, time DESC"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"خطأ في استرجاع سجل تسليم الدرج: {str(e)}")
            return []

    def record_attendance(self, username, check_type):
        """تسجيل الحضور أو الانصراف للمستخدم
        check_type: 'in' للحضور، 'out' للانصراف
        """
        try:
            # التحقق من وجود المستخدم
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if self.cursor.fetchone()[0] == 0:
                return False, "المستخدم غير موجود"
            
            current_date = self.get_current_date()
            current_time = self.get_current_time()
            
            if check_type == 'in':
                # التحقق من عدم وجود تسجيل حضور لنفس اليوم
                self.cursor.execute("""
                SELECT COUNT(*) FROM attendance_log 
                WHERE username = ? AND date = ? AND check_in_time IS NOT NULL
                """, (username, current_date))
                
                if self.cursor.fetchone()[0] > 0:
                    return False, "تم تسجيل الحضور مسبقاً اليوم"
                
                # تسجيل الحضور
                self.cursor.execute("""
                INSERT INTO attendance_log (username, date, check_in_time)
                VALUES (?, ?, ?)
                """, (username, current_date, current_time))
                
                self.conn.commit()
                return True, f"تم تسجيل حضورك بنجاح في {current_time}"
                
            elif check_type == 'out':
                # البحث عن سجل حضور لنفس اليوم
                self.cursor.execute("""
                SELECT id FROM attendance_log 
                WHERE username = ? AND date = ? AND check_in_time IS NOT NULL
                ORDER BY id DESC LIMIT 1
                """, (username, current_date))
                
                result = self.cursor.fetchone()
                if not result:
                    return False, "لم يتم تسجيل الحضور اليوم"
                
                log_id = result[0]
                
                # التحقق من عدم وجود تسجيل انصراف لنفس السجل
                self.cursor.execute("""
                SELECT check_out_time FROM attendance_log 
                WHERE id = ?
                """, (log_id,))
                
                if self.cursor.fetchone()[0] is not None:
                    return False, "تم تسجيل الانصراف مسبقاً اليوم"
                
                # تسجيل الانصراف
                self.cursor.execute("""
                UPDATE attendance_log 
                SET check_out_time = ?
                WHERE id = ?
                """, (current_time, log_id))
                
                self.conn.commit()
                return True, f"تم تسجيل انصرافك بنجاح في {current_time}"
                
            return False, "نوع التسجيل غير صحيح"
            
        except Exception as e:
            print(f"Error in record_attendance: {str(e)}")
            self.conn.rollback()
            return False, f"حدث خطأ: {str(e)}"
            
    def get_attendance_report(self, start_date=None, end_date=None, username=None):
        """الحصول على تقرير الحضور والانصراف"""
        try:
            query = """
            SELECT a.id, a.username, a.date, a.check_in_time, a.check_out_time, 
                   a.status, a.notes, u.role
            FROM attendance_log a
            JOIN users u ON a.username = u.username
            WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND a.date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND a.date <= ?"
                params.append(end_date)
                
            if username:
                query += " AND a.username = ?"
                params.append(username)
                
            query += " ORDER BY a.date DESC, a.username"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"Error in get_attendance_report: {str(e)}")
            return []
            
    def get_current_date(self):
        """الحصول على التاريخ الحالي بتنسيق YYYY-MM-DD"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
        
    def get_current_time(self):
        """الحصول على الوقت الحالي بتنسيق HH:MM:SS"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

# Global database instance
db = Database()
# التحقق من حالة قاعدة البيانات عند بدء التشغيل
db.check_database_status()