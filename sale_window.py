from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QTableWidget, QTableWidgetItem, QInputDialog, 
                            QFileDialog, QMessageBox, QComboBox, QGroupBox, QRadioButton,
                            QCheckBox, QSpinBox, QDoubleSpinBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo
from PyQt5.QtGui import QTextDocument, QImage, QPixmap, QFocusEvent, QPainter, QFont
from datetime import datetime
from database import db
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from escpos.printer import Usb

class ExternalScannerInput(QLineEdit):
    """مربع نص معدل لاستقبال مدخلات من الماسح الخارجي"""
    scanComplete = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("مرر منتجًا على الماسح الضوئي أو أدخل الكود يدويًا...")
        self.returnPressed.connect(self.on_return_pressed)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                background-color: #f0f8ff;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #2ecc71;
            }
        """)
        self.last_scanned = ""
        self.scan_timer = QTimer()
        self.scan_timer.setInterval(100)  # 100ms delay between scans
        self.scan_timer.timeout.connect(self.reset_last_scanned)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """مراقبة أحداث المكون للتأكد من التركيز"""
        if obj == self and event.type() == QEvent.MouseButtonPress:
            self.setFocus()
        return super().eventFilter(obj, event)
    
    def on_return_pressed(self):
        """تنفذ عند الضغط على Enter (معظم الماسحات ترسل Enter تلقائياً بعد المسح)"""
        scanned_text = self.text().strip()
        if scanned_text and scanned_text != self.last_scanned:
            self.last_scanned = scanned_text
            print(f"تم مسح الكود: {scanned_text}")
            self.scanComplete.emit(scanned_text)
            self.scan_timer.start()
            self.clear()
    
    def reset_last_scanned(self):
        """إعادة تعيين آخر مسح ضوئي للسماح بمسح نفس الكود مرة أخرى"""
        self.scan_timer.stop()
        self.last_scanned = ""

class SalesWindow(QWidget):
    # تعريف إشارة الإغلاق
    closed_signal = pyqtSignal()

    def __init__(self, username="مستخدم"):
        super().__init__()
        self.setWindowTitle("🧾 عملية البيع")
        self.setGeometry(150, 150, 800, 700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.showMaximized()  # جعل النافذة مكبرة افتراضياً
        self.cart = []
        self.total = 0.0
        self.discount = 0.0
        self.net_total = 0.0
        self.username = username
        
        # تهيئة الطابعة
        self.setup_printer()
        
        self.initUI()
        QTimer.singleShot(500, self.ensure_scanner_focus)

    def setup_printer(self):
        """تهيئة الطابعة الحرارية"""
        try:
            # تعطيل مؤقت للطابعة الحرارية
            self.thermal_printer = None
            
            # إعداد طابعة النظام العادية
            self.system_printer = QPrinter()
            
            # الحصول على قائمة الطابعات المتاحة
            available_printers = [printer.printerName() for printer in QPrinterInfo.availablePrinters()]
            print(f"الطابعات المتاحة: {available_printers}")
            
            if "XPK200L" in available_printers:
                self.system_printer.setPrinterName("XPK200L")
                print("تم العثور على طابعة XPK200L")
            else:
                # استخدام أول طابعة متاحة
                if available_printers:
                    self.system_printer.setPrinterName(available_printers[0])
                    print(f"تم اختيار الطابعة: {available_printers[0]}")
                else:
                    print("لم يتم العثور على أي طابعة")
            
            self.system_printer.setPageSize(QPrinter.A5)
            self.system_printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)
            self.system_printer.setResolution(300)
            self.system_printer.setOutputFormat(QPrinter.NativeFormat)
            self.system_printer.setColorMode(QPrinter.GrayScale)
            print("تم إعداد طابعة النظام بنجاح")
            
        except Exception as e:
            print(f"خطأ في إعداد الطابعة: {str(e)}")
            self.thermal_printer = None
            self.system_printer = None
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Store title
        title = QLabel("منفذ الشهداء")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Invoice info
        self.invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        invoice_layout = QVBoxLayout()
        
        # إنشاء إطار للمعلومات
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        # إضافة معلومات الفاتورة
        invoice_label = QLabel(f"رقم الفاتورة: {self.invoice_id}")
        date_label = QLabel(f"التاريخ: {self.date}")
        cashier_label = QLabel(f"اسم الكاشير: {self.username}")
        
        # تنسيق خاص للكاشير
        cashier_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                border-bottom: 1px solid #bdc3c7;
            }
        """)
        
        info_layout.addWidget(invoice_label)
        info_layout.addWidget(date_label)
        info_layout.addWidget(cashier_label)
        
        invoice_layout.addWidget(info_frame)
        layout.addLayout(invoice_layout)

        # Membership input
        self.member_input = QLineEdit()
        self.member_input.setPlaceholderText("رقم العضوية (اختياري)")
        layout.addWidget(self.member_input)

        # Scanner section
        scanner_group = QGroupBox("إدخال الباركود")
        scanner_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scanner_layout = QVBoxLayout()
        
        self.external_scanner_input = ExternalScannerInput()
        self.external_scanner_input.scanComplete.connect(self.process_external_scan)
        scanner_layout.addWidget(self.external_scanner_input)
        
        scanner_group.setLayout(scanner_layout)
        layout.addWidget(scanner_group)

        # Control buttons
        btn_layout = QHBoxLayout()
        buttons = [
            ("🔍 بحث عن منتج", self.search_product, "#2ecc71"),
            ("✅ إتمام البيع", self.complete_sale, "#27ae60"),
            ("🗑️ مسح السلة", self.clear_cart, "#e74c3c")
        ]

        for text, handler, color in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                    min-width: 120px;
                }}
                QPushButton:hover {{
                    background-color: #34495e;
                }}
            """)
            btn.clicked.connect(handler)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # Products table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(7)  # زيادة عدد الأعمدة
        self.product_table.setHorizontalHeaderLabels(["م", "المنتج", "الكود", "السعر", "الكمية", "الوزن (كجم)", "الإجمالي"])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.product_table)

        # Invoice summary
        summary_layout = QVBoxLayout()
        self.total_label = QLabel("المجموع: 0.00 ج")
        self.discount_label = QLabel("الخصم: 0.00 ج")
        self.net_label = QLabel("الصافي: 0.00 ج")
        self.net_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c;")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.discount_label)
        summary_layout.addWidget(self.net_label)
        layout.addLayout(summary_layout)

        # Print button
        print_btn = QPushButton("🖨️ طباعة الفاتورة")
        print_btn.clicked.connect(self.print_invoice)
        layout.addWidget(print_btn)

        self.setLayout(layout)
    
    def ensure_scanner_focus(self):
        self.external_scanner_input.setFocus()
        print("تم إعادة تركيز الماسح الضوئي")

    def process_external_scan(self, code):
        """معالجة مسح الكود - نسخة مبسطة"""
        if not code:
            return
            
        try:
            # 1. جلب المنتج بشكل محدد
            db.cursor.execute("""
                SELECT 
                    code,
                    name,
                    price,
                    quantity,
                    weight,
                    sell_by,
                    safe_limit
                FROM products 
                WHERE code = ?
            """, (code,))
            
            product = db.cursor.fetchone()
            if not product:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على المنتج")
                return
                
            # 2. تحويل البيانات الأساسية
            code = str(product[0])
            name = str(product[1])
            price = float(product[2])
            current_quantity = int(product[3]) if product[3] is not None else 0
            current_weight = float(product[4]) if product[4] is not None and isinstance(product[4], (int, float, str)) else 0
            sell_by = str(product[5]) if product[5] is not None else 'quantity'
            safe_limit = int(product[6]) if product[6] is not None else 0
            
            # 3. حساب السعر الإجمالي
            total = 0
            quantity = None
            weight = None
            
            # 4. طلب الكمية أو الوزن
            if sell_by == 'quantity':
                # التحقق من وجود كمية متاحة للبيع
                if current_quantity <= 0:
                    QMessageBox.warning(self, "خطأ", "لا توجد كمية متاحة من هذا المنتج في المخزون!")
                    return
                    
                qty, ok = QInputDialog.getInt(
                    self, 
                    "الكمية", 
                    f"المخزون المتاح: {current_quantity}\nالحد الأمن: {safe_limit}\nأدخل الكمية المطلوبة:", 
                    1, 1, current_quantity
                )
                if not ok:
                    return
                    
                # التحقق من الحد الأمن
                remaining_quantity = current_quantity - qty
                if remaining_quantity <= safe_limit:
                    warning_msg = f"تنبيه: المخزون سيصل إلى {remaining_quantity} وهو "
                    if remaining_quantity == safe_limit:
                        warning_msg += f"يساوي الحد الأمن ({safe_limit})"
                    elif remaining_quantity < safe_limit:
                        warning_msg += f"أقل من الحد الأمن ({safe_limit})"
                    
                    reply = QMessageBox.warning(
                        self,
                        "تحذير المخزون",
                        f"{warning_msg}\n\nهل تريد الاستمرار في عملية البيع؟",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.No:
                        return
                
                quantity = qty
                total = price * qty
                
            elif sell_by == 'weight':
                # التحقق من وجود وزن متاح للبيع
                if current_weight <= 0:
                    QMessageBox.warning(self, "خطأ", "لا يوجد وزن متاح من هذا المنتج في المخزون!")
                    return
                    
                w, ok = QInputDialog.getDouble(
                    self, 
                    "الوزن", 
                    f"الوزن المتاح: {current_weight:.3f} كجم\nالحد الأمن: {safe_limit:.3f} كجم\nأدخل الوزن المطلوب بالكيلوجرام:", 
                    0.1, 0.001, current_weight, 3
                )
                if not ok:
                    return
                    
                # التحقق من الحد الأمن للوزن
                remaining_weight = current_weight - w
                if remaining_weight <= safe_limit:
                    warning_msg = f"تنبيه: المخزون سيصل إلى {remaining_weight:.3f} كجم وهو "
                    if remaining_weight == safe_limit:
                        warning_msg += f"يساوي الحد الأمن ({safe_limit:.3f} كجم)"
                    elif remaining_weight < safe_limit:
                        warning_msg += f"أقل من الحد الأمن ({safe_limit:.3f} كجم)"
                    
                    reply = QMessageBox.warning(
                        self,
                        "تحذير المخزون",
                        f"{warning_msg}\n\nهل تريد الاستمرار في عملية البيع؟",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    
                    if reply == QMessageBox.No:
                        return
                
                weight = w
                total = price * w
                
            else:  # both
                # التحقق من وجود كمية أو وزن متاح للبيع
                if current_quantity <= 0 and current_weight <= 0:
                    QMessageBox.warning(self, "خطأ", "لا توجد كمية أو وزن متاح من هذا المنتج في المخزون!")
                    return
                
                # تحديد خيارات البيع المتاحة بناءً على المخزون
                available_options = []
                if current_quantity > 0:
                    available_options.append("بالقطعة")
                if current_weight > 0:
                    available_options.append("بالوزن")
                
                if len(available_options) == 1:
                    # إذا كان هناك خيار واحد فقط متاح
                    choice = 0 if available_options[0] == "بالقطعة" else 1
                else:
                    # السماح للمستخدم باختيار طريقة البيع
                    options = "|".join(available_options)
                    choice = QMessageBox.question(
                        self,
                        "اختيار طريقة البيع",
                        "كيف تريد بيع هذا المنتج؟",
                        options, 0, 1
                    )
                
                if (choice == 0 and "بالقطعة" in available_options) or (available_options[0] == "بالقطعة" and len(available_options) == 1):  # بالقطعة
                    qty, ok = QInputDialog.getInt(
                        self, 
                        "الكمية", 
                        f"المخزون المتاح: {current_quantity}\nالحد الأمن: {safe_limit}\nأدخل الكمية المطلوبة:", 
                        1, 1, current_quantity
                    )
                    if not ok:
                        return
                    
                    # التحقق من الحد الأمن
                    remaining_quantity = current_quantity - qty
                    if remaining_quantity <= safe_limit:
                        warning_msg = f"تنبيه: المخزون سيصل إلى {remaining_quantity} وهو "
                        if remaining_quantity == safe_limit:
                            warning_msg += f"يساوي الحد الأمن ({safe_limit})"
                        elif remaining_quantity < safe_limit:
                            warning_msg += f"أقل من الحد الأمن ({safe_limit})"
                        
                        reply = QMessageBox.warning(
                            self,
                            "تحذير المخزون",
                            f"{warning_msg}\n\nهل تريد الاستمرار في عملية البيع؟",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if reply == QMessageBox.No:
                            return
                    
                    quantity = qty
                    total = price * qty
                else:  # بالوزن
                    w, ok = QInputDialog.getDouble(
                        self, 
                        "الوزن", 
                        f"الوزن المتاح: {current_weight:.3f} كجم\nالحد الأمن: {safe_limit:.3f} كجم\nأدخل الوزن المطلوب بالكيلوجرام:", 
                        0.1, 0.001, current_weight, 3
                    )
                    if not ok:
                        return
                        
                    # التحقق من الحد الأمن للوزن
                    remaining_weight = current_weight - w
                    if remaining_weight <= safe_limit:
                        warning_msg = f"تنبيه: المخزون سيصل إلى {remaining_weight:.3f} كجم وهو "
                        if remaining_weight == safe_limit:
                            warning_msg += f"يساوي الحد الأمن ({safe_limit:.3f} كجم)"
                        elif remaining_weight < safe_limit:
                            warning_msg += f"أقل من الحد الأمن ({safe_limit:.3f} كجم)"
                        
                        reply = QMessageBox.warning(
                            self,
                            "تحذير المخزون",
                            f"{warning_msg}\n\nهل تريد الاستمرار في عملية البيع؟",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        
                        if reply == QMessageBox.No:
                            return
                    
                    weight = w
                    total = price * w
            
            # 5. إضافة للسلة
            item = {
                'code': code,
                'name': name,
                'price': price,
                'quantity': quantity,
                'weight': weight,
                'sell_by': sell_by,
                'total_price': total
            }
        
            print(f"إضافة منتج للسلة: {item}")  # للتأكد من البيانات
            self.cart.append(item)
            self.update_cart_display()
            QMessageBox.information(self, "تم", "تمت إضافة المنتج بنجاح")
            
        except Exception as e:
            print(f"خطأ: {str(e)}")
            print(f"نوع الخطأ: {type(e)}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
            
        finally:
            self.external_scanner_input.clear()
            self.external_scanner_input.setFocus()

    def search_product(self):
        """البحث عن منتج وإضافته للسلة"""
        try:
            name, ok = QInputDialog.getText(self, "بحث عن منتج", "أدخل اسم المنتج:")
            if ok and name:
                products = db.get_all_products()
                matched = [p for p in products if name.lower() in p[1].lower()]
                
                if not matched:
                    QMessageBox.warning(self, "تحذير", "لا يوجد منتج بهذا الاسم!")
                    return
                    
                if len(matched) == 1:
                    self.process_external_scan(matched[0][0])  # استخدام نفس دالة المسح الضوئي
                else:
                    # تحسين عرض المنتجات المتطابقة ليشمل المخزون المتاح
                    items = [f"{p[1]} (كود: {p[0]}) - المخزون المتاح: {p[3]}" for p in matched]
                    item, ok = QInputDialog.getItem(self, "اختر منتج", "المنتجات المتطابقة:", items, 0, False)
                    if ok and item:
                        code = item.split("كود: ")[1].split(")")[0]
                        self.process_external_scan(code)  # استخدام نفس دالة المسح الضوئي
                        
        except Exception as e:
            print(f"خطأ في البحث عن منتج: {str(e)}")
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء البحث عن المنتج: {str(e)}")

    def add_product_to_cart(self, code, quantity=None):
        try:
            # البحث عن المنتج في قاعدة البيانات
            db.cursor.execute("""
                SELECT name, price, quantity, weight, sell_by, price_type, safe_limit 
                FROM products WHERE code = ?
            """, (code,))
            product = db.cursor.fetchone()
            
            if not product:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على المنتج!")
                return
                
            name, price, current_quantity, weight, sell_by, price_type, safe_limit = product
            
            # التحقق من طريقة البيع
            if sell_by == 'quantity':
                # التحقق من وجود كمية متاحة للبيع
                if current_quantity <= 0:
                    QMessageBox.warning(self, "خطأ", "لا توجد كمية متاحة من هذا المنتج في المخزون!")
                    return
                    
                if quantity is None:
                    quantity, ok = QInputDialog.getInt(self, "إدخال الكمية", "أدخل الكمية المطلوبة:", 1, 1)
                    if not ok:
                        return
                        
                if quantity > current_quantity:
                    QMessageBox.warning(self, "خطأ", "الكمية المطلوبة غير متوفرة في المخزون!")
                    return
                    
                # التحقق من الحد الأمن
                remaining_quantity = current_quantity - quantity
                if remaining_quantity <= safe_limit:
                    warning_msg = f"تنبيه: الكمية المتبقية ({remaining_quantity}) وصلت إلى أو أقل من الحد الأمن ({safe_limit})"
                    if remaining_quantity == 0:
                        warning_msg += "\nلا يمكن بيع المزيد من هذا المنتج!"
                    response = QMessageBox.warning(self, "تحذير المخزون", 
                                                warning_msg + "\n\nهل تريد المتابعة؟",
                                                QMessageBox.Yes | QMessageBox.No)
                    if response == QMessageBox.No:
                        return
                
                total_price = price * quantity
                
                # إضافة المنتج إلى السلة
                self.cart.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'quantity': quantity,
                    'weight': 0,
                    'total': total_price
                })
                
            elif sell_by == 'weight':
                # التحقق من وجود وزن متاح للبيع
                if weight <= 0:
                    QMessageBox.warning(self, "خطأ", "لا يوجد وزن متاح من هذا المنتج في المخزون!")
                    return
                    
                weight_input, ok = QInputDialog.getDouble(self, "إدخال الوزن", 
                                                        "أدخل الوزن المطلوب (كجم):", 0.1, 0.001, 1000, 3)
                if not ok:
                    return
                    
                if weight_input > weight:
                    QMessageBox.warning(self, "خطأ", "الوزن المطلوب غير متوفر في المخزون!")
                    return
                    
                # التحقق من الحد الأمن للوزن
                remaining_weight = weight - weight_input
                if remaining_weight <= safe_limit:
                    warning_msg = f"تنبيه: الوزن المتبقي ({remaining_weight:.3f} كجم) وصل إلى أو أقل من الحد الأمن ({safe_limit} كجم)"
                    if remaining_weight == 0:
                        warning_msg += "\nلا يمكن بيع المزيد من هذا المنتج!"
                    response = QMessageBox.warning(self, "تحذير المخزون", 
                                                warning_msg + "\n\nهل تريد المتابعة؟",
                                                QMessageBox.Yes | QMessageBox.No)
                    if response == QMessageBox.No:
                        return
                
                total_price = price * weight_input
                
                # إضافة المنتج إلى السلة
                self.cart.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'quantity': 0,
                    'weight': weight_input,
                    'total': total_price
                })
                
            else:  # both
                # التحقق من وجود كمية أو وزن متاح للبيع
                if current_quantity <= 0 and weight <= 0:
                    QMessageBox.warning(self, "خطأ", "لا توجد كمية أو وزن متاح من هذا المنتج في المخزون!")
                    return
                
                # تحديد خيارات البيع المتاحة بناءً على المخزون
                available_options = []
                if current_quantity > 0:
                    available_options.append("بالقطعة")
                if weight > 0:
                    available_options.append("بالوزن")
                
                if len(available_options) == 1:
                    # إذا كان هناك خيار واحد فقط متاح
                    choice = 0 if available_options[0] == "بالقطعة" else 1
                else:
                    # السماح للمستخدم باختيار طريقة البيع
                    options = "|".join(available_options)
                    choice = QMessageBox.question(self, "اختيار طريقة البيع",
                                               "كيف تريد بيع هذا المنتج؟",
                                               options, 0, 1)
                
                if (choice == 0 and "بالقطعة" in available_options) or (available_options[0] == "بالقطعة" and len(available_options) == 1):  # بالقطعة
                    quantity, ok = QInputDialog.getInt(self, "إدخال الكمية", "أدخل الكمية المطلوبة:", 1, 1)
                    if not ok:
                        return
                        
                    if quantity > current_quantity:
                        QMessageBox.warning(self, "خطأ", "الكمية المطلوبة غير متوفرة في المخزون!")
                        return
                        
                    # التحقق من الحد الأمن
                    remaining_quantity = current_quantity - quantity
                    if remaining_quantity <= safe_limit:
                        warning_msg = f"تنبيه: الكمية المتبقية ({remaining_quantity}) وصلت إلى أو أقل من الحد الأمن ({safe_limit})"
                        if remaining_quantity == 0:
                            warning_msg += "\nلا يمكن بيع المزيد من هذا المنتج!"
                        response = QMessageBox.warning(self, "تحذير المخزون", 
                                                    warning_msg + "\n\nهل تريد المتابعة؟",
                                                    QMessageBox.Yes | QMessageBox.No)
                        if response == QMessageBox.No:
                            return
                    
                    total_price = price * quantity
                    
                    self.cart.append({
                        'code': code,
                        'name': name,
                        'price': price,
                        'quantity': quantity,
                        'weight': 0,
                        'total': total_price
                    })
                    
                else:  # بالوزن
                    weight_input, ok = QInputDialog.getDouble(self, "إدخال الوزن", 
                                                            "أدخل الوزن المطلوب (كجم):", 0.1, 0.001, 1000, 3)
                    if not ok:
                        return
                        
                    if weight_input > weight:
                        QMessageBox.warning(self, "خطأ", "الوزن المطلوب غير متوفر في المخزون!")
                        return
                        
                    # التحقق من الحد الأمن للوزن
                    remaining_weight = weight - weight_input
                    if remaining_weight <= safe_limit:
                        warning_msg = f"تنبيه: الوزن المتبقي ({remaining_weight:.3f} كجم) وصل إلى أو أقل من الحد الأمن ({safe_limit} كجم)"
                        if remaining_weight == 0:
                            warning_msg += "\nلا يمكن بيع المزيد من هذا المنتج!"
                        response = QMessageBox.warning(self, "تحذير المخزون", 
                                                    warning_msg + "\n\nهل تريد المتابعة؟",
                                                    QMessageBox.Yes | QMessageBox.No)
                        if response == QMessageBox.No:
                            return
                    
                    total_price = price * weight_input
                    
                    self.cart.append({
                        'code': code,
                        'name': name,
                        'price': price,
                        'quantity': 0,
                        'weight': weight_input,
                        'total': total_price
                    })
            
            # تحديث عرض السلة والمجموع
            self.update_cart_display()
            self.calculate_totals()
            
            # تنظيف حقل الإدخال وإعادة التركيز
            self.external_scanner_input.clear()
            self.external_scanner_input.setFocus()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إضافة المنتج: {str(e)}")

    def update_cart_display(self):
        """تحديث عرض السلة"""
        try:
            self.product_table.setRowCount(0)
            
            for idx, item in enumerate(self.cart, 1):
                row = self.product_table.rowCount()
                self.product_table.insertRow(row)
                
                # تحضير القيم للعرض
                quantity_display = str(item.get('quantity', '-'))
                weight_display = f"{item.get('weight', 0):.3f}" if item.get('weight') is not None else "-"
                total_price = item.get('total_price', 0)
                
                items = [
                    QTableWidgetItem(str(idx)),
                    QTableWidgetItem(item.get('name', '')),
                    QTableWidgetItem(item.get('code', '')),
                    QTableWidgetItem(f"{item.get('price', 0):.2f} ج"),
                    QTableWidgetItem(quantity_display),
                    QTableWidgetItem(weight_display),
                    QTableWidgetItem(f"{total_price:.2f} ج")
                ]
                
                for i, table_item in enumerate(items):
                    table_item.setTextAlignment(Qt.AlignCenter)
                    self.product_table.setItem(row, i, table_item)
            
            self.calculate_totals()
            
        except Exception as e:
            print(f"خطأ في تحديث عرض السلة: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def calculate_totals(self):
        """حساب المجاميع"""
        try:
            self.total = sum(item.get('total_price', 0) for item in self.cart)
            self.discount = self.total * 0.0  # يمكن تعديل نسبة الخصم هنا
            self.net_total = self.total - self.discount
            
            self.total_label.setText(f"المجموع: {self.total:.2f} ج")
            self.discount_label.setText(f"الخصم: {self.discount:.2f} ج (0%)")
            self.net_label.setText(f"الصافي: {self.net_total:.2f} ج")
        except Exception as e:
            print(f"خطأ في حساب المجاميع: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def clear_cart(self):
        self.cart = []
        self.update_cart_display()
        QMessageBox.information(self, "تم", "تم مسح السلة بنجاح")
        self.external_scanner_input.setFocus()

    def complete_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "تنبيه", "لا يوجد منتجات في السلة")
            return
            
        reply = QMessageBox.question(
            self,
            "تأكيد البيع",
            f"هل تريد إتمام عملية البيع؟\nالمبلغ الإجمالي: {self.net_total:.2f} جنيهاً",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db.conn.execute("BEGIN TRANSACTION")
                
                db.cursor.execute('''INSERT INTO invoices 
                                  (invoice_id, date, customer_id, cashier_username, total, discount, net_total)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (self.invoice_id, self.date, 
                                 self.member_input.text() or None,
                                 self.username,  # Add cashier username
                                 self.total, self.discount, self.net_total))

                for item in self.cart:
                    db.cursor.execute('''INSERT INTO invoice_items 
                                      (invoice_id, product_code, product_name, price, quantity, weight, total_price)
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (self.invoice_id, item['code'], item['name'], 
                                     item['price'], item['quantity'], item.get('weight', 0), item['total_price']))
                    
                    if item['quantity'] is not None:
                        db.cursor.execute("UPDATE products SET quantity = quantity - ? WHERE code = ?",
                                        (item['quantity'], item['code']))
                
                db.conn.commit()
                
                QMessageBox.information(
                    self, 
                    "تمت العملية بنجاح", 
                    f"تم إتمام عملية البيع بنجاح\nرقم الفاتورة: {self.invoice_id}\nالمبلغ الإجمالي: {self.net_total:.2f} جنيهاً"
                )
                
                # طباعة الفاتورة تلقائيًا بعد إتمام البيع
                self.print_invoice(direct_print=True)
                
                self.clear_cart()
                self.invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            except Exception as e:
                db.conn.rollback()
                QMessageBox.critical(
                    self, 
                    "فشل في إتمام العملية", 
                    f"حدث خطأ أثناء محاولة إتمام البيع:\n{str(e)}\n\nتم التراجع عن جميع التغييرات"
                )

    def print_invoice(self, direct_print=False):
        """دالة طباعة الفاتورة مع دعم الطابعة الحرارية والعادية"""
        if not self.cart:
            QMessageBox.warning(self, "تحذير", "لا توجد فاتورة للطباعة!")
            return
        
        try:
            # محاولة الطباعة على الطابعة الحرارية أولاً
            if self.print_thermal_invoice():
                if direct_print:
                    QMessageBox.information(self, "تم", "تم طباعة الفاتورة بنجاح على الطابعة الحرارية")
                else:
                    QMessageBox.information(self, "تم", "تم إرسال الفاتورة للطابعة الحرارية بنجاح")
                return
                
            # إذا فشلت الطباعة الحرارية، نستخدم الطابعة العادية
            doc = QTextDocument()
            doc.setHtml(self.generate_invoice_html())
            
            # ضبط إعدادات الطابعة العادية
            self.system_printer.setPageSize(QPrinter.A5)
            self.system_printer.setFullPage(True)
            
            # عرض مربع حوار الطباعة إذا لم يكن طباعة مباشرة
            if not direct_print:
                print_dialog = QPrintDialog(self.system_printer, self)
                if print_dialog.exec_() != QPrintDialog.Accepted:
                    return
            
            # تنفيذ الطباعة
            doc.print_(self.system_printer)
            
            if direct_print:
                QMessageBox.information(self, "تم", "تم طباعة الفاتورة بنجاح")
            else:
                QMessageBox.information(self, "تم", "تم إرسال الفاتورة للطباعة بنجاح")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ في الطباعة", f"حدث خطأ أثناء محاولة الطباعة:\n{str(e)}")
            
            # محاولة إنشاء صورة للفاتورة كحل بديل
            try:
                self.save_invoice_as_image()
                QMessageBox.information(self, "حل بديل", "تم حفظ الفاتورة كصورة في مجلد المستندات")
            except Exception as e2:
                QMessageBox.critical(self, "خطأ", f"فشل في حفظ الفاتورة كصورة:\n{str(e2)}")

    def print_thermal_invoice(self):
        """طباعة الفاتورة على الطابعة الحرارية"""
        if not self.thermal_printer:
            return False
            
        try:
            # إنشاء صورة الفاتورة
            img_width = 384  # مناسب للطابعات 80mm
            img_height = 600  # ارتفاع مناسب للفاتورة
            image = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(image)
            
            # تحميل خط عربي (يجب تثبيت الخط في النظام)
            try:
                font_path = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"
                font = ImageFont.truetype(font_path, 20)
                bold_font = ImageFont.truetype(font_path, 24)
                title_font = ImageFont.truetype(font_path, 28)
            except:
                # إذا لم يتم العثور على الخط العربي، نستخدم خط افتراضي (قد لا يدعم العربية جيداً)
                font = ImageFont.load_default()
                bold_font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # كتابة محتوى الفاتورة
            y = 10
            
            # عنوان المتجر
            draw.text((img_width - 10, y), "منفذ الشهداء", font=title_font, fill="black", anchor="ra")
            y += 40
            
            # معلومات الفاتورة
            draw.text((img_width - 10, y), f"فاتورة رقم: {self.invoice_id}", font=bold_font, fill="black", anchor="ra")
            y += 30
            draw.text((img_width - 10, y), f"التاريخ: {self.date}", font=font, fill="black", anchor="ra")
            y += 30
            draw.text((img_width - 10, y), f"الكاشير: {self.username}", font=font, fill="black", anchor="ra")
            y += 30
            
            # معلومات العضو
            if self.member_input.text():
                draw.text((img_width - 10, y), f"رقم العضوية: {self.member_input.text()}", font=font, fill="black", anchor="ra")
                y += 30
            
            # خط فاصل
            draw.line((10, y, img_width - 10, y), fill="black", width=2)
            y += 20
            
            # عناوين الأعمدة
            headers = ["المنتج", "الكمية", "السعر", "الوزن", "الإجمالي"]
            draw.text((img_width - 10, y), "  ".join(headers), font=bold_font, fill="black", anchor="ra")
            y += 30
            draw.line((10, y, img_width - 10, y), fill="black")
            y += 10
            
            # تفاصيل المنتجات
            for item in self.cart:
                # اسم المنتج (مع تقصير إذا كان طويلاً)
                product_name = item['name'][:15] + "..." if len(item['name']) > 15 else item['name']
                
                # تحضير عرض الكمية والوزن
                quantity_display = str(item['quantity']) if item['quantity'] is not None else "-"
                weight_display = f"{item['weight']:.3f}" if item.get('weight') is not None else "-"
                
                # كتابة بيانات المنتج في سطر واحد
                line = f"{item['total_price']:.2f} ج  {item['price']:.2f} ج  {quantity_display}  {weight_display}  {product_name}"
                draw.text((img_width - 10, y), line, font=font, fill="black", anchor="ra")
                y += 30
            
            # خط فاصل
            draw.line((10, y, img_width - 10, y), fill="black", width=2)
            y += 20
            
            # المجاميع
            draw.text((img_width - 10, y), f"المجموع: {self.total:.2f} ج", font=bold_font, fill="black", anchor="ra")
            draw.text((img_width - 10, y), f"الخصم: {self.discount:.2f} ج", font=bold_font, fill="black", anchor="ra")
            draw.text((img_width - 10, y), f"الصافي: {self.net_total:.2f} ج", font=title_font, fill="black", anchor="ra")
            y += 40
            
            # رسالة الشكر
            draw.text((img_width // 2, y), "شكراً لزيارتكم", font=bold_font, fill="black", anchor="ma")
            y += 30
            draw.text((img_width // 2, y), "نرجو زيارة متجرنا مرة أخرى", font=font, fill="black", anchor="ma")
            
            # قص الورق بعد الطباعة
            self.thermal_printer.image(image)
            self.thermal_printer.cut()
            
            return True
            
        except Exception as e:
            print(f"خطأ في الطباعة الحرارية: {str(e)}")
            return False

    def generate_invoice_html(self):
        items_html = ""
        for idx, item in enumerate(self.cart, 1):
            quantity_display = str(item.get('quantity', '-'))
            weight_display = f"{item.get('weight', 0):.3f}" if item.get('weight') is not None else "-"
            items_html += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{idx}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{item.get('name', '')}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{item.get('code', '')}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{quantity_display}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{weight_display}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{item.get('price', 0):.2f} ج</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{item.get('total_price', 0):.2f} ج</td>
            </tr>
            """
        
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial; direction: rtl; }}
                .header {{ text-align: center; margin-bottom: 15px; }}
                .info {{ margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th {{ background-color: #f2f2f2; padding: 6px; text-align: center; }}
                .total {{ font-weight: bold; margin-top: 8px; }}
                .footer {{ margin-top: 15px; text-align: center; font-style: italic; }}
                .cashier-info {{ text-align: right; margin-top: 10px; color: #444; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>منفذ الشهداء</h1>
                <h2>فاتورة بيع</h2>
            </div>
            
            <div class="info">
                <p><strong>رقم الفاتورة:</strong> {self.invoice_id}</p>
                <p><strong>التاريخ:</strong> {self.date}</p>
                <p><strong>رقم العضوية:</strong> {self.member_input.text() or '-----'}</p>
                <p><strong>الكاشير:</strong> {self.username}</p>
            </div>
            
            <table border="1">
                <tr>
                    <th>م</th>
                    <th>اسم المنتج</th>
                    <th>الكود</th>
                    <th>الكمية</th>
                    <th>الوزن (كجم)</th>
                    <th>سعر الوحدة</th>
                    <th>الإجمالي</th>
                </tr>
                {items_html}
            </table>
            <div class="total">
                <p>المجموع: {self.total:.2f} ج</p>
                <p>الخصم (0%): {self.discount:.2f} ج</p>
                <p>الإجمالي النهائي: {self.net_total:.2f} ج</p>
            </div>
            
            <div class="footer">
                <p>شكراً لزيارتكم - نرجو زيارة متجرنا مرة أخرى</p>
            </div>
        </body>
        </html>
        """
        
    def save_invoice_as_image(self):
        """حفظ الفاتورة كصورة PNG كحل بديل إذا فشلت الطباعة"""
        doc = QTextDocument()
        doc.setHtml(self.generate_invoice_html())
        
        # إنشاء صورة من مستند HTML
        img = QImage(doc.size().toSize(), QImage.Format_ARGB32)
        img.fill(Qt.white)
        
        painter = QPainter(img)
        doc.drawContents(painter)
        painter.end()
        
        # حفظ الصورة في مجلد المستندات
        docs_path = os.path.expanduser('~/Documents')
        os.makedirs(docs_path, exist_ok=True)
        file_path = os.path.join(docs_path, f"invoice_{self.invoice_id}.png")
        img.save(file_path, "PNG")
        
        return file_path
        
    def closeEvent(self, event):
        """التعامل مع حدث إغلاق النافذة"""
        self.closed_signal.emit()  # إرسال إشارة الإغلاق
        super().closeEvent(event)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = SalesWindow()
    window.show()
    sys.exit(app.exec_())