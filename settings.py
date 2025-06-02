from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                            QDialog, QComboBox, QFrame, QDateEdit, QTextEdit, QCheckBox,
                            QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from database import db

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة المستخدمين")
        # تكبير النافذة وجعلها قابلة للتمدد
        self.setGeometry(100, 50, 800, 600)
        # تعيين الحد الأدنى للحجم
        self.setMinimumSize(600, 500)
        # تمكين أزرار التكبير والتصغير وجعل النافذة مكبرة افتراضياً
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.showMaximized()  # جعل النافذة مكبرة افتراضياً
        
        self.initUI()
        
        # إضافة متغيرات للحالة
        self.edit_mode = False
        self.current_username = ""

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # عنوان النافذة
        title = QLabel("👥 إضافة وتعديل المستخدمين")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # نموذج إضافة مستخدم جديد
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان النموذج
        self.form_title = QLabel("إضافة مستخدم جديد")
        self.form_title.setObjectName("form_title")
        self.form_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        form_layout.addWidget(self.form_title)
        
        # إضافة حقل البحث عن المستخدم
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث عن مستخدم:")
        search_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل اسم المستخدم واضغط Enter للبحث")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.returnPressed.connect(self.search_user)
        search_layout.addWidget(self.search_input)
        
        form_layout.addLayout(search_layout)
        
        # خط فاصل بعد البحث
        separator0 = QFrame()
        separator0.setFrameShape(QFrame.HLine)
        separator0.setFrameShadow(QFrame.Sunken)
        separator0.setStyleSheet("background-color: #bdc3c7; margin: 10px 0;")
        form_layout.addWidget(separator0)
        
        # معلومات المستخدم الأساسية
        basic_info = QHBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "cashier"])
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        
        basic_info.addWidget(QLabel("اسم المستخدم:"))
        basic_info.addWidget(self.username_input)
        basic_info.addWidget(QLabel("كلمة المرور:"))
        basic_info.addWidget(self.password_input)
        basic_info.addWidget(QLabel("الصلاحية:"))
        basic_info.addWidget(self.role_combo)
        
        form_layout.addLayout(basic_info)
        
        # إضافة خط فاصل
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7; margin: 10px 0;")
        form_layout.addWidget(separator)
        
        # قسم أيام العمل
        work_days_title = QLabel("🗓️ أيام العمل:")
        work_days_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        form_layout.addWidget(work_days_title)
        
        work_days_info = QLabel("حدد الأيام التي سيعمل فيها المستخدم:")
        work_days_info.setStyleSheet("font-style: italic; color: #7f8c8d; margin-bottom: 5px;")
        form_layout.addWidget(work_days_info)
        
        days_layout = QHBoxLayout()
        days_layout.setSpacing(10)
        
        # إنشاء خانات اختيار لكل يوم من أيام الأسبوع
        self.day_checkboxes = {}
        days = ["السبت", "الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة"]
        
        for day in days:
            checkbox = QCheckBox(day)
            checkbox.setChecked(day != "الجمعة")  # افتراضياً كل الأيام مختارة ما عدا الجمعة
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)
        
        form_layout.addLayout(days_layout)
        
        # قسم ساعات العمل
        hours_title = QLabel("⏰ ساعات العمل:")
        hours_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-top: 10px;")
        form_layout.addWidget(hours_title)
        
        hours_info = QLabel("حدد ساعات بداية ونهاية الدوام:")
        hours_info.setStyleSheet("font-style: italic; color: #7f8c8d; margin-bottom: 5px;")
        form_layout.addWidget(hours_info)
        
        hours_layout = QHBoxLayout()
        
        hours_layout.addWidget(QLabel("من الساعة:"))
        self.start_hour = QComboBox()
        for hour in range(0, 24):
            self.start_hour.addItem(f"{hour:02d}:00")
        self.start_hour.setCurrentIndex(8)  # افتراضياً 8 صباحاً
        self.start_hour.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                min-width: 80px;
            }
        """)
        
        hours_layout.addWidget(self.start_hour)
        hours_layout.addWidget(QLabel("إلى الساعة:"))
        
        self.end_hour = QComboBox()
        for hour in range(0, 24):
            self.end_hour.addItem(f"{hour:02d}:00")
        self.end_hour.setCurrentIndex(20)  # افتراضياً 8 مساءً
        self.end_hour.setStyleSheet(self.start_hour.styleSheet())
        
        hours_layout.addWidget(self.end_hour)
        hours_layout.addStretch()
        
        form_layout.addLayout(hours_layout)
        
        # إضافة خط فاصل آخر
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #bdc3c7; margin: 10px 0;")
        form_layout.addWidget(separator2)
        
        # أزرار العمليات
        buttons_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ إضافة مستخدم")
        self.add_btn.setObjectName("add_btn")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.add_btn.clicked.connect(self.add_user)
        buttons_layout.addWidget(self.add_btn)
        
        # زر حفظ التعديلات
        self.save_btn = QPushButton("💾 حفظ التعديلات")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)  # تعطيل الزر حتى يتم تحديد مستخدم
        buttons_layout.addWidget(self.save_btn)
        
        # زر تعديل مستخدم
        edit_btn = QPushButton("🔍 تعديل مستخدم")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        edit_btn.clicked.connect(self.search_user)
        buttons_layout.addWidget(edit_btn)
        
        # زر حذف المستخدم (بدلاً من مسح الحقول)
        self.delete_btn = QPushButton("🗑️ حذف المستخدم")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_user)
        self.delete_btn.setEnabled(False)  # تعطيل الزر حتى يتم تحديد مستخدم
        buttons_layout.addWidget(self.delete_btn)
        
        form_layout.addLayout(buttons_layout)
        
        layout.addWidget(form_frame)
        layout.addStretch()  # إضافة مساحة فارغة في نهاية التخطيط

        self.setLayout(layout)

    def search_user(self):
        """البحث عن مستخدم بالاسم"""
        username = self.search_input.text().strip()
        if not username:
            QMessageBox.warning(self, "تحذير", "الرجاء إدخال اسم المستخدم للبحث")
            return
            
        try:
            # البحث عن المستخدم في قاعدة البيانات
            user_data = db.get_user_with_schedule(username)
            if user_data:
                # استخراج البيانات
                username = user_data[0]
                role = user_data[1]
                work_days = user_data[3] if len(user_data) > 3 and user_data[3] else "السبت,الأحد,الإثنين,الثلاثاء,الأربعاء,الخميس"
                start_hour = user_data[4] if len(user_data) > 4 and user_data[4] else "08:00"
                end_hour = user_data[5] if len(user_data) > 5 and user_data[5] else "20:00"
                
                # تحميل بيانات المستخدم في النموذج
                self.load_user_data(username, role, work_days, start_hour, end_hour)
                
                # تفعيل زر حفظ التعديلات وزر الحذف
                self.save_btn.setEnabled(True)
                self.delete_btn.setEnabled(username != 'admin')  # لا يمكن حذف المستخدم admin
            else:
                QMessageBox.warning(self, "تحذير", f"لم يتم العثور على المستخدم: {username}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء البحث عن المستخدم: {str(e)}")

    def clear_fields(self):
        """مسح جميع الحقول وإعادة ضبطها على القيم الافتراضية"""
        self.username_input.clear()
        self.username_input.setReadOnly(False)
        self.password_input.clear()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.role_combo.setCurrentIndex(0)
        self.search_input.clear()
        
        # إعادة ضبط أيام العمل
        for day, checkbox in self.day_checkboxes.items():
            checkbox.setChecked(day != "الجمعة")
        
        # إعادة ضبط ساعات العمل
        self.start_hour.setCurrentIndex(8)  # 8 صباحاً
        self.end_hour.setCurrentIndex(20)   # 8 مساءً
        
        # إلغاء وضع التعديل
        self.edit_mode = False
        self.current_username = ""
        
        # تحديث عنوان النموذج
        self.form_title.setText("إضافة مستخدم جديد")
        
        # تحديث نص زر الإضافة وتعطيل زر الحفظ والحذف
        self.add_btn.setText("➕ إضافة مستخدم")
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def load_user_data(self, username, role, work_days, start_hour, end_hour):
        """تحميل بيانات المستخدم للتعديل"""
        try:
            # تعيين وضع التعديل
            self.edit_mode = True
            self.current_username = username
            
            # ملء الحقول ببيانات المستخدم
            self.username_input.setText(username)
            self.username_input.setReadOnly(True)  # لا يمكن تغيير اسم المستخدم
            self.password_input.clear()  # لا نعرض كلمة المرور الحالية
            self.password_input.setPlaceholderText("اترك فارغاً إذا لم ترغب في تغيير كلمة المرور")
            
            # تعيين الدور
            index = self.role_combo.findText(role)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
            
            # تعيين أيام العمل
            days_list = work_days.split(",")
            for day, checkbox in self.day_checkboxes.items():
                checkbox.setChecked(day in days_list)
            
            # تعيين ساعات العمل
            start_index = self.start_hour.findText(start_hour)
            if start_index >= 0:
                self.start_hour.setCurrentIndex(start_index)
                
            end_index = self.end_hour.findText(end_hour)
            if end_index >= 0:
                self.end_hour.setCurrentIndex(end_index)
            
            # تغيير عنوان النموذج
            self.form_title.setText(f"تعديل المستخدم: {username}")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل بيانات المستخدم: {str(e)}")

    def save_changes(self):
        """حفظ التعديلات على المستخدم الحالي"""
        if not self.edit_mode or not self.current_username:
            QMessageBox.warning(self, "تحذير", "الرجاء تحديد مستخدم للتعديل أولاً")
            return
            
        self.add_user()  # استخدام نفس الدالة لحفظ التغييرات

    def delete_user(self):
        """حذف المستخدم الحالي"""
        if not self.edit_mode or not self.current_username:
            QMessageBox.warning(self, "تحذير", "الرجاء تحديد مستخدم للحذف أولاً")
            return
            
        # لا يمكن حذف المستخدم admin
        if self.current_username == 'admin':
            QMessageBox.warning(self, "تحذير", "لا يمكن حذف المستخدم admin")
            return
            
        # تأكيد الحذف
        reply = QMessageBox.question(
            self, 
            "تأكيد الحذف",
            f"هل أنت متأكد من حذف المستخدم {self.current_username}؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # حذف المستخدم
                if db.delete_user(self.current_username):
                    QMessageBox.information(self, "تم", f"تم حذف المستخدم {self.current_username} بنجاح")
                    self.clear_fields()
                else:
                    QMessageBox.warning(self, "تحذير", "فشل حذف المستخدم")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف المستخدم: {str(e)}")

    def add_user(self):
        """إضافة مستخدم جديد أو تحديث مستخدم موجود"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText()
        
        # جمع أيام العمل المحددة
        work_days = []
        for day, checkbox in self.day_checkboxes.items():
            if checkbox.isChecked():
                work_days.append(day)
        
        work_days_str = ",".join(work_days)
        
        # الحصول على ساعات العمل
        start_hour = self.start_hour.currentText()
        end_hour = self.end_hour.currentText()
        
        try:
            if self.edit_mode:
                # تحديث مستخدم موجود
                if not password:
                    # إذا كانت كلمة المرور فارغة، نستخدم دالة تحديث بدون تغيير كلمة المرور
                    if db.update_user_without_password(username, role, work_days_str, start_hour, end_hour):
                        QMessageBox.information(self, "تم", "تم تحديث بيانات المستخدم بنجاح")
                        self.clear_fields()
                    else:
                        QMessageBox.warning(self, "تحذير", "فشل تحديث المستخدم")
                else:
                    # إذا تم إدخال كلمة مرور جديدة
                    if db.update_user(username, password, role, work_days_str, start_hour, end_hour):
                        QMessageBox.information(self, "تم", "تم تحديث بيانات المستخدم بنجاح")
                        self.clear_fields()
                    else:
                        QMessageBox.warning(self, "تحذير", "فشل تحديث المستخدم")
            else:
                # إضافة مستخدم جديد
                if not username or not password:
                    QMessageBox.warning(self, "تحذير", "يجب ملء اسم المستخدم وكلمة المرور")
                    return
                    
                if db.add_user_with_schedule(username, password, role, work_days_str, start_hour, end_hour):
                    QMessageBox.information(self, "تم", "تم إضافة المستخدم بنجاح")
                    self.clear_fields()
                else:
                    QMessageBox.warning(self, "تحذير", "اسم المستخدم موجود بالفعل")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")

class UsersListWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("قائمة المستخدمين")
        # تكبير النافذة وجعلها قابلة للتمدد
        self.setGeometry(100, 50, 1300, 750)
        # تعيين الحد الأدنى للحجم
        self.setMinimumSize(1200, 700)
        # تمكين أزرار التكبير والتصغير
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        self.initUI()
        self.load_users()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        # زيادة هوامش الصفحة الرئيسية
        layout.setContentsMargins(25, 25, 25, 25)

        # عنوان النافذة
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel("👥 قائمة المستخدمين")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        
        layout.addWidget(title_frame)

        # أزرار العمليات - وضعها في إطار منفصل
        actions_frame = QFrame()
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
            }
        """)
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setSpacing(20)
        
        add_btn = QPushButton("➕ إضافة مستخدم جديد")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 18px 30px;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                min-height: 60px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_btn.clicked.connect(self.add_new_user)
        actions_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 تحديث القائمة")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 18px 30px;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                min-height: 60px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_users)
        actions_layout.addWidget(refresh_btn)
        
        # زر العودة للإعدادات
        back_btn = QPushButton("↩️ العودة للإعدادات")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                padding: 18px 30px;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                min-height: 60px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        back_btn.clicked.connect(self.close)
        actions_layout.addWidget(back_btn)
        
        actions_layout.addStretch()
        
        layout.addWidget(actions_frame)

        # إطار قائمة المستخدمين
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 25px;
                margin-top: 20px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setSpacing(15)
        
        # عنوان فرعي للجدول
        table_title = QLabel("بيانات المستخدمين")
        table_title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 15px;
            border-bottom: 1px solid #bdc3c7;
            margin-bottom: 15px;
        """)
        list_layout.addWidget(table_title)
        
        # جدول المستخدمين
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels(["اسم المستخدم", "الصلاحية", "تاريخ الإنشاء", "أيام العمل", "من", "إلى", "تعديل", "حذف"])
        self.users_table.horizontalHeader().setStretchLastSection(False)
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 15px;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QTableWidget::item:selected {
                background-color: #e8f4fc;
                color: #2c3e50;
            }
        """)
        
        # تعيين عرض الأعمدة
        self.users_table.setColumnWidth(0, 150)  # اسم المستخدم
        self.users_table.setColumnWidth(1, 120)  # الصلاحية
        self.users_table.setColumnWidth(2, 150)  # تاريخ الإنشاء
        self.users_table.setColumnWidth(3, 350)  # أيام العمل
        self.users_table.setColumnWidth(4, 100)  # من
        self.users_table.setColumnWidth(5, 100)  # إلى
        self.users_table.setColumnWidth(6, 100)  # تعديل
        self.users_table.setColumnWidth(7, 100)  # حذف
        
        # تعيين ارتفاع الصفوف
        self.users_table.verticalHeader().setDefaultSectionSize(60)
        # إخفاء رؤوس الصفوف (أرقام الصفوف)
        self.users_table.verticalHeader().setVisible(False)
        # تمكين التمرير التلقائي
        self.users_table.setAutoScroll(True)
        # السماح بتحديد صف كامل
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        # تعيين لون الخلفية للصفوف بالتناوب
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setStyleSheet(self.users_table.styleSheet() + """
            QTableWidget {
                alternate-background-color: #f5f5f5;
            }
        """)
        
        list_layout.addWidget(self.users_table)
        
        # إضافة تذييل للجدول
        footer = QLabel("ملاحظة: لا يمكن حذف المستخدم 'admin' لأنه المستخدم الرئيسي للنظام")
        footer.setStyleSheet("""
            font-size: 14px;
            font-style: italic;
            color: #7f8c8d;
            margin-top: 10px;
        """)
        footer.setAlignment(Qt.AlignRight)
        list_layout.addWidget(footer)
        
        layout.addWidget(list_frame)

        self.setLayout(layout)

    def load_users(self):
        try:
            users = db.get_all_users()
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                username = user[0]
                role = user[1]
                date = user[2]
                work_days = user[3] if len(user) > 3 and user[3] else "السبت,الأحد,الإثنين,الثلاثاء,الأربعاء,الخميس"
                start_hour = user[4] if len(user) > 4 and user[4] else "08:00"
                end_hour = user[5] if len(user) > 5 and user[5] else "20:00"
                
                username_item = QTableWidgetItem(username)
                username_item.setTextAlignment(Qt.AlignCenter)
                
                role_item = QTableWidgetItem()
                role_item.setTextAlignment(Qt.AlignCenter)
                
                date_item = QTableWidgetItem(date)
                date_item.setTextAlignment(Qt.AlignCenter)
                
                work_days_item = QTableWidgetItem(work_days)
                work_days_item.setTextAlignment(Qt.AlignCenter)
                
                start_hour_item = QTableWidgetItem(start_hour)
                start_hour_item.setTextAlignment(Qt.AlignCenter)
                
                end_hour_item = QTableWidgetItem(end_hour)
                end_hour_item.setTextAlignment(Qt.AlignCenter)
                
                # تنسيق خاص للمشرف
                if role == 'admin':
                    username_item.setForeground(Qt.darkGreen)
                    role_item.setForeground(Qt.darkGreen)
                    role_item.setText("مشرف")
                elif role == 'cashier':
                    role_item.setText("كاشير")
                    role_item.setForeground(Qt.blue)
                
                self.users_table.setItem(row, 0, username_item)
                self.users_table.setItem(row, 1, role_item)
                self.users_table.setItem(row, 2, date_item)
                self.users_table.setItem(row, 3, work_days_item)
                self.users_table.setItem(row, 4, start_hour_item)
                self.users_table.setItem(row, 5, end_hour_item)
                
                # زر التعديل
                edit_cell = QWidget()
                edit_layout = QHBoxLayout(edit_cell)
                edit_layout.setAlignment(Qt.AlignCenter)
                edit_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("✏️")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 10px;
                        font-size: 16px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, u=username, r=role, w=work_days, s=start_hour, e=end_hour: self.edit_user(u, r, w, s, e))
                edit_layout.addWidget(edit_btn)
                self.users_table.setCellWidget(row, 6, edit_cell)
                
                # زر الحذف
                delete_cell = QWidget()
                delete_layout = QHBoxLayout(delete_cell)
                delete_layout.setAlignment(Qt.AlignCenter)
                delete_layout.setContentsMargins(0, 0, 0, 0)
                
                if username != 'admin':  # لا يمكن حذف المستخدم admin
                    delete_btn = QPushButton("🗑️")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            padding: 10px;
                            font-size: 16px;
                            font-weight: bold;
                            min-width: 80px;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    delete_btn.clicked.connect(lambda checked, u=username: self.delete_user(u))
                    delete_layout.addWidget(delete_btn)
                
                self.users_table.setCellWidget(row, 7, delete_cell)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل المستخدمين: {str(e)}")

    def add_new_user(self):
        """فتح نافذة إضافة مستخدم جديد"""
        dialog = UserManagementDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()  # تحديث القائمة بعد الإضافة
    
    def edit_user(self, username, role, work_days, start_hour, end_hour):
        """تعديل مستخدم موجود"""
        dialog = UserManagementDialog(self)
        dialog.load_user_data(username, role, work_days, start_hour, end_hour)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()  # تحديث القائمة بعد التعديل

    def delete_user(self, username):
        """حذف مستخدم"""
        reply = QMessageBox.question(
            self,
            "تأكيد",
            f"هل أنت متأكد من حذف المستخدم {username}؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if db.delete_user(username):
                    self.load_users()
                    QMessageBox.information(self, "تم", "تم حذف المستخدم بنجاح")
                else:
                    QMessageBox.warning(self, "تحذير", "لا يمكن حذف المستخدم admin")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف المستخدم: {str(e)}")

class CashDrawerHandoverDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تسليم وتسلم الدرج")
        self.setGeometry(200, 200, 600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # عنوان النافذة
        title = QLabel("💰 تسليم وتسلم الدرج")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # نموذج إضافة عملية تسليم جديدة
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # الصف الأول: المسلم والمستلم
        row1 = QHBoxLayout()
        
        delivered_by_label = QLabel("المُسلم:")
        delivered_by_label.setStyleSheet("font-weight: bold;")
        self.delivered_by_combo = QComboBox()
        self.delivered_by_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        received_by_label = QLabel("المُستلم:")
        received_by_label.setStyleSheet("font-weight: bold;")
        self.received_by_combo = QComboBox()
        self.received_by_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        row1.addWidget(delivered_by_label)
        row1.addWidget(self.delivered_by_combo)
        row1.addWidget(received_by_label)
        row1.addWidget(self.received_by_combo)
        
        # الصف الثاني: المبلغ والملاحظات
        row2 = QHBoxLayout()
        
        amount_label = QLabel("المبلغ:")
        amount_label.setStyleSheet("font-weight: bold;")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("أدخل المبلغ")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        notes_label = QLabel("ملاحظات:")
        notes_label.setStyleSheet("font-weight: bold;")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية")
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        row2.addWidget(amount_label)
        row2.addWidget(self.amount_input)
        row2.addWidget(notes_label)
        row2.addWidget(self.notes_input)
        
        form_layout.addLayout(row1)
        form_layout.addLayout(row2)
        
        # زر التسجيل
        add_btn = QPushButton("✅ تسجيل عملية التسليم")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_btn.clicked.connect(self.save_handover)
        form_layout.addWidget(add_btn)
        
        layout.addWidget(form_frame)

        # إضافة مساحة مرنة في أسفل النافذة
        layout.addStretch()
        
        # رسالة توجيه للمستخدم
        info_label = QLabel("لعرض سجلات تسليم وتسلم الدرج، يرجى الانتقال إلى قسم التقارير")
        info_label.setStyleSheet("""
            color: #7f8c8d; 
            font-style: italic;
            padding: 10px;
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        self.setLayout(layout)
        
        # تحميل المستخدمين
        self.load_users()

    def load_users(self):
        """تحميل قائمة المستخدمين"""
        try:
            users = db.get_all_users()
            
            for user in users:
                username = user[0]
                self.delivered_by_combo.addItem(username)
                self.received_by_combo.addItem(username)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل المستخدمين: {str(e)}")

    def save_handover(self):
        """تسجيل عملية تسليم جديدة"""
        delivered_by = self.delivered_by_combo.currentText()
        received_by = self.received_by_combo.currentText()
        
        # التحقق من عدم تطابق المسلم والمستلم
        if delivered_by == received_by:
            QMessageBox.warning(self, "تحذير", "لا يمكن أن يكون المُسلم والمُستلم نفس الشخص!")
            return
            
        try:
            amount_text = self.amount_input.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "تحذير", "يرجى إدخال المبلغ")
                return
                
            amount = float(amount_text)
            notes = self.notes_input.toPlainText().strip()
            
            if db.save_cash_drawer_handover(delivered_by, received_by, amount, notes):
                QMessageBox.information(self, "تم", "تم تسجيل عملية التسليم بنجاح")
                self.amount_input.clear()
                self.notes_input.clear()
            else:
                QMessageBox.warning(self, "تحذير", "حدث خطأ أثناء تسجيل عملية التسليم")
                
        except ValueError:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ صحيح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تسجيل عملية التسليم: {str(e)}")

class SettingsWindow(QWidget):
    closed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚙️ الإعدادات")
        # تكبير النافذة وجعلها قابلة للتمدد
        self.setGeometry(50, 50, 1200, 800)
        # تعيين الحد الأدنى للحجم
        self.setMinimumSize(1000, 700)
        # تمكين أزرار التكبير والتصغير
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        
        self.initUI()

    def initUI(self):
        # إنشاء تخطيط رئيسي عمودي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # عنوان النافذة
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel("⚙️ الإعدادات")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        
        main_layout.addWidget(title_frame)

        # منطقة قابلة للتمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # إنشاء ويدجت للمحتوى القابل للتمرير
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25)
        
        # إطار الأزرار
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 35px;
                border: 1px solid #e0e0e0;
            }
        """)
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setSpacing(25)
        buttons_layout.setContentsMargins(20, 20, 20, 20)

        # زر إدارة المستخدمين
        users_btn = QPushButton("👥 إدارة المستخدمين وجداول العمل")
        users_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 35px;
                border: none;
                border-radius: 15px;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        users_btn.setMinimumHeight(120)
        users_btn.clicked.connect(self.open_user_management)
        buttons_layout.addWidget(users_btn)

        # إضافة وصف توضيحي
        description = QLabel("من هنا يمكنك إضافة وتعديل المستخدمين وتحديد أيام وساعات العمل الخاصة بهم")
        description.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
            margin-top: 10px;
            padding: 10px;
            text-align: center;
        """)
        description.setAlignment(Qt.AlignCenter)
        buttons_layout.addWidget(description)

        scroll_layout.addWidget(buttons_frame)
        
        # إضافة مساحة فارغة في نهاية التخطيط
        scroll_layout.addStretch()
        
        # تعيين المحتوى للمنطقة القابلة للتمرير
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def open_user_management(self):
        """فتح نافذة إضافة مستخدم جديد"""
        dialog = UserManagementDialog(self)
        dialog.exec_()

    def closeEvent(self, event):
        """التعامل مع حدث إغلاق النافذة"""
        self.closed_signal.emit()
        super().closeEvent(event) 