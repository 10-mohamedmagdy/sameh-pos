from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from main_menu import MainMenu
from database import db

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول")
        self.setGeometry(150, 150, 350, 400)  # حجم أصغر ومناسب
        self.setFixedSize(350, 400)
        self.initUI()
        self.center_window()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # العنوان
        title = QLabel("تسجيل الدخول")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # اسم المستخدم
        username_label = QLabel("اسم المستخدم:")
        username_label.setStyleSheet("font-size: 14px; color: #34495e; padding: 5px;")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("أدخل اسم المستخدم...")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.username_input)

        # كلمة المرور
        password_label = QLabel("كلمة المرور:")
        password_label.setStyleSheet("font-size: 14px; color: #34495e; padding: 5px;")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        layout.addWidget(self.password_input)

        # زر تسجيل الدخول
        login_btn = QPushButton("دخول")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                min-height: 40px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        layout.addStretch()

        # Footer
        footer = QLabel("© 2025 نظام إدارة المبيعات والمخزون")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(footer)

        self.setLayout(layout)
        
        # تنسيق النافذة الرئيسية
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: Arial;
            }
        """)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        try:
            db.cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?",
                            (username, password))
            user = db.cursor.fetchone()

            if user:
                self.main_menu = MainMenu(user_role=user[0])
                self.main_menu.show()
                self.close()
            else:
                QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تسجيل الدخول: {str(e)}")

    def center_window(self):
        frame = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())
