from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QDateEdit, QHBoxLayout, QMessageBox,
    QTabWidget, QSpinBox, QLineEdit, QDialog, QStackedWidget,
    QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from database import db

class ReportsWindow(QWidget):
    closed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("التقارير والإحصائيات")
        self.setGeometry(200, 200, 1200, 800)
        self.setStyleSheet("background-color: #f0f8ff;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        self.showMaximized()  # جعل النافذة مكبرة افتراضياً
        
        # تهيئة التواريخ الافتراضية
        current_date = QDate.currentDate()
        self.default_start_date = current_date.toString("yyyy-MM-dd")
        self.default_end_date = current_date.toString("yyyy-MM-dd")
        
        self.initUI()
        
        # تحميل البيانات تلقائياً عند فتح النافذة
        self.load_initial_data()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # العنوان الرئيسي
        header = QLabel("📊 لوحة التقارير الرئيسية")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

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

        # إضافة أزرار التقارير
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # زر تقرير المبيعات
        sales_btn = QPushButton("📊 تقرير المبيعات")
        sales_btn.setStyleSheet(button_style)
        sales_btn.clicked.connect(lambda: self.show_report(0))
        buttons_layout.addWidget(sales_btn)

        # زر تقرير المخزون
        inventory_btn = QPushButton("📦 تقرير المخزون")
        inventory_btn.setStyleSheet(button_style)
        inventory_btn.clicked.connect(lambda: self.show_report(1))
        buttons_layout.addWidget(inventory_btn)

        # زر المنتجات الأكثر مبيعاً
        top_products_btn = QPushButton("⭐ المنتجات\nالأكثر مبيعاً")
        top_products_btn.setStyleSheet(button_style)
        top_products_btn.clicked.connect(lambda: self.show_report(2))
        buttons_layout.addWidget(top_products_btn)

        # زر المنتجات الأقل مبيعاً
        low_products_btn = QPushButton("📉 المنتجات\nالأقل مبيعاً")
        low_products_btn.setStyleSheet(button_style)
        low_products_btn.clicked.connect(lambda: self.show_report(3))
        buttons_layout.addWidget(low_products_btn)
        
        # زر سجل تسليم وتسلم الدرج
        cash_drawer_btn = QPushButton("💰 سجل تسليم\nوتسلم الدرج")
        cash_drawer_btn.setStyleSheet(button_style)
        cash_drawer_btn.clicked.connect(lambda: self.show_report(4))
        buttons_layout.addWidget(cash_drawer_btn)

        # زر سجل المستخدمين
        users_btn = QPushButton("👥 سجل المستخدمين")
        users_btn.setStyleSheet(button_style)
        users_btn.clicked.connect(lambda: self.show_report(5))
        buttons_layout.addWidget(users_btn)

        # زر سجل الحضور والانصراف
        attendance_btn = QPushButton("🕒 سجل الحضور\nوالانصراف")
        attendance_btn.setStyleSheet(button_style)
        attendance_btn.clicked.connect(lambda: self.show_report(6))
        buttons_layout.addWidget(attendance_btn)

        main_layout.addLayout(buttons_layout)

        # إضافة مساحة لعرض التقارير
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_sales_report())
        self.stacked_widget.addWidget(self.create_stock_report())
        self.stacked_widget.addWidget(self.create_popular_products_report())
        self.stacked_widget.addWidget(self.create_low_demand_products_report())
        self.stacked_widget.addWidget(self.create_cash_drawer_report())
        self.stacked_widget.addWidget(self.create_users_report())
        self.stacked_widget.addWidget(self.create_attendance_report())
        main_layout.addWidget(self.stacked_widget)
        
        self.setLayout(main_layout)

    def show_report(self, index):
        """عرض التقرير المحدد"""
        self.stacked_widget.setCurrentIndex(index)
        
        # تحميل البيانات عند تغيير التقرير
        if index == 0:  # تقرير المبيعات
            if not self.start_date_text.text() or not self.end_date_text.text():
                self.start_date_text.setText(self.default_start_date)
                self.end_date_text.setText(self.default_end_date)
            self.load_sales_data()
        elif index == 1:  # تقرير المخزون
            if not self.stock_start_date.text() or not self.stock_end_date.text():
                self.stock_start_date.setText(self.default_start_date)
                self.stock_end_date.setText(self.default_end_date)
            self.load_stock_data()
        elif index == 2:  # المنتجات الأكثر مبيعاً
            if not self.popular_start_date.text() or not self.popular_end_date.text():
                self.popular_start_date.setText(self.default_start_date)
                self.popular_end_date.setText(self.default_end_date)
            self.load_popular_products()
        elif index == 3:  # المنتجات الأقل مبيعاً
            if not self.low_demand_start_date.text() or not self.low_demand_end_date.text():
                self.low_demand_start_date.setText(self.default_start_date)
                self.low_demand_end_date.setText(self.default_end_date)
            self.load_low_demand_products()
        elif index == 4:  # سجل تسليم وتسلم الدرج
            if not self.cash_drawer_start_date.text() or not self.cash_drawer_end_date.text():
                self.cash_drawer_start_date.setText(self.default_start_date)
                self.cash_drawer_end_date.setText(self.default_end_date)
            self.load_cash_drawer_report()
        elif index == 5:  # سجل المستخدمين
            self.load_users_report()
        elif index == 6:  # سجل الحضور والانصراف
            if not self.attendance_start_date.text() or not self.attendance_end_date.text():
                self.attendance_start_date.setText(self.default_start_date)
                self.attendance_end_date.setText(self.default_end_date)
            self.load_attendance_report()

    def create_sales_report(self):
        """إنشاء تقرير المبيعات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # تحكم التاريخ
        date_controls = QHBoxLayout()
        date_controls.addWidget(QLabel("من تاريخ:"))
        
        self.start_date_text = QLineEdit()
        self.start_date_text.setPlaceholderText("YYYY-MM-DD")
        self.start_date_text.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_controls.addWidget(self.start_date_text)
        
        date_controls.addWidget(QLabel("إلى تاريخ:"))
        self.end_date_text = QLineEdit()
        self.end_date_text.setPlaceholderText("YYYY-MM-DD")
        self.end_date_text.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_controls.addWidget(self.end_date_text)
        
        self.btn_refresh_sales = QPushButton("تحديث البيانات")
        self.btn_refresh_sales.clicked.connect(self.load_sales_data)
        self.btn_refresh_sales.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        date_controls.addWidget(self.btn_refresh_sales)
        
        # إضافة مساحة مرنة لمحاذاة العناصر
        date_controls.addStretch()
        
        layout.addLayout(date_controls)

        # إضافة ملخص المبيعات والأرباح
        summary_layout = QHBoxLayout()
        
        self.sales_summary = QLabel("إجمالي المبيعات: 0")
        self.sales_summary.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        self.sales_summary.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.sales_summary)
        
        self.profit_summary = QLabel("إجمالي الربح: 0")
        self.profit_summary.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #27ae60;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        self.profit_summary.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.profit_summary)
        
        layout.addLayout(summary_layout)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)  # إضافة عمود الربح
        self.sales_table.setHorizontalHeaderLabels([
            "رقم الفاتورة", "التاريخ", "رقم العميل",
            "الإجمالي", "الخصم", "الصافي", "الربح"
        ])
        self.style_table(self.sales_table)
        self.sales_table.cellDoubleClicked.connect(self.show_invoice_details)
        
        layout.addWidget(self.sales_table)
        
        info_label = QLabel("انقر نقرًا مزدوجًا على أي فاتورة لعرض التفاصيل")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        widget.setLayout(layout)
        return widget

    def create_stock_report(self):
        """إنشاء تقرير المخزون"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # إضافة هوامش للتنسيق
        
        # إضافة التحكم في التاريخ
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)  # المسافة بين عناصر التحكم
        
        # حقول التاريخ
        date_group = QHBoxLayout()
        date_group.addWidget(QLabel("من تاريخ:"))
        self.stock_start_date = QLineEdit()
        self.stock_start_date.setPlaceholderText("YYYY-MM-DD")
        self.stock_start_date.setText(self.default_start_date)
        self.stock_start_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_group.addWidget(self.stock_start_date)
        
        date_group.addWidget(QLabel("إلى تاريخ:"))
        self.stock_end_date = QLineEdit()
        self.stock_end_date.setPlaceholderText("YYYY-MM-DD")
        self.stock_end_date.setText(self.default_end_date)
        self.stock_end_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_group.addWidget(self.stock_end_date)
        
        # إضافة المجموعات إلى التحكم الرئيسي
        controls_layout.addLayout(date_group)
        controls_layout.addStretch()
        
        # أزرار التحكم
        self.btn_refresh_stock = QPushButton("تحديث البيانات")
        self.btn_refresh_stock.clicked.connect(self.load_stock_data)
        self.btn_refresh_stock.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        controls_layout.addWidget(self.btn_refresh_stock)
        
        layout.addLayout(controls_layout)

        # جدول المخزون
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels(["الكود", "اسم المنتج", "الكمية", "الوزن (كجم)", "حد التنبيه", "الحالة"])
        
        # تنسيق الجدول
        self.stock_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 10px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eeeeee;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # تمكين التناوب في لون الصفوف
        self.stock_table.setAlternatingRowColors(True)
        
        # تمديد الجدول ليملأ المساحة المتاحة
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # تعيين الحد الأدنى لارتفاع الصفوف
        self.stock_table.verticalHeader().setDefaultSectionSize(40)
        
        # إخفاء أرقام الصفوف
        self.stock_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.stock_table)
        widget.setLayout(layout)
        return widget

    def create_popular_products_report(self):
        """إنشاء تقرير المنتجات الأكثر مبيعاً"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # عنوان التقرير
        title = QLabel("المنتجات الأكثر مبيعاً")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # إضافة التحكم في التاريخ
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)  # المسافة بين عناصر التحكم
        
        # حقول التاريخ
        date_group = QHBoxLayout()
        date_group.addWidget(QLabel("من تاريخ:"))
        self.popular_start_date = QLineEdit()
        self.popular_start_date.setPlaceholderText("YYYY-MM-DD")
        self.popular_start_date.setText(self.default_start_date)
        self.popular_start_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_group.addWidget(self.popular_start_date)
        
        date_group.addWidget(QLabel("إلى تاريخ:"))
        self.popular_end_date = QLineEdit()
        self.popular_end_date.setPlaceholderText("YYYY-MM-DD")
        self.popular_end_date.setText(self.default_end_date)
        self.popular_end_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_group.addWidget(self.popular_end_date)
        
        # إضافة المجموعات إلى التحكم الرئيسي
        controls_layout.addLayout(date_group)
        controls_layout.addStretch()
        
        # زر التحديث
        self.btn_refresh_popular = QPushButton("تحديث البيانات")
        self.btn_refresh_popular.clicked.connect(self.load_popular_products)
        self.btn_refresh_popular.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        controls_layout.addWidget(self.btn_refresh_popular)
        
        layout.addLayout(controls_layout)
        
        # جدول المنتجات
        self.popular_products_table = QTableWidget()
        self.popular_products_table.setColumnCount(6)
        self.popular_products_table.setHorizontalHeaderLabels([
            "كود المنتج", "اسم المنتج", "عدد المبيعات",
            "إجمالي المبيعات", "إجمالي الربح", " الربح للوحدة"
        ])
        self.style_table(self.popular_products_table)
        layout.addWidget(self.popular_products_table)
        
        widget.setLayout(layout)
        return widget

    def create_low_demand_products_report(self):
        """إنشاء تقرير المنتجات الأقل مبيعاً"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # عنوان التقرير
        title = QLabel("المنتجات الأقل مبيعاً")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # إضافة التحكم في التاريخ
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)  # المسافة بين عناصر التحكم
        
        # حقول التاريخ
        date_group = QHBoxLayout()
        date_group.addWidget(QLabel("من تاريخ:"))
        self.low_demand_start_date = QLineEdit()
        self.low_demand_start_date.setPlaceholderText("YYYY-MM-DD")
        self.low_demand_start_date.setText(self.default_start_date)
        self.low_demand_start_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_group.addWidget(self.low_demand_start_date)
        
        date_group.addWidget(QLabel("إلى تاريخ:"))
        self.low_demand_end_date = QLineEdit()
        self.low_demand_end_date.setPlaceholderText("YYYY-MM-DD")
        self.low_demand_end_date.setText(self.default_end_date)
        self.low_demand_end_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_group.addWidget(self.low_demand_end_date)
        
        # إضافة المجموعات إلى التحكم الرئيسي
        controls_layout.addLayout(date_group)
        controls_layout.addStretch()
        
        # زر التحديث
        self.btn_refresh_low_demand = QPushButton("تحديث البيانات")
        self.btn_refresh_low_demand.clicked.connect(self.load_low_demand_products)
        self.btn_refresh_low_demand.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        controls_layout.addWidget(self.btn_refresh_low_demand)
        
        layout.addLayout(controls_layout)
        
        # جدول المنتجات
        self.low_demand_table = QTableWidget()
        self.low_demand_table.setColumnCount(7)
        self.low_demand_table.setHorizontalHeaderLabels([
            "كود المنتج", "اسم المنتج", "عدد المبيعات",
            "إجمالي المبيعات", "إجمالي الربح", "الربح للوحدة", "عدد مرات البيع"
        ])
        self.style_table(self.low_demand_table)
        layout.addWidget(self.low_demand_table)
        
        widget.setLayout(layout)
        return widget

    def create_cash_drawer_report(self):
        """إنشاء تقرير سجل تسليم وتسلم الدرج"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # عنوان التقرير
        title = QLabel("سجل تسليم وتسلم الدرج")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # التحكم في التاريخ
        date_controls = QHBoxLayout()
        date_controls.addWidget(QLabel("من تاريخ:"))
        
        self.cash_drawer_start_date = QLineEdit()
        self.cash_drawer_start_date.setPlaceholderText("YYYY-MM-DD")
        self.cash_drawer_start_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_controls.addWidget(self.cash_drawer_start_date)
        
        date_controls.addWidget(QLabel("إلى تاريخ:"))
        self.cash_drawer_end_date = QLineEdit()
        self.cash_drawer_end_date.setPlaceholderText("YYYY-MM-DD")
        self.cash_drawer_end_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_controls.addWidget(self.cash_drawer_end_date)
        
        self.btn_refresh_cash_drawer = QPushButton("تحديث البيانات")
        self.btn_refresh_cash_drawer.clicked.connect(self.load_cash_drawer_report)
        self.btn_refresh_cash_drawer.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        date_controls.addWidget(self.btn_refresh_cash_drawer)
        
        # إضافة مساحة مرنة لمحاذاة العناصر
        date_controls.addStretch()
        
        layout.addLayout(date_controls)
        
        # إضافة ملخص عمليات تسليم الدرج
        summary_layout = QHBoxLayout()
        
        self.cash_drawer_summary = QLabel("إجمالي عمليات التسليم: 0")
        self.cash_drawer_summary.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        self.cash_drawer_summary.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.cash_drawer_summary)
        
        layout.addLayout(summary_layout)
        
        # جدول سجل تسليم وتسلم الدرج
        self.cash_drawer_table = QTableWidget()
        self.cash_drawer_table.setColumnCount(7)
        self.cash_drawer_table.setHorizontalHeaderLabels([
            "رقم العملية", "التاريخ", "الوقت", "المُسلم", "المُستلم", "المبلغ", "ملاحظات"
        ])
        
        # تنسيق الجدول
        self.style_table(self.cash_drawer_table)
        
        # ضبط عرض الأعمدة
        header = self.cash_drawer_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
            
        layout.addWidget(self.cash_drawer_table)
        
        widget.setLayout(layout)
        return widget

    def create_users_report(self):
        """إنشاء تقرير المستخدمين"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # عنوان التقرير
        title = QLabel("👥 سجل المستخدمين")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
            margin-bottom: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # جدول المستخدمين
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["اسم المستخدم", "الصلاحية", "تاريخ الإنشاء", "أيام العمل", "ساعة البداية", "ساعة النهاية"])
        
        # تنسيق الجدول
        self.style_table(self.users_table)
        
        # تعيين عرض الأعمدة
        self.users_table.setColumnWidth(0, 150)  # اسم المستخدم
        self.users_table.setColumnWidth(1, 120)  # الصلاحية
        self.users_table.setColumnWidth(2, 200)  # تاريخ الإنشاء
        self.users_table.setColumnWidth(3, 300)  # أيام العمل
        self.users_table.setColumnWidth(4, 100)  # ساعة البداية
        self.users_table.setColumnWidth(5, 100)  # ساعة النهاية
        
        layout.addWidget(self.users_table)
        
        # إضافة ملاحظة توضيحية
        note = QLabel("ملاحظة: يعرض هذا التقرير جميع المستخدمين المسجلين في النظام وبيانات جداول العمل الخاصة بهم")
        note.setStyleSheet("""
            font-style: italic;
            color: #7f8c8d;
            padding: 5px;
            font-size: 14px;
        """)
        note.setAlignment(Qt.AlignRight)
        layout.addWidget(note)
        
        widget.setLayout(layout)
        return widget

    def create_attendance_report(self):
        """إنشاء تقرير الحضور والانصراف"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # عنوان التقرير
        title = QLabel("🕒 سجل الحضور والانصراف")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
            margin-bottom: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # التحكم في التاريخ
        date_controls = QHBoxLayout()
        date_controls.addWidget(QLabel("من تاريخ:"))
        
        self.attendance_start_date = QLineEdit()
        self.attendance_start_date.setPlaceholderText("YYYY-MM-DD")
        self.attendance_start_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_controls.addWidget(self.attendance_start_date)
        
        date_controls.addWidget(QLabel("إلى تاريخ:"))
        self.attendance_end_date = QLineEdit()
        self.attendance_end_date.setPlaceholderText("YYYY-MM-DD")
        self.attendance_end_date.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
        """)
        date_controls.addWidget(self.attendance_end_date)
        
        self.btn_refresh_attendance = QPushButton("تحديث البيانات")
        self.btn_refresh_attendance.clicked.connect(self.load_attendance_report)
        self.btn_refresh_attendance.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        date_controls.addWidget(self.btn_refresh_attendance)
        
        # إضافة مساحة مرنة لمحاذاة العناصر
        date_controls.addStretch()
        
        layout.addLayout(date_controls)
        
        # جدول سجل الحضور والانصراف
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(7)
        self.attendance_table.setHorizontalHeaderLabels([
            "اسم المستخدم", "الصلاحية", "التاريخ", "وقت الحضور", "وقت الانصراف", "مدة العمل", "الحالة"
        ])
        
        # تنسيق الجدول
        self.style_table(self.attendance_table)
        
        # تعيين عرض الأعمدة
        self.attendance_table.setColumnWidth(0, 150)  # اسم المستخدم
        self.attendance_table.setColumnWidth(1, 100)  # الصلاحية
        self.attendance_table.setColumnWidth(2, 120)  # التاريخ
        self.attendance_table.setColumnWidth(3, 120)  # وقت الحضور
        self.attendance_table.setColumnWidth(4, 120)  # وقت الانصراف
        self.attendance_table.setColumnWidth(5, 120)  # مدة العمل
        self.attendance_table.setColumnWidth(6, 120)  # الحالة
        
        layout.addWidget(self.attendance_table)
        
        # إضافة ملاحظة توضيحية
        note = QLabel("ملاحظة: يعرض هذا التقرير سجل الحضور والانصراف للموظفين ومدة العمل الفعلية")
        note.setStyleSheet("""
            font-style: italic;
            color: #7f8c8d;
            padding: 5px;
            font-size: 14px;
        """)
        note.setAlignment(Qt.AlignRight)
        layout.addWidget(note)
        
        widget.setLayout(layout)
        return widget

    def load_initial_data(self):
        """تحميل البيانات الأولية عند فتح النافذة"""
        try:
            # تعيين التواريخ الافتراضية في جميع حقول التاريخ
            current_date = QDate.currentDate()
            
            # تقرير المبيعات
            self.start_date_text.setText(self.default_start_date)
            self.end_date_text.setText(self.default_end_date)
            
            # تقرير المخزون
            self.stock_start_date.setText(self.default_start_date)
            self.stock_end_date.setText(self.default_end_date)
            
            # تقرير المنتجات الأكثر مبيعاً
            self.popular_start_date.setText(self.default_start_date)
            self.popular_end_date.setText(self.default_end_date)
            
            # تقرير المنتجات الأقل مبيعاً
            self.low_demand_start_date.setText(self.default_start_date)
            self.low_demand_end_date.setText(self.default_end_date)
            
            # تقرير تسليم وتسلم الدرج
            self.cash_drawer_start_date.setText(self.default_start_date)
            self.cash_drawer_end_date.setText(self.default_end_date)
            
            # تقرير الحضور والانصراف
            self.attendance_start_date.setText(self.default_start_date)
            self.attendance_end_date.setText(self.default_end_date)
            
            # تحميل بيانات التقرير الحالي
            current_index = self.stacked_widget.currentIndex()
            self.show_report(current_index)
            
            # تحميل بيانات المستخدمين مسبقاً
            self.load_users_report()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات الأولية: {str(e)}")

    def load_sales_data(self):
        """تحميل بيانات المبيعات"""
        try:
            start_date = self.start_date_text.text().strip()
            end_date = self.end_date_text.text().strip()
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "تنبيه", "برجاء إدخال التاريخ")
                return
            
            # تحميل البيانات من قاعدة البيانات
            self.sales_table.setRowCount(0)  # مسح البيانات القديمة
            
            result = db.get_invoices_by_date_range(start_date, end_date)
            if not result['invoices']:
                self.sales_summary.setText("إجمالي المبيعات: 0.00 ج")
                self.profit_summary.setText("إجمالي الربح: 0.00 ج")
                return
                
            self.sales_table.setRowCount(len(result['invoices']))
            
            for row, invoice in enumerate(result['invoices']):
                invoice_id, date, customer_id, cashier, total, discount, net_total, profit = invoice
                
                # تحويل القيم إلى أرقام
                try:
                    total = float(total or 0)
                    discount = float(discount or 0)
                    net_total = float(net_total or 0)
                    profit = float(profit or 0)
                except (ValueError, TypeError):
                    continue
                
                # إضافة البيانات للجدول
                self.sales_table.setItem(row, 0, self.create_table_item(str(invoice_id)))
                self.sales_table.setItem(row, 1, self.create_table_item(str(date)))
                self.sales_table.setItem(row, 2, self.create_table_item(str(customer_id) if customer_id else "-"))
                self.sales_table.setItem(row, 3, self.create_table_item(f"{total:.2f}"))
                self.sales_table.setItem(row, 4, self.create_table_item(f"{discount:.2f}"))
                self.sales_table.setItem(row, 5, self.create_table_item(f"{net_total:.2f}"))
                self.sales_table.setItem(row, 6, self.create_table_item(f"{profit:.2f}"))
                
                # تلوين خلية الربح باللون الأخضر
                profit_item = self.sales_table.item(row, 6)
                if profit_item:
                    profit_item.setForeground(Qt.darkGreen)
            
            # تحديث ملخص المبيعات والأرباح
            self.sales_summary.setText(f"إجمالي المبيعات: {result['total_sales']:.2f} ج")
            self.profit_summary.setText(f"إجمالي الربح: {result['total_profit']:.2f} ج")
            
        except Exception as e:
            print(f"Error in load_sales_data: {str(e)}")  # للتشخيص
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات: {str(e)}")
            self.sales_table.setRowCount(0)
            self.sales_summary.setText("إجمالي المبيعات: 0.00 ج")
            self.profit_summary.setText("إجمالي الربح: 0.00 ج")

    def load_stock_data(self):
        """تحميل بيانات المخزون مع مراعاة نوع البيع (كمية/وزن/كلاهما)"""
        try:
            # الحصول على المنتجات من قاعدة البيانات
            db.cursor.execute("""
                SELECT code, name, price, purchase_price, quantity, weight, sell_by, price_type, safe_limit 
                FROM products
                ORDER BY name
            """)
            products = db.cursor.fetchall()
            
            if not products:
                QMessageBox.warning(self, "تنبيه", "لا توجد منتجات في المخزون")
                return
                
            self.stock_table.setRowCount(0)
            row = 0
            
            for product in products:
                try:
                    # استخراج البيانات من المنتج
                    code = str(product[0])
                    name = str(product[1])
                    quantity = float(product[4]) if product[4] is not None else 0
                    weight = float(product[5]) if product[5] is not None else 0.0
                    sell_by = str(product[6]) if product[6] is not None else 'quantity'
                    safe_limit = float(product[8]) if product[8] is not None else 0
                    
                    # تحضير عرض الكمية والوزن حسب نوع البيع
                    quantity_display = str(int(quantity)) if sell_by in ['quantity', 'both'] else "-"
                    weight_display = f"{weight:.3f}" if sell_by in ['weight', 'both'] else "-"
                    
                    # تحديد الحالة بناءً على نوع البيع والحد الأمن
                    status = "🟢 آمن"
                    
                    if sell_by == 'quantity':
                        if quantity <= safe_limit:
                            status = "🔴 تنبيه - الكمية منخفضة"
                    elif sell_by == 'weight':
                        if weight <= safe_limit:
                            status = "🔴 تنبيه - الوزن منخفض"
                    elif sell_by == 'both':
                        if quantity <= safe_limit and weight <= safe_limit:
                            status = "🔴 تنبيه - الكمية والوزن منخفضان"
                        elif quantity <= safe_limit:
                            status = "🔴 تنبيه - الكمية منخفضة"
                        elif weight <= safe_limit:
                            status = "🔴 تنبيه - الوزن منخفض"
                    
                    # إضافة الصف للجدول
                    self.stock_table.insertRow(row)
                    
                    # إنشاء وتنسيق عناصر الجدول
                    items = [
                        (code, Qt.AlignCenter),
                        (name, Qt.AlignRight | Qt.AlignVCenter),
                        (quantity_display, Qt.AlignCenter),
                        (weight_display, Qt.AlignCenter),
                        (str(int(safe_limit)), Qt.AlignCenter),
                        (status, Qt.AlignRight | Qt.AlignVCenter)
                    ]
                    
                    for col, (text, alignment) in enumerate(items):
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(alignment)
                        
                        # تنسيق خاص للحالة
                        if col == 5:  # عمود الحالة
                            if "🔴" in text:
                                item.setForeground(Qt.red)
                            elif "🟢" in text:
                                item.setForeground(Qt.darkGreen)
                        
                        self.stock_table.setItem(row, col, item)
                    
                    row += 1
                        
                except (ValueError, TypeError, IndexError) as e:
                    print(f"خطأ في تحويل البيانات للمنتج {product}: {str(e)}")
                    continue
            
            # تحديث عرض الجدول
            self.stock_table.resizeColumnsToContents()
            for col in range(self.stock_table.columnCount()):
                width = self.stock_table.columnWidth(col)
                self.stock_table.setColumnWidth(col, width + 20)  # إضافة مساحة إضافية
                
        except Exception as e:
            print(f"خطأ في تحميل بيانات المخزون: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المخزون:\n{str(e)}")

    def load_all_stock_data(self):
        """تحميل كل بيانات المخزون"""
        self.load_stock_data()

    def load_popular_products(self):
        """تحميل بيانات المنتجات الأكثر مبيعاً"""
        try:
            start_date = self.popular_start_date.text()
            end_date = self.popular_end_date.text()
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "تنبيه", "الرجاء إدخال التاريخ")
                return
            
            # تحميل المنتجات الأكثر مبيعاً
            top_products = db.get_top_products(
                start_date=start_date,
                end_date=end_date,
                min_quantity=50,    # الحد الأدنى للكمية
                min_weight=100,     # الحد الأدنى للوزن
                min_sales=500       # الحد الأدنى لإجمالي المبيعات
            )
            
            # تحميل المنتجات الأقل مبيعاً
            low_products = db.get_low_selling_products(
                start_date=start_date,
                end_date=end_date,
                min_quantity=50,
                min_weight=100,
                min_sales=500
            )
            
            # عرض المنتجات الأكثر مبيعاً
            self.popular_products_table.setRowCount(len(top_products))
            for row, product in enumerate(top_products):
                code, name, sell_by, quantity, weight, total_sales, total_profit = product
                
                # تحديد الكمية المباعة حسب نوع البيع
                total_sold = weight if sell_by == 'weight' else quantity
                avg_profit = total_profit / total_sold if total_sold > 0 else 0
                
                self.popular_products_table.setItem(row, 0, self.create_table_item(str(code)))
                self.popular_products_table.setItem(row, 1, self.create_table_item(str(name)))
                self.popular_products_table.setItem(row, 2, self.create_table_item(str(total_sold)))
                self.popular_products_table.setItem(row, 3, self.create_table_item(f"{total_sales:.2f}"))
                self.popular_products_table.setItem(row, 4, self.create_table_item(f"{total_profit:.2f}"))
                self.popular_products_table.setItem(row, 5, self.create_table_item(f"{avg_profit:.2f}"))
                
                # تلوين خلايا الربح باللون الأخضر
                for col in [4, 5]:
                    item = self.popular_products_table.item(row, col)
                    item.setForeground(Qt.darkGreen)
            
            # عرض المنتجات الأقل مبيعاً
            self.low_demand_table.setRowCount(len(low_products))
            for row, product in enumerate(low_products):
                code, name, sell_by, quantity, weight, total_sales, total_profit, sales_count = product
                # تحديد الكمية المباعة حسب نوع البيع
                total_sold = weight if sell_by == 'weight' else quantity
                avg_profit = total_profit / total_sold if total_sold > 0 else 0
                self.low_demand_table.setItem(row, 0, self.create_table_item(str(code)))
                self.low_demand_table.setItem(row, 1, self.create_table_item(str(name)))
                self.low_demand_table.setItem(row, 2, self.create_table_item(str(total_sold)))
                self.low_demand_table.setItem(row, 3, self.create_table_item(f"{total_sales:.2f}"))
                self.low_demand_table.setItem(row, 4, self.create_table_item(f"{total_profit:.2f}"))
                self.low_demand_table.setItem(row, 5, self.create_table_item(f"{avg_profit:.2f}"))
                self.low_demand_table.setItem(row, 6, self.create_table_item(str(sales_count)))
                # تلوين خلية الربح باللون الأخضر إذا كان موجب، وباللون الأحمر إذا كان سالب
                profit_item = self.low_demand_table.item(row, 4)
                avg_profit_item = self.low_demand_table.item(row, 5)
                if total_profit >= 0:
                    profit_item.setForeground(Qt.darkGreen)
                    avg_profit_item.setForeground(Qt.darkGreen)
                else:
                    profit_item.setForeground(Qt.red)
                    avg_profit_item.setForeground(Qt.red)
                
        except Exception as e:
            print(f"Error in load_popular_products: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات: {str(e)}")
            self.popular_products_table.setRowCount(0)
            self.low_demand_table.setRowCount(0)

    def load_low_demand_products(self):
        """تحميل بيانات المنتجات الأقل مبيعاً"""
        try:
            start_date = self.low_demand_start_date.text()
            end_date = self.low_demand_end_date.text()
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "تنبيه", "الرجاء إدخال التاريخ")
                return
            
            # تحميل المنتجات الأقل مبيعاً
            low_products = db.get_low_selling_products(
                start_date=start_date,
                end_date=end_date,
                min_quantity=50,    # الحد الأدنى للكمية
                min_weight=100,     # الحد الأدنى للوزن
                min_sales=500       # الحد الأدنى لإجمالي المبيعات
            )
            
            self.low_demand_table.setRowCount(len(low_products))
            
            for row, product in enumerate(low_products):
                code, name, sell_by, quantity, weight, total_sales, total_profit, sales_count = product
                # تحديد الكمية المباعة حسب نوع البيع
                total_sold = weight if sell_by == 'weight' else quantity
                avg_profit = total_profit / total_sold if total_sold > 0 else 0
                self.low_demand_table.setItem(row, 0, self.create_table_item(str(code)))
                self.low_demand_table.setItem(row, 1, self.create_table_item(str(name)))
                self.low_demand_table.setItem(row, 2, self.create_table_item(str(total_sold)))
                self.low_demand_table.setItem(row, 3, self.create_table_item(f"{total_sales:.2f}"))
                self.low_demand_table.setItem(row, 4, self.create_table_item(f"{total_profit:.2f}"))
                self.low_demand_table.setItem(row, 5, self.create_table_item(f"{avg_profit:.2f}"))
                self.low_demand_table.setItem(row, 6, self.create_table_item(str(sales_count)))
                # تلوين خلية الربح باللون الأخضر إذا كان موجب، وباللون الأحمر إذا كان سالب
                profit_item = self.low_demand_table.item(row, 4)
                avg_profit_item = self.low_demand_table.item(row, 5)
                if total_profit >= 0:
                    profit_item.setForeground(Qt.darkGreen)
                    avg_profit_item.setForeground(Qt.darkGreen)
                else:
                    profit_item.setForeground(Qt.red)
                    avg_profit_item.setForeground(Qt.red)
                
        except Exception as e:
            print(f"Error in load_low_demand_products: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات: {str(e)}")
            self.low_demand_table.setRowCount(0)

    def load_cash_drawer_report(self):
        """تحميل بيانات سجل تسليم وتسلم الدرج"""
        try:
            # الحصول على نطاق التاريخ
            start_date = self.cash_drawer_start_date.text()
            end_date = self.cash_drawer_end_date.text()
            
            # التحقق من صحة التواريخ
            if not start_date or not end_date:
                QMessageBox.warning(self, "تحذير", "يرجى تحديد نطاق التاريخ")
                return
                
            # الحصول على بيانات تسليم الدرج
            handovers = db.get_cash_drawer_handovers(start_date, end_date)
            
            # عرض عدد العمليات
            self.cash_drawer_summary.setText(f"إجمالي عمليات التسليم: {len(handovers)}")
            
            # تحديث الجدول
            self.cash_drawer_table.setRowCount(0)
            
            # إضافة الصفوف إلى الجدول
            for row, handover in enumerate(handovers):
                self.cash_drawer_table.insertRow(row)
                
                id_item = self.create_table_item(str(handover[0]))
                date_item = self.create_table_item(handover[1])
                time_item = self.create_table_item(handover[2])
                delivered_by_item = self.create_table_item(handover[3])
                received_by_item = self.create_table_item(handover[4])
                amount_item = self.create_table_item(f"{handover[5]:.2f}")
                notes_item = self.create_table_item(handover[6] if handover[6] else "")
                
                # تلوين المبلغ باللون الأخضر
                amount_item.setForeground(Qt.darkGreen)
                
                self.cash_drawer_table.setItem(row, 0, id_item)
                self.cash_drawer_table.setItem(row, 1, date_item)
                self.cash_drawer_table.setItem(row, 2, time_item)
                self.cash_drawer_table.setItem(row, 3, delivered_by_item)
                self.cash_drawer_table.setItem(row, 4, received_by_item)
                self.cash_drawer_table.setItem(row, 5, amount_item)
                self.cash_drawer_table.setItem(row, 6, notes_item)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل بيانات تسليم الدرج: {str(e)}")

    def load_users_report(self):
        """تحميل بيانات المستخدمين"""
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
                
                # إنشاء عناصر الجدول
                username_item = self.create_table_item(username)
                
                role_text = "مشرف" if role == "admin" else "كاشير"
                role_item = self.create_table_item(role_text)
                if role == "admin":
                    role_item.setForeground(Qt.darkGreen)
                else:
                    role_item.setForeground(Qt.blue)
                
                date_item = self.create_table_item(date)
                work_days_item = self.create_table_item(work_days)
                start_hour_item = self.create_table_item(start_hour)
                end_hour_item = self.create_table_item(end_hour)
                
                # إضافة العناصر إلى الجدول
                self.users_table.setItem(row, 0, username_item)
                self.users_table.setItem(row, 1, role_item)
                self.users_table.setItem(row, 2, date_item)
                self.users_table.setItem(row, 3, work_days_item)
                self.users_table.setItem(row, 4, start_hour_item)
                self.users_table.setItem(row, 5, end_hour_item)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل بيانات المستخدمين: {str(e)}")

    def load_attendance_report(self):
        """تحميل بيانات سجل الحضور والانصراف"""
        try:
            start_date = self.attendance_start_date.text().strip()
            end_date = self.attendance_end_date.text().strip()
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "تنبيه", "برجاء إدخال التاريخ")
                return
                
            # الحصول على بيانات الحضور والانصراف
            attendance_records = db.get_attendance_report(start_date, end_date)
            
            # تحديث الجدول
            self.attendance_table.setRowCount(0)
            
            # إضافة الصفوف إلى الجدول
            for row, record in enumerate(attendance_records):
                self.attendance_table.insertRow(row)
                
                username = record[1]
                date = record[2]
                check_in_time = record[3] if record[3] else "لم يسجل"
                check_out_time = record[4] if record[4] else "لم يسجل"
                status = record[5]
                role = record[7]
                
                # الحصول على أوقات العمل المحددة للمستخدم
                user_data = db.get_user_schedule(username)
                if user_data:
                    expected_start_hour = user_data[0]
                    expected_end_hour = user_data[1]
                else:
                    expected_start_hour = "08:00"
                    expected_end_hour = "20:00"
                
                # حساب مدة العمل
                work_duration = "غير مكتمل"
                if check_in_time != "لم يسجل" and check_out_time != "لم يسجل":
                    try:
                        from datetime import datetime
                        format_str = "%H:%M:%S"
                        check_in = datetime.strptime(check_in_time, format_str)
                        check_out = datetime.strptime(check_out_time, format_str)
                        duration = check_out - check_in
                        hours, remainder = divmod(duration.seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        work_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    except Exception as e:
                        print(f"خطأ في حساب مدة العمل: {str(e)}")
                        work_duration = "خطأ في الحساب"
                
                # إنشاء عناصر الجدول
                username_item = self.create_table_item(username)
                
                role_text = "مشرف" if role == "admin" else "كاشير"
                role_item = self.create_table_item(role_text)
                if role == "admin":
                    role_item.setForeground(Qt.darkGreen)
                else:
                    role_item.setForeground(Qt.blue)
                
                date_item = self.create_table_item(date)
                check_in_item = self.create_table_item(check_in_time)
                check_out_item = self.create_table_item(check_out_time)
                duration_item = self.create_table_item(work_duration)
                
                # تحديد حالة الحضور والانصراف
                status_text = "حاضر" if status == "present" else status
                status_item = self.create_table_item(status_text)
                
                # مقارنة أوقات الحضور والانصراف مع أوقات العمل المحددة
                if check_in_time != "لم يسجل" and check_out_time != "لم يسجل":
                    try:
                        # تحويل الأوقات إلى كائنات datetime للمقارنة
                        format_str = "%H:%M:%S"
                        format_expected = "%H:%M"
                        
                        check_in = datetime.strptime(check_in_time, format_str)
                        check_out = datetime.strptime(check_out_time, format_str)
                        expected_start = datetime.strptime(expected_start_hour, format_expected)
                        expected_end = datetime.strptime(expected_end_hour, format_expected)
                        
                        # حساب الفرق بالدقائق
                        late_minutes = (check_in.hour - expected_start.hour) * 60 + (check_in.minute - expected_start.minute)
                        early_minutes = (expected_end.hour - check_out.hour) * 60 + (expected_end.minute - check_out.minute)
                        
                        if late_minutes > 10:
                            # تنسيق عرض التأخير (بالساعات إذا تجاوز 59 دقيقة)
                            if late_minutes >= 60:
                                late_hours = late_minutes // 60
                                late_mins = late_minutes % 60
                                status_text = f"متأخر {late_hours} ساعة و {late_mins} دقيقة"
                            else:
                                status_text = f"متأخر {late_minutes} دقيقة"
                            status_item.setForeground(Qt.red)
                        elif early_minutes > 10:
                            # تنسيق عرض الانصراف المبكر (بالساعات إذا تجاوز 59 دقيقة)
                            if early_minutes >= 60:
                                early_hours = early_minutes // 60
                                early_mins = early_minutes % 60
                                status_text = f"انصراف مبكر {early_hours} ساعة و {early_mins} دقيقة"
                            else:
                                status_text = f"انصراف مبكر {early_minutes} دقيقة"
                            status_item.setForeground(Qt.darkYellow)
                        else:
                            status_text = "مكتمل"
                            status_item.setForeground(Qt.darkGreen)
                        
                        status_item.setText(status_text)
                    except Exception as e:
                        print(f"خطأ في حساب حالة الحضور: {str(e)}")
                        status_item.setText("خطأ في الحساب")
                elif check_in_time == "لم يسجل":
                    status_item.setForeground(Qt.red)
                    status_item.setText("غائب")
                elif check_out_time == "لم يسجل":
                    status_item.setForeground(Qt.red)
                    status_item.setText("لم يسجل الانصراف")
                
                # إضافة العناصر إلى الجدول
                self.attendance_table.setItem(row, 0, username_item)
                self.attendance_table.setItem(row, 1, role_item)
                self.attendance_table.setItem(row, 2, date_item)
                self.attendance_table.setItem(row, 3, check_in_item)
                self.attendance_table.setItem(row, 4, check_out_item)
                self.attendance_table.setItem(row, 5, duration_item)
                self.attendance_table.setItem(row, 6, status_item)
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل بيانات الحضور والانصراف: {str(e)}")

    def style_table(self, table):
        """تنسيق الجدول بشكل موحد ومتناسق"""
        # تنسيق الجدول الرئيسي
        table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                alternate-background-color: #f8f9fa;
                gridline-color: #dcdde1;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dcdde1;
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
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        # تفعيل الألوان المتناوبة للصفوف
        table.setAlternatingRowColors(True)
        
        # إخفاء رؤوس الصفوف العمودية
        table.verticalHeader().setVisible(False)
        
        # تمديد العمود الأخير ليملأ المساحة المتبقية
        table.horizontalHeader().setStretchLastSection(True)
        
        # ضبط حجم الأعمدة لتتناسب مع المحتوى
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # تعيين الحد الأدنى لعرض الأعمدة
        for i in range(table.columnCount()):
            table.setColumnWidth(i, 150)
        
        # تمكين اختيار الصفوف كاملة
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
        # تمكين الفرز بالنقر على رأس العمود
        table.setSortingEnabled(True)
        
        # ضبط ارتفاع الصفوف
        table.verticalHeader().setDefaultSectionSize(40)
        
        # تعيين المسافة بين الخلايا
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)

    def create_table_item(self, text):
        """إنشاء عنصر جدول مع تنسيق موحد"""
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        # تعيين الخط وحجمه
        font = item.font()
        font.setPointSize(12)
        item.setFont(font)
        return item
        
    def show_invoice_details(self, row, column):
        """عرض تفاصيل الفاتورة"""
        try:
            # التحقق من وجود عنصر في الصف المحدد
            item = self.sales_table.item(row, 0)
            if not item:
                QMessageBox.warning(self, "تنبيه", "لا توجد تفاصيل لهذه الفاتورة")
                return
                
            invoice_id = item.text()
            if not invoice_id:
                QMessageBox.warning(self, "تنبيه", "رقم الفاتورة غير صحيح")
                return

            # Get invoice details including cashier name
            db.cursor.execute("""
                SELECT i.invoice_id, i.date, i.customer_id, i.cashier_username, i.total, i.discount, i.net_total
                FROM invoices i
                WHERE i.invoice_id = ?
            """, (invoice_id,))
            invoice_details = db.cursor.fetchone()
            
            if not invoice_details:
                QMessageBox.warning(self, "تنبيه", "لا توجد معلومات لهذه الفاتورة")
                return
                
            # Get invoice items
            db.cursor.execute("""
                SELECT ii.id, ii.product_code, p.name, ii.price, ii.quantity, ii.weight, ii.total_price, p.sell_by
                FROM invoice_items ii
                LEFT JOIN products p ON ii.product_code = p.code
                WHERE ii.invoice_id = ?
            """, (invoice_id,))
            invoice_items = db.cursor.fetchall()
            
            if not invoice_items:
                QMessageBox.warning(self, "تنبيه", "لا توجد عناصر لهذه الفاتورة")
                return

            # إنشاء نافذة تفاصيل الفاتورة
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"تفاصيل الفاتورة #{invoice_id}")
            details_dialog.setStyleSheet("background-color: #f0f8ff;")
            details_dialog.setMinimumWidth(800)
            details_dialog.setMinimumHeight(600)
            
            dialog_layout = QVBoxLayout()
            
            # عنوان المتجر
            store_header = QLabel("منفذ الشهداء")
            store_header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
            store_header.setAlignment(Qt.AlignCenter)
            dialog_layout.addWidget(store_header)
            
            # معلومات الفاتورة
            date = invoice_details[1] or "-"
            customer = invoice_details[2] if invoice_details[2] not in [None, 'None'] else "-"
            cashier = invoice_details[3] or "غير محدد"
            total = float(invoice_details[4] or 0)
            discount = float(invoice_details[5] or 0)
            net = float(invoice_details[6] or 0)
            
            invoice_info = QLabel(f"""
                <div style='text-align: center;'>
                    <p style='margin: 5px;'>رقم الفاتورة: {invoice_id}</p>
                    <p style='margin: 5px;'>التاريخ: {date}</p>
                    <p style='margin: 5px;'>رقم العميل: {customer}</p>
                    <p style='margin: 5px;'>الكاشير: {cashier}</p>
                </div>
            """)
            invoice_info.setStyleSheet("font-size: 14px; color: #2c3e50;")
            dialog_layout.addWidget(invoice_info)
            
            # جدول المنتجات
            items_table = QTableWidget()
            items_table.setColumnCount(7)
            items_table.setHorizontalHeaderLabels(["م", "المنتج", "الكود", "السعر", "الكمية", "الوزن (كجم)", "الإجمالي"])
            self.style_table(items_table)
            
            items_table.setRowCount(len(invoice_items))
            for i, item in enumerate(invoice_items):
                # تحضير القيم للعرض مع التعامل مع القيم الفارغة
                name = str(item[2] or "-")
                code = str(item[1] or "-")
                price = float(item[3] or 0)
                quantity = item[4] if item[4] is not None else "-"
                weight = f"{float(item[5]):.3f}" if item[5] is not None else "-"
                total_price = float(item[6] or 0)
                
                items = [
                    self.create_table_item(str(i + 1)),
                    self.create_table_item(name),
                    self.create_table_item(code),
                    self.create_table_item(f"{price:.2f} ج"),
                    self.create_table_item(str(quantity)),
                    self.create_table_item(str(weight)),
                    self.create_table_item(f"{total_price:.2f} ج")
                ]
                
                for col, table_item in enumerate(items):
                    items_table.setItem(i, col, table_item)
            
            items_table.resizeColumnsToContents()
            dialog_layout.addWidget(items_table)
            
            # ملخص المبالغ
            totals_info = QLabel(f"""
                <div style='text-align: center;'>
                    <p style='margin: 5px;'>المجموع: {total:.2f} ج</p>
                    <p style='margin: 5px;'>الخصم: {discount:.2f} ج</p>
                    <p style='font-size: 18px; font-weight: bold; color: #e74c3c;'>الصافي: {net:.2f} ج</p>
                </div>
            """)
            totals_info.setStyleSheet("font-size: 16px; color: #2c3e50;")
            dialog_layout.addWidget(totals_info)
            
            # زر الإغلاق
            close_btn = QPushButton("إغلاق")
            close_btn.clicked.connect(details_dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            dialog_layout.addWidget(close_btn)
            
            details_dialog.setLayout(dialog_layout)
            details_dialog.exec_()
            
        except Exception as e:
            print(f"خطأ في عرض تفاصيل الفاتورة: {str(e)}")
            QMessageBox.critical(self, "خطأ", "حدث خطأ أثناء عرض تفاصيل الفاتورة")

    def closeEvent(self, event):
        self.closed_signal.emit()
        super().closeEvent(event)