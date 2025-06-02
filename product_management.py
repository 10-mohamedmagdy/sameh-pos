from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem, QDialog, QHeaderView, QHBoxLayout, QMenu, QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
import barcode  # تأكد من تثبيت مكتبة python-barcode
from barcode.writer import ImageWriter
import io
import os
import uuid
from database import db  # افتراض أن db هي حالة قاعدة البيانات


class ProductManagementWindow(QWidget):
    # تعريف إشارة الإغلاق
    closed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة المنتجات")
        self.setGeometry(150, 150, 800, 600)  # زيادة الحجم للرؤية الأفضل
        self.setStyleSheet("background-color: #f0f8ff;")  # خلفية زرقاء فاتحة
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.showMaximized()  # جعل النافذة مكبرة افتراضياً
        self.initUI()

    def create_table_item(self, text):
        """إنشاء عنصر جدول مع تنسيق موحد"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)  # محاذاة النص في المنتصف
        return item

    def initUI(self):
        layout = QVBoxLayout()
        
        # إنشاء وتطبيق خط العنوان
        title_font = QFont("Arial", 18, QFont.Bold)

        title = QLabel("🛠️ إدارة المنتجات", self)
        title.setFont(title_font)
        title.setStyleSheet("color: #0047ab; padding: 10px;")  # نص أزرق داكن
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # تنسيق الأزرار
        button_style = """
            QPushButton {
                background-color: #4682b4; 
                color: white; 
                border-radius: 8px; 
                padding: 10px; 
                font-size: 14px; 
                font-weight: bold;
                margin: 5px;
                min-width: 150px;
                min-height: 70px;
            }
            QPushButton:hover {
                background-color: #5f9ea0;
            }
            QPushButton:pressed {
                background-color: #3a5f77;
            }
        """

        # إنشاء تخطيط أفقي للأزرار لجعلها متجاورة
        buttons_layout = QHBoxLayout()
        
        # أزرار التحكم في نافذة إدارة المنتجات في صف واحد
        buttons = {
            "عرض جميع المنتجات": self.show_all_products,
            "إضافة منتج جديد": self.add_product,
            "تعديل منتج": self.edit_product,
            "حذف منتج": self.delete_product,
            "العودة للقائمة الرئيسية": self.close
        }

        for label, func in buttons.items():
            btn = QPushButton(label, self)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(func)
            buttons_layout.addWidget(btn)

        # إضافة تخطيط الأزرار إلى التخطيط الرئيسي
        layout.addLayout(buttons_layout)

        # إضافة جدول لعرض المنتجات مع التنسيق
        self.product_table = QTableWidget(self)
        self.product_table.setColumnCount(8)  # تقليل عدد الأعمدة بعد إزالة عمود المسلسل
        self.product_table.setHorizontalHeaderLabels([
            "الكود/الباركود", "الاسم", "سعر البيع", "سعر الشراء",
            "الكمية", "الوزن (كجم)", "نوع السعر", "الحد الأمن"
        ])
        
        # تنسيق الجدول
        self.product_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #d3d3d3;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #2c3e50;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #f0f8ff;
            }
        """)
        
        # ضبط عرض الأعمدة للتمدد
        header = self.product_table.horizontalHeader()
        for i in range(8):  # تحديث نطاق الأعمدة
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # إضافة خاصية القائمة السياقية (Context Menu) عند الضغط بزر الماوس الأيمن
        self.product_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.product_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # إضافة الجدول إلى التخطيط
        layout.addWidget(self.product_table)
        
        self.setLayout(layout)

    def show_context_menu(self, position):
        """عرض قائمة عند النقر بزر الماوس الأيمن"""
        # التحقق من وجود صف محدد
        row = self.product_table.rowAt(position.y())
        if row >= 0:
            # إنشاء قائمة منبثقة مع تنسيق محسن
            context_menu = QMenu(self)
            context_menu.setStyleSheet("""
                QMenu {
                    background-color: #f0f8ff;
                    border: 1px solid #4682b4;
                    border-radius: 4px;
                }
                QMenu::item {
                    padding: 8px 25px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: #b0d4f1;
                }
            """)
            
            # إضافة خيار لطباعة الباركود مع أيقونة
            print_barcode_action = context_menu.addAction("🏷️ طباعة الباركود")
            
            # عرض القائمة في موقع النقر
            action = context_menu.exec_(self.product_table.mapToGlobal(position))
            
            # إذا تم اختيار طباعة الباركود
            if action == print_barcode_action:
                # الحصول على كود المنتج واسمه من الصف المحدد
                product_code = self.product_table.item(row, 0).text()
                product_name = self.product_table.item(row, 1).text()
                
                # طباعة الباركود للمنتج المحدد
                self.show_barcode(product_code, product_name)

    def show_all_products(self):
        try:
            db.cursor.execute("""
                SELECT code, name, price, purchase_price, quantity, weight, sell_by, price_type, safe_limit 
                FROM products
            """)
            products = db.cursor.fetchall()

            # مسح بيانات الجدول الحالية
            self.product_table.setRowCount(0)

            # إدراج المنتجات في الجدول
            for row, product in enumerate(products):
                self.product_table.insertRow(row)
                code, name, price, purchase_price, quantity, weight, sell_by, price_type, safe_limit = product
                
                # إنشاء عناصر الجدول (بدون عمود المسلسل)
                self.product_table.setItem(row, 0, self.create_table_item(str(code)))     # الكود
                self.product_table.setItem(row, 1, self.create_table_item(str(name)))     # الاسم
                self.product_table.setItem(row, 2, self.create_table_item(f"{price:.2f}")) # سعر البيع
                self.product_table.setItem(row, 3, self.create_table_item(f"{purchase_price:.2f}")) # سعر الشراء
                
                # عرض الكمية و/أو الوزن حسب نوع البيع
                if sell_by == 'quantity':
                    self.product_table.setItem(row, 4, self.create_table_item(str(quantity)))
                    self.product_table.setItem(row, 5, self.create_table_item("-"))
                elif sell_by == 'weight':
                    self.product_table.setItem(row, 4, self.create_table_item("-"))
                    self.product_table.setItem(row, 5, self.create_table_item(f"{weight:.3f}"))
                else:  # both
                    self.product_table.setItem(row, 4, self.create_table_item(str(quantity)))
                    self.product_table.setItem(row, 5, self.create_table_item(f"{weight:.3f}"))
                    
                # عرض نوع السعر والحد الأمن
                self.product_table.setItem(row, 6, self.create_table_item(price_type))
                self.product_table.setItem(row, 7, self.create_table_item(str(safe_limit)))

                # تطبيق تنسيق خاص للأرقام
                for col in [2, 3, 4, 5, 7]:  # تحديث أرقام الأعمدة بعد إزالة عمود المسلسل
                    item = self.product_table.item(row, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
                        # تلوين الأسعار باللون الأخضر
                        if col in [2, 3]:
                            item.setForeground(Qt.darkGreen)

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء عرض المنتجات: {str(e)}")

    def add_product(self):
        try:
            # إنشاء باركود أولاً والذي سيكون نفسه كود المنتج
            barcode_dialog = QDialog(self)
            barcode_dialog.setWindowTitle("إنشاء باركود للمنتج الجديد")
            barcode_dialog.setStyleSheet("background-color: #f0f8ff;")
            barcode_layout = QVBoxLayout()
            
            info_label = QLabel("سيتم إنشاء باركود تلقائي للمنتج الجديد.\nهذا الباركود سيكون هو نفسه كود المنتج.")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #0047ab; padding: 10px; font-weight: bold;")
            barcode_layout.addWidget(info_label)
            
            # إنشاء زر لإنشاء باركود رقمي جديد
            button_layout = QHBoxLayout()
            
            numeric_btn = QPushButton("إنشاء باركود رقمي")
            numeric_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4682b4; 
                    color: white; 
                    border-radius: 8px; 
                    padding: 10px; 
                    font-size: 14px; 
                    font-weight: bold;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #5f9ea0;
                }
            """)
            
            alphanumeric_btn = QPushButton("إنشاء باركود حرفي")
            alphanumeric_btn.setStyleSheet(numeric_btn.styleSheet())
            
            custom_btn = QPushButton("إدخال باركود يدوياً")
            custom_btn.setStyleSheet(numeric_btn.styleSheet())
            
            button_layout.addWidget(numeric_btn)
            button_layout.addWidget(alphanumeric_btn)
            button_layout.addWidget(custom_btn)
            
            barcode_layout.addLayout(button_layout)
            barcode_dialog.setLayout(barcode_layout)
            
            # متغير لتخزين الباركود المنشأ
            generated_code = [""]  # استخدام قائمة لتتمكن من التعديل عليها داخل الدوال المتداخلة
            
            def generate_numeric_barcode():
                # إنشاء باركود رقمي بطول 12 رقم (للتوافق مع EAN-13)
                import random
                numeric_code = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                generated_code[0] = numeric_code
                barcode_dialog.accept()
                
            def generate_alphanumeric_barcode():
                # إنشاء باركود حرفي (لـ Code128)
                import random, string
                alphanumeric_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                generated_code[0] = alphanumeric_code
                barcode_dialog.accept()
                
            def enter_custom_barcode():
                code, ok = QInputDialog.getText(self, "إدخال باركود", "أدخل الباركود:")
                if ok and code:
                    # التحقق من عدم وجود المنتج بنفس الباركود
                    if code in [prod[0] for prod in db.get_all_products()]:
                        QMessageBox.warning(self, "خطأ", "هذا الباركود موجود بالفعل، الرجاء إدخال باركود آخر.")
                        return
                    generated_code[0] = code
                    barcode_dialog.accept()
            
            numeric_btn.clicked.connect(generate_numeric_barcode)
            alphanumeric_btn.clicked.connect(generate_alphanumeric_barcode)
            custom_btn.clicked.connect(enter_custom_barcode)
            
            # عرض نافذة إنشاء الباركود
            barcode_dialog.exec_()
            
            # إذا لم يتم إنشاء باركود، توقف العملية
            if not generated_code[0]:
                return
                
            # استخدام الباركود المنشأ كـ كود للمنتج
            code = generated_code[0]
            
            # إنشاء المنتج الجديد
            name, ok2 = QInputDialog.getText(self, "إضافة منتج", "اسم المنتج:")
            if not ok2:
                return

            price, ok3 = QInputDialog.getDouble(self, "إضافة منتج", "سعر البيع:", decimals=2)
            if not ok3:
                return

            # إضافة سؤال عن سعر الشراء
            purchase_price, ok4 = QInputDialog.getDouble(self, "إضافة منتج", "سعر الشراء:", decimals=2)
            if not ok4:
                return

            # إضافة سؤال عن نوع السعر
            price_type_dialog = QDialog(self)
            price_type_dialog.setWindowTitle("نوع السعر")
            price_type_dialog.setStyleSheet("background-color: #f0f8ff;")
            price_type_layout = QVBoxLayout()
            
            info_label = QLabel("هل السعر المدخل للكمية أم للوزن؟")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #0047ab; padding: 10px; font-weight: bold;")
            price_type_layout.addWidget(info_label)
            
            button_layout = QHBoxLayout()
            
            by_quantity_btn = QPushButton("السعر للكمية")
            by_quantity_btn.setStyleSheet(numeric_btn.styleSheet())
            
            by_weight_btn = QPushButton("السعر للوزن (كجم)")
            by_weight_btn.setStyleSheet(numeric_btn.styleSheet())
            
            button_layout.addWidget(by_quantity_btn)
            button_layout.addWidget(by_weight_btn)
            
            price_type_layout.addLayout(button_layout)
            price_type_dialog.setLayout(price_type_layout)
            
            price_info = [""]  # لتخزين معلومات السعر
            
            def set_quantity_price():
                price_info[0] = "السعر للقطعة"
                price_type_dialog.accept()
                
            def set_weight_price():
                price_info[0] = "السعر للكيلو"
                price_type_dialog.accept()
            
            by_quantity_btn.clicked.connect(set_quantity_price)
            by_weight_btn.clicked.connect(set_weight_price)
            
            price_type_dialog.exec_()
            
            if not price_info[0]:
                return

            # إضافة اختيار نوع البيع
            sell_type_dialog = QDialog(self)
            sell_type_dialog.setWindowTitle("نوع البيع")
            sell_type_dialog.setStyleSheet("background-color: #f0f8ff;")
            sell_type_layout = QVBoxLayout()
            
            info_label = QLabel("اختر طريقة بيع المنتج")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #0047ab; padding: 10px; font-weight: bold;")
            sell_type_layout.addWidget(info_label)
            
            button_layout = QHBoxLayout()
            
            by_quantity_btn = QPushButton("بيع بالكمية فقط")
            by_quantity_btn.setStyleSheet(numeric_btn.styleSheet())
            
            by_weight_btn = QPushButton("بيع بالوزن فقط")
            by_weight_btn.setStyleSheet(numeric_btn.styleSheet())

            by_both_btn = QPushButton("بيع بالكمية والوزن معاً")
            by_both_btn.setStyleSheet(numeric_btn.styleSheet())
            
            button_layout.addWidget(by_quantity_btn)
            button_layout.addWidget(by_weight_btn)
            button_layout.addWidget(by_both_btn)
            
            sell_type_layout.addLayout(button_layout)
            sell_type_dialog.setLayout(sell_type_layout)
            
            sell_type = [""]  # لتخزين نوع البيع
            
            def set_quantity_type():
                sell_type[0] = "quantity"
                sell_type_dialog.accept()
                
            def set_weight_type():
                sell_type[0] = "weight"
                sell_type_dialog.accept()
                
            def set_both_type():
                sell_type[0] = "both"
                sell_type_dialog.accept()
            
            by_quantity_btn.clicked.connect(set_quantity_type)
            by_weight_btn.clicked.connect(set_weight_type)
            by_both_btn.clicked.connect(set_both_type)
            
            sell_type_dialog.exec_()
            
            if not sell_type[0]:
                return

            quantity = 0
            weight = 0
            
            if sell_type[0] in ["quantity", "both"]:
                quantity, ok5 = QInputDialog.getInt(self, "إضافة منتج", "الكمية:")
                if not ok5:
                    return

            if sell_type[0] in ["weight", "both"]:
                weight_text, ok6 = QInputDialog.getText(self, "إضافة منتج", "الوزن (كجم):")
                if not ok6:
                    return
                try:
                    weight = float(weight_text.replace("كجم", "").strip())
                except ValueError:
                    QMessageBox.warning(self, "خطأ", "صيغة الوزن غير صحيحة")
                    return

            # إضافة الحد الأمن
            safe_limit, ok7 = QInputDialog.getInt(self, "إضافة منتج", "الحد الأمن للمنتج:", min=0)
            if not ok7:
                return

            # إضافة المنتج إلى قاعدة البيانات مع نوع البيع
            try:
                db.add_product(code, name, price, purchase_price, quantity, weight, sell_type[0], price_info[0], safe_limit)
                
                # عرض الباركود المنشأ للمنتج
                self.show_barcode(code, name)
                
                QMessageBox.information(self, "نجاح", "تمت إضافة المنتج بنجاح!")
                
                # تحديث الجدول لعرض المنتج الجديد
                self.show_all_products()
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إضافة المنتج: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

    def show_barcode(self, code, product_name):
        """عرض الباركود في نافذة منبثقة محسنة"""
        try:
            # تحديد نوع الباركود المناسب
            barcode_type = None
            product_code = code
            
            if product_code.isdigit():
                if len(product_code) <= 12:
                    barcode_type = barcode.get_barcode_class('ean13')
                    # إضافة أصفار إذا كان الطول أقل من 12 رقم
                    while len(product_code) < 12:
                        product_code = '0' + product_code
                else:
                    barcode_type = barcode.get_barcode_class('code128')
            else:
                barcode_type = barcode.get_barcode_class('code128')
            
            if barcode_type:
                # إنشاء الباركود
                filename = f"{product_name}_{product_code}"
                barcode_obj = barcode_type(product_code, writer=ImageWriter())
                barcode_path = barcode_obj.save(filename)
                
                # عرض الباركود في نافذة منبثقة محسنة
                barcode_dialog = QDialog(self)
                barcode_dialog.setWindowTitle("باركود المنتج")
                barcode_dialog.setGeometry(300, 300, 500, 450)  # تحسين حجم النافذة
                barcode_dialog.setStyleSheet("""
                    background-color: #f0f8ff;
                    border: 2px solid #4682b4;
                    border-radius: 10px;
                """)
                
                barcode_layout = QVBoxLayout()
                barcode_layout.setContentsMargins(20, 20, 20, 20)  # إضافة هوامش داخلية
                barcode_layout.setSpacing(15)  # زيادة المسافة بين العناصر
                
                # إضافة عنوان
                title_label = QLabel("باركود المنتج")
                title_label.setAlignment(Qt.AlignCenter)
                title_label.setStyleSheet("""
                    color: #0047ab;
                    font-size: 20px;
                    font-weight: bold;
                    padding: 10px;
                    border-bottom: 2px solid #4682b4;
                """)
                barcode_layout.addWidget(title_label)
                
                # إضافة معلومات المنتج
                info_label = QLabel(f"كود المنتج/الباركود: {code}\nاسم المنتج: {product_name}")
                info_label.setAlignment(Qt.AlignCenter)
                info_label.setStyleSheet("""
                    color: #0047ab;
                    font-size: 16px;
                    padding: 15px;
                    background-color: #e6f2ff;
                    border-radius: 8px;
                """)
                barcode_layout.addWidget(info_label)
                
                # إضافة صورة الباركود مع تحسين المظهر
                barcode_image = QLabel()
                barcode_pixmap = QPixmap(barcode_path)
                
                # تغيير حجم الصورة إذا كانت كبيرة جدًا
                if barcode_pixmap.width() > 400:
                    barcode_pixmap = barcode_pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                
                barcode_image.setPixmap(barcode_pixmap)
                barcode_image.setAlignment(Qt.AlignCenter)
                barcode_image.setStyleSheet("""
                    background-color: white;
                    padding: 20px;
                    border: 1px solid #d3d3d3;
                    border-radius: 5px;
                """)
                barcode_layout.addWidget(barcode_image)
                
                # إضافة زر للطباعة بتصميم محسن
                print_btn = QPushButton("🖨️ طباعة الباركود")
                print_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4682b4; 
                        color: white; 
                        border-radius: 8px; 
                        padding: 12px; 
                        font-size: 16px; 
                        font-weight: bold;
                        margin: 10px;
                    }
                    QPushButton:hover {
                        background-color: #5f9ea0;
                    }
                    QPushButton:pressed {
                        background-color: #3a5f77;
                    }
                """)
                
                def print_barcode_image():
                    # هنا يمكن إضافة كود الطباعة الفعلي
                    QMessageBox.information(barcode_dialog, "طباعة", f"جاري طباعة الباركود للمنتج {product_name}")
                    
                print_btn.clicked.connect(print_barcode_image)
                barcode_layout.addWidget(print_btn)
                
                # إضافة زر للإغلاق
                close_btn = QPushButton("إغلاق")
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #a9a9a9; 
                        color: white; 
                        border-radius: 8px; 
                        padding: 10px; 
                        font-size: 14px; 
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #808080;
                    }
                """)
                close_btn.clicked.connect(barcode_dialog.close)
                barcode_layout.addWidget(close_btn)
                
                barcode_dialog.setLayout(barcode_layout)
                barcode_dialog.exec_()
                
                return True
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء إنشاء الباركود: {str(e)}")
            return False

    def edit_product(self):
        code, ok = QInputDialog.getText(self, "تعديل منتج", "ادخل كود المنتج:")
        if ok and code:
            try:
                db.cursor.execute("""
                    SELECT code, name, price, quantity, weight, sell_by, price_type 
                    FROM products 
                    WHERE code = ?
                """, (code,))
                product = db.cursor.fetchone()
                
                if product:
                    name, ok1 = QInputDialog.getText(self, "تعديل اسم", "اسم المنتج:", text=product[1])
                    if not ok1:
                        return
                        
                    price, ok2 = QInputDialog.getDouble(self, "تعديل السعر", "سعر المنتج:", value=float(product[2]))
                    if not ok2:
                        return

                    # إضافة سؤال عن نوع السعر
                    price_type_dialog = QDialog(self)
                    price_type_dialog.setWindowTitle("نوع السعر")
                    price_type_dialog.setStyleSheet("background-color: #f0f8ff;")
                    price_type_layout = QVBoxLayout()
                    
                    info_label = QLabel("هل السعر المدخل للكمية أم للوزن؟")
                    info_label.setAlignment(Qt.AlignCenter)
                    info_label.setStyleSheet("color: #0047ab; padding: 10px; font-weight: bold;")
                    price_type_layout.addWidget(info_label)
                    
                    button_layout = QHBoxLayout()
                    
                    by_quantity_btn = QPushButton("السعر للكمية")
                    by_quantity_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4682b4; 
                            color: white; 
                            border-radius: 8px; 
                            padding: 10px; 
                            font-size: 14px; 
                            font-weight: bold;
                            margin: 5px;
                        }
                        QPushButton:hover {
                            background-color: #5f9ea0;
                        }
                    """)
                    
                    by_weight_btn = QPushButton("السعر للوزن (كجم)")
                    by_weight_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4682b4; 
                            color: white; 
                            border-radius: 8px; 
                            padding: 10px; 
                            font-size: 14px; 
                            font-weight: bold;
                            margin: 5px;
                        }
                        QPushButton:hover {
                            background-color: #5f9ea0;
                        }
                    """)
                    
                    button_layout.addWidget(by_quantity_btn)
                    button_layout.addWidget(by_weight_btn)
                    
                    price_type_layout.addLayout(button_layout)
                    price_type_dialog.setLayout(price_type_layout)
                    
                    price_info = [""]  # لتخزين معلومات السعر
                    
                    def set_quantity_price():
                        price_info[0] = "السعر للقطعة"
                        price_type_dialog.accept()
                        
                    def set_weight_price():
                        price_info[0] = "السعر للكيلو"
                        price_type_dialog.accept()
                    
                    by_quantity_btn.clicked.connect(set_quantity_price)
                    by_weight_btn.clicked.connect(set_weight_price)
                    
                    price_type_dialog.exec_()
                    
                    if not price_info[0]:
                        return

                    # إضافة اختيار نوع البيع
                    sell_type_dialog = QDialog(self)
                    sell_type_dialog.setWindowTitle("نوع البيع")
                    sell_type_dialog.setStyleSheet("background-color: #f0f8ff;")
                    sell_type_layout = QVBoxLayout()
                    
                    info_label = QLabel("اختر طريقة بيع المنتج")
                    info_label.setAlignment(Qt.AlignCenter)
                    info_label.setStyleSheet("color: #0047ab; padding: 10px; font-weight: bold;")
                    sell_type_layout.addWidget(info_label)
                    
                    button_layout = QHBoxLayout()
                    
                    by_quantity_btn = QPushButton("بيع بالكمية فقط")
                    by_quantity_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4682b4; 
                            color: white; 
                            border-radius: 8px; 
                            padding: 10px; 
                            font-size: 14px; 
                            font-weight: bold;
                            margin: 5px;
                        }
                        QPushButton:hover {
                            background-color: #5f9ea0;
                        }
                    """)
                    
                    by_weight_btn = QPushButton("بيع بالوزن فقط")
                    by_weight_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4682b4; 
                            color: white; 
                            border-radius: 8px; 
                            padding: 10px; 
                            font-size: 14px; 
                            font-weight: bold;
                            margin: 5px;
                        }
                        QPushButton:hover {
                            background-color: #5f9ea0;
                        }
                    """)

                    by_both_btn = QPushButton("بيع بالكمية والوزن معاً")
                    by_both_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4682b4; 
                            color: white; 
                            border-radius: 8px; 
                            padding: 10px; 
                            font-size: 14px; 
                            font-weight: bold;
                            margin: 5px;
                        }
                        QPushButton:hover {
                            background-color: #5f9ea0;
                        }
                    """)
                    
                    button_layout.addWidget(by_quantity_btn)
                    button_layout.addWidget(by_weight_btn)
                    button_layout.addWidget(by_both_btn)
                    
                    sell_type_layout.addLayout(button_layout)
                    sell_type_dialog.setLayout(sell_type_layout)
                    
                    sell_type = [product[5]]  # لتخزين نوع البيع، نستخدم النوع الحالي كقيمة افتراضية
                    
                    def set_quantity_type():
                        sell_type[0] = "quantity"
                        sell_type_dialog.accept()
                        
                    def set_weight_type():
                        sell_type[0] = "weight"
                        sell_type_dialog.accept()

                    def set_both_type():
                        sell_type[0] = "both"
                        sell_type_dialog.accept()
                    
                    by_quantity_btn.clicked.connect(set_quantity_type)
                    by_weight_btn.clicked.connect(set_weight_type)
                    by_both_btn.clicked.connect(set_both_type)
                    
                    sell_type_dialog.exec_()

                    quantity = 0
                    weight = 0
                    
                    if sell_type[0] in ["quantity", "both"]:
                        quantity, ok3 = QInputDialog.getInt(self, "تعديل الكمية", "الكمية:", value=int(product[3]) if product[3] else 0)
                        if not ok3:
                            return

                    if sell_type[0] in ["weight", "both"]:
                        weight_text, ok3 = QInputDialog.getText(self, "تعديل الوزن", "الوزن (كجم):", text=str(product[4]) if product[4] else "0")
                        if not ok3:
                            return
                        try:
                            weight = float(weight_text.replace("كجم", "").strip())
                        except ValueError:
                            QMessageBox.warning(self, "خطأ", "صيغة الوزن غير صحيحة")
                            return

                    # تحديث المنتج في قاعدة البيانات
                    db.cursor.execute("""
                        UPDATE products 
                        SET name = ?, price = ?, quantity = ?, weight = ?, sell_by = ?, price_type = ?
                        WHERE code = ?
                    """, (name, price, quantity, weight, sell_type[0], price_info[0], code))
                    db.conn.commit()
                    
                    QMessageBox.information(self, "نجاح", "تم تعديل المنتج بنجاح!")
                    self.show_all_products()
                else:
                    QMessageBox.warning(self, "خطأ", "كود المنتج غير موجود")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تعديل المنتج: {str(e)}")

    def delete_product(self):
        """حذف منتج"""
        code, ok = QInputDialog.getText(self, "حذف منتج", "ادخل كود المنتج:")
        if ok and code:
            try:
                # التحقق من وجود المنتج
                product = db.get_product(code)
                if not product:
                    QMessageBox.warning(self, "خطأ", "كود المنتج غير موجود.")
                    return

                # التحقق من استخدام المنتج في الفواتير
                product_used = False
                sales_info = None
                if db.check_product_usage(code):
                    product_used = True
                    # الحصول على معلومات المبيعات
                    sales_info = db.get_product_sales_info(code)

                # إظهار معلومات المنتج والاستخدام قبل التأكيد
                confirmation_msg = f"هل أنت متأكد من حذف المنتج: {product[1]}؟\n\n"
                
                if product_used and sales_info:
                    invoices_count, last_invoice, last_date = sales_info
                    confirmation_msg += f"""
                    هذا المنتج مستخدم في فواتير سابقة:
                    - عدد الفواتير: {invoices_count}
                    - آخر فاتورة: {last_invoice}
                    - تاريخ آخر بيع: {last_date}
                    
                    تنبيه: حذف هذا المنتج قد يؤثر على التقارير التاريخية.
                    """
                
                confirmation_msg += "\nلا يمكن التراجع عن هذه العملية!"

                # تأكيد الحذف
                confirm = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    confirmation_msg,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if confirm == QMessageBox.Yes:
                    db.cursor.execute("DELETE FROM products WHERE code = ?", (code,))
                    db.conn.commit()
                    QMessageBox.information(self, "تم", "تم حذف المنتج بنجاح.")
                    
                    # تحديث الجدول بعد الحذف
                    self.show_all_products()
                    
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف المنتج: {str(e)}")
                db.conn.rollback()

    def closeEvent(self, event):
        """التعامل مع حدث إغلاق النافذة"""
        self.closed_signal.emit()  # إرسال إشارة الإغلاق
        super().closeEvent(event)