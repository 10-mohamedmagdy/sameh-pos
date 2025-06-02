from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QApplication, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from database import db
import sys
import os

class MainMenu(QWidget):
    def __init__(self, user_role='admin'):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle("نظام إدارة المبيعات والمخزون")
        self.setGeometry(100, 100, 500, 600)
        self.setMinimumSize(QSize(450, 550))
        
        # Get username from database
        self.username = self.get_current_username()
        
        # Initialize windows as None
        self.product_window = None
        self.sale_window = None
        self.reports_window = None
        self.settings_window = None
        
        # Set window icon
        try:
            self.setWindowIcon(QIcon('icon.png'))
        except:
            pass
            
        self.initUI()
        self.center_window()
        self.showMaximized()  # جعل النافذة مكبرة افتراضياً

    def get_current_username(self):
        """الحصول على اسم المستخدم الحالي من قاعدة البيانات"""
        try:
            db.cursor.execute("SELECT username FROM users WHERE role = ?", (self.user_role,))
            result = db.cursor.fetchone()
            return result[0] if result else "مستخدم"
        except:
            return "مستخدم"

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # User info section
        user_info = QHBoxLayout()
        
        # Welcome message
        welcome_label = QLabel(f"👋 مرحباً، {self.username}")
        welcome_label.setStyleSheet("""
            font-size: 16px;
            color: #34495e;
            padding: 5px;
        """)
        user_info.addWidget(welcome_label)
        
        # Role badge
        role_label = QLabel(f"🔰 {self.user_role}")
        role_label.setStyleSheet(f"""
            font-size: 14px;
            color: white;
            background-color: {'#2ecc71' if self.user_role == 'admin' else '#3498db'};
            padding: 5px 10px;
            border-radius: 10px;
        """)
        user_info.addWidget(role_label)
        
        user_info.addStretch()
        layout.addLayout(user_info)

        # Title
        title = QLabel("📋 القائمة الرئيسية")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            margin: 20px 0;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
        """)
        layout.addWidget(title)

        # Menu buttons based on user role
        menu_buttons = []
        
        if self.user_role == 'admin':
            menu_buttons.extend([
                {
                    "text": "📦 إدارة المنتجات",
                    "action": self.open_product_management,
                    "color": "#3498db",
                    "hover": "#2980b9",
                    "icon": "product_icon.png"
                },
                {
                    "text": "💰 عملية بيع",
                    "action": self.open_sales_window,
                    "color": "#2ecc71",
                    "hover": "#27ae60",
                    "icon": "sale_icon.png"
                },
                {
                    "text": "📊 التقارير والإحصائيات",
                    "action": self.open_reports_window,
                    "color": "#9b59b6",
                    "hover": "#8e44ad",
                    "icon": "report_icon.png"
                },
                {
                    "text": "⚙️ الإعدادات",
                    "action": self.open_settings_window,
                    "color": "#e67e22",
                    "hover": "#d35400",
                    "icon": "settings_icon.png"
                },
                {
                    "text": "💰 تسليم وتسلم الدرج",
                    "action": self.open_cash_drawer,
                    "color": "#16a085",
                    "hover": "#1abc9c",
                    "icon": "drawer_icon.png"
                },
                {
                    "text": "✅ تسجيل الحضور",
                    "action": self.record_check_in,
                    "color": "#27ae60",
                    "hover": "#2ecc71",
                    "icon": "check_in_icon.png"
                },
                {
                    "text": "❌ تسجيل الانصراف",
                    "action": self.record_check_out,
                    "color": "#c0392b",
                    "hover": "#e74c3c",
                    "icon": "check_out_icon.png"
                }
            ])
        else:  # cashier
            menu_buttons.extend([
                {
                    "text": "💰 عملية بيع",
                    "action": self.open_sales_window,
                    "color": "#2ecc71",
                    "hover": "#27ae60",
                    "icon": "sale_icon.png"
                },
                {
                    "text": "💰 تسليم وتسلم الدرج",
                    "action": self.open_cash_drawer,
                    "color": "#16a085",
                    "hover": "#1abc9c",
                    "icon": "drawer_icon.png"
                },
                {
                    "text": "✅ تسجيل الحضور",
                    "action": self.record_check_in,
                    "color": "#27ae60",
                    "hover": "#2ecc71",
                    "icon": "check_in_icon.png"
                },
                {
                    "text": "❌ تسجيل الانصراف",
                    "action": self.record_check_out,
                    "color": "#c0392b",
                    "hover": "#e74c3c",
                    "icon": "check_out_icon.png"
                }
            ])
            
        menu_buttons.append({
            "text": "🚪 تسجيل الخروج",
            "action": self.logout,
            "color": "#e74c3c",
            "hover": "#c0392b",
            "icon": "exit_icon.png"
        })

        # Create button grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Add buttons to grid
        row = 0
        col = 0
        max_cols = 2
        
        for button in menu_buttons:
            btn = QPushButton(button["text"])
            btn.setFont(QFont('Arial', 14))
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(200)
            
            try:
                btn.setIcon(QIcon(button["icon"]))
                btn.setIconSize(QSize(32, 32))
            except:
                pass
                
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {button["color"]};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {button["hover"]};
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background-color: #2c3e50;
                }}
            """)
            
            btn.clicked.connect(button["action"])
            grid.addWidget(btn, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        layout.addLayout(grid)
        layout.addStretch()
        
        # Footer
        footer = QLabel("© 2024 نظام إدارة المبيعات والمخزون")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #7f8c8d;
            padding: 10px;
            font-size: 12px;
        """)
        layout.addWidget(footer)
        
        self.setLayout(layout)

    def logout(self):
        """تسجيل الخروج من النظام"""
        reply = QMessageBox.question(
            self,
            "تأكيد",
            "هل تريد تسجيل الخروج من النظام؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # إغلاق قاعدة البيانات
            try:
                db.close()
                print("تم إغلاق قاعدة البيانات بنجاح")
            except Exception as e:
                print(f"خطأ في إغلاق قاعدة البيانات: {str(e)}")
            
            # إغلاق التطبيق
            QApplication.quit()

    def center_window(self):
        frame = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def open_product_management(self):
        try:
            from product_management import ProductManagementWindow
            if self.product_window is None:
                self.product_window = ProductManagementWindow()
                self.product_window.closed_signal.connect(lambda: setattr(self, 'product_window', None))
            
            self.product_window.show()
            self.product_window.raise_()
            self.product_window.activateWindow()
        except ImportError as e:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على وحدة إدارة المنتجات")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح نافذة المنتجات:\n{str(e)}")

    def open_sales_window(self):
        try:
            print("محاولة فتح نافذة المبيعات...")
            
            # التحقق من اتصال قاعدة البيانات
            from database import db, Database
            if not hasattr(db, 'conn') or db.conn is None:
                print("إعادة تهيئة اتصال قاعدة البيانات...")
                db = Database()
            
            print("محاولة استيراد وحدة المبيعات...")
            from sale_window import SalesWindow
            print("تم استيراد وحدة المبيعات بنجاح")
            
            if self.sale_window is None:
                print("إنشاء نافذة مبيعات جديدة...")
                self.sale_window = SalesWindow(username=self.username)
                self.sale_window.closed_signal.connect(lambda: self.handle_window_close('sale_window'))
                print("تم إنشاء نافذة المبيعات بنجاح")
            
            print("عرض نافذة المبيعات...")
            self.sale_window.show()
            self.sale_window.raise_()
            self.sale_window.activateWindow()
            print("تم فتح نافذة المبيعات بنجاح")
            
        except ImportError as e:
            error_msg = f"خطأ في استيراد وحدة المبيعات: {str(e)}\n"
            error_msg += "المسار الحالي: " + os.getcwd() + "\n"
            error_msg += "مسارات البحث: " + str(sys.path)
            print(error_msg)
            QMessageBox.critical(self, "خطأ", error_msg)
        except Exception as e:
            error_msg = f"خطأ غير متوقع عند فتح نافذة المبيعات: {str(e)}\n"
            error_msg += f"نوع الخطأ: {type(e).__name__}\n"
            error_msg += "التفاصيل الكاملة:\n"
            import traceback
            error_msg += traceback.format_exc()
            print(error_msg)
            QMessageBox.critical(self, "خطأ", error_msg)

    def handle_window_close(self, window_name):
        print(f"إغلاق نافذة {window_name}")
        setattr(self, window_name, None)

    def open_reports_window(self):
        try:
            from reports_window import ReportsWindow
            if self.reports_window is None:
                self.reports_window = ReportsWindow()
                self.reports_window.closed_signal.connect(lambda: setattr(self, 'reports_window', None))
            
            self.reports_window.show()
            self.reports_window.raise_()
            self.reports_window.activateWindow()
        except ImportError as e:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على وحدة التقارير")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح نافذة التقارير:\n{str(e)}")

    def open_settings_window(self):
        try:
            from settings import SettingsWindow
            if self.settings_window is None:
                self.settings_window = SettingsWindow()
                self.settings_window.closed_signal.connect(lambda: setattr(self, 'settings_window', None))
            
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
        except ImportError as e:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على وحدة الإعدادات")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح نافذة الإعدادات:\n{str(e)}")

    def open_cash_drawer(self):
        """فتح نافذة تسليم وتسلم الدرج"""
        try:
            from settings import CashDrawerHandoverDialog
            dialog = CashDrawerHandoverDialog(self)
            dialog.exec_()
        except ImportError as e:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على وحدة تسليم وتسلم الدرج")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح نافذة تسليم وتسلم الدرج:\n{str(e)}")
            
    def record_check_in(self):
        """تسجيل الحضور للمستخدم الحالي"""
        try:
            success, message = db.record_attendance(self.username, 'in')
            if success:
                QMessageBox.information(self, "تسجيل الحضور", message)
            else:
                QMessageBox.warning(self, "تحذير", message)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تسجيل الحضور:\n{str(e)}")
            
    def record_check_out(self):
        """تسجيل الانصراف للمستخدم الحالي"""
        try:
            success, message = db.record_attendance(self.username, 'out')
            if success:
                QMessageBox.information(self, "تسجيل الانصراف", message)
            else:
                QMessageBox.warning(self, "تحذير", message)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تسجيل الانصراف:\n{str(e)}")

    def show_under_development(self):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("تطوير")
        msg.setText("هذه الميزة قيد التطوير")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):
        print("بدء إغلاق التطبيق...")
        # Close all child windows
        for window_name in ['product_window', 'sale_window', 'reports_window', 'settings_window']:
            window = getattr(self, window_name)
            if window is not None and window.isVisible():
                print(f"إغلاق {window_name}...")
                window.close()
        
        # Close database connection
        try:
            print("إغلاق اتصال قاعدة البيانات...")
            db.close()
            print("تم إغلاق قاعدة البيانات بنجاح")
        except Exception as e:
            print(f"خطأ في إغلاق قاعدة البيانات: {str(e)}")
        
        print("إغلاق التطبيق...")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply application-wide styles
    app.setStyleSheet("""
        QWidget {
            font-family: 'Arial';
            font-size: 14px;
        }
        QMessageBox {
            min-width: 300px;
        }
        QPushButton {
            min-width: 120px;
        }
    """)
    
    # Set application font
    font = QFont()
    font.setFamily("Arial")
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())