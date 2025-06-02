from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from database import db

class CustomerManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة العملاء")
        self.setGeometry(300, 300, 600, 400)
        self.initUI()
        self.load_customers()

    def initUI(self):
        layout = QVBoxLayout()

        # عنوان النافذة
        title = QLabel("إدارة العملاء", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # حقول إدخال البيانات
        form_layout = QVBoxLayout()
        
        # اسم العميل
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم العميل")
        form_layout.addWidget(self.name_input)

        # رقم الهاتف
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف")
        form_layout.addWidget(self.phone_input)

        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("إضافة عميل")
        self.add_btn.clicked.connect(self.add_customer)
        buttons_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("تحديث")
        self.update_btn.clicked.connect(self.update_customer)
        self.update_btn.setEnabled(False)
        buttons_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("حذف")
        self.delete_btn.clicked.connect(self.delete_customer)
        self.delete_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_btn)

        self.clear_btn = QPushButton("مسح الحقول")
        self.clear_btn.clicked.connect(self.clear_fields)
        buttons_layout.addWidget(self.clear_btn)

        form_layout.addLayout(buttons_layout)
        layout.addLayout(form_layout)

        # جدول عرض العملاء
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(3)
        self.customers_table.setHorizontalHeaderLabels(["ID", "الاسم", "الهاتف"])
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.cellClicked.connect(self.table_cell_clicked)
        layout.addWidget(self.customers_table)

        self.setLayout(layout)

    def load_customers(self):
        customers = db.get_all_customers()
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer[0])))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer[1]))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer[2] if customer[2] else ""))

    def add_customer(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name:
            QMessageBox.warning(self, "تحذير", "يجب إدخال اسم العميل")
            return

        try:
            db.add_customer(name, phone if phone else None)
            self.load_customers()
            self.clear_fields()
            QMessageBox.information(self, "نجاح", "تم إضافة العميل بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة العميل: {str(e)}")

    def update_customer(self):
        selected_row = self.customers_table.currentRow()
        if selected_row < 0:
            return

        customer_id = int(self.customers_table.item(selected_row, 0).text())
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name:
            QMessageBox.warning(self, "تحذير", "يجب إدخال اسم العميل")
            return

        try:
            # في SQLite، سنحتاج إلى تنفيذ UPDATE مباشرة
            conn = db.conn
            cursor = conn.cursor()
            cursor.execute("UPDATE customers SET name = ?, phone = ? WHERE id = ?",
                          (name, phone if phone else None, customer_id))
            conn.commit()
            
            self.load_customers()
            self.clear_fields()
            QMessageBox.information(self, "نجاح", "تم تحديث بيانات العميل بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث العميل: {str(e)}")

    def delete_customer(self):
        selected_row = self.customers_table.currentRow()
        if selected_row < 0:
            return

        customer_id = int(self.customers_table.item(selected_row, 0).text())
        
        reply = QMessageBox.question(self, 'تأكيد الحذف', 
                                    'هل أنت متأكد من حذف هذا العميل؟',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = db.conn
                cursor = conn.cursor()
                cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
                conn.commit()
                
                self.load_customers()
                self.clear_fields()
                QMessageBox.information(self, "نجاح", "تم حذف العميل بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف العميل: {str(e)}")

    def table_cell_clicked(self, row, column):
        customer_id = self.customers_table.item(row, 0).text()
        customer_name = self.customers_table.item(row, 1).text()
        customer_phone = self.customers_table.item(row, 2).text() if self.customers_table.item(row, 2) else ""

        self.name_input.setText(customer_name)
        self.phone_input.setText(customer_phone)
        
        self.add_btn.setEnabled(False)
        self.update_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def clear_fields(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.customers_table.clearSelection()
        
        self.add_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)