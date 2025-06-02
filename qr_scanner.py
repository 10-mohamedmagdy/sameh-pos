from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QComboBox,
    QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import sys

class QRCodeScanner(QWidget):
    code_detected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ماسح QR Code")
        self.setGeometry(100, 100, 640, 520)
        self.initUI()
        
        self.last_code = ""
        self.last_detection_time = 0
        self.available_cameras = []
        self.current_camera_index = 0
        self.is_scanning = False
        self.cap = None
        
        # Scan for available cameras
        self.scan_for_cameras()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Camera selection controls
        camera_controls = QHBoxLayout()
        
        camera_controls.addWidget(QLabel("اختر الكاميرا:"))
        self.camera_combo = QComboBox()
        camera_controls.addWidget(self.camera_combo)
        
        self.refresh_btn = QPushButton("تحديث الكاميرات")
        self.refresh_btn.clicked.connect(self.scan_for_cameras)
        camera_controls.addWidget(self.refresh_btn)
        
        layout.addLayout(camera_controls)
        
        # Camera view
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        layout.addWidget(self.camera_label)
        
        # Status and controls
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("جاهز للمسح...")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.start_btn = QPushButton("بدء المسح")
        self.start_btn.clicked.connect(self.toggle_scanning)
        self.start_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        status_layout.addWidget(self.start_btn)
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        
        # Timer for video processing
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.setInterval(100)  # Update at 10 FPS to not overwhelm the system
    
    def scan_for_cameras(self):
        """Scan for available cameras including USB devices"""
        self.available_cameras = []
        self.camera_combo.clear()
        
        # Start from -1 to include default camera devices
        # Go up to 10 to catch USB cameras which may be assigned higher numbers
        for i in range(-1, 10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    camera_name = f"Camera {i}" if i >= 0 else "Default Camera"
                    self.available_cameras.append(i)
                    self.camera_combo.addItem(camera_name, i)
                cap.release()
        
        if self.camera_combo.count() > 0:
            # Select the first non-default camera if available
            if self.camera_combo.count() > 1:
                self.camera_combo.setCurrentIndex(1)
            self.status_label.setText(f"تم العثور على {self.camera_combo.count()} كاميرا")
        else:
            self.status_label.setText("لم يتم العثور على كاميرات")
            QMessageBox.warning(self, "تحذير", "لم يتم العثور على أي كاميرا متصلة!")

    def toggle_scanning(self):
        if self.is_scanning:
            self.stop_scanner()
        else:
            self.start_scanner()
    
    def start_scanner(self):
        """Start the QR code scanner"""
        if self.camera_combo.count() == 0:
            QMessageBox.warning(self, "خطأ", "لا توجد كاميرات متاحة!")
            return
        
        self.current_camera_index = self.camera_combo.currentData()
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(self.current_camera_index)
        
        # Configure camera properties for better scanning
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus if available
        
        if not self.cap.isOpened():
            QMessageBox.critical(self, "خطأ", f"لا يمكن فتح الكاميرا {self.current_camera_index}!")
            return
        
        self.is_scanning = True
        self.timer.start()
        self.start_btn.setText("إيقاف المسح")
        self.start_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        self.status_label.setText("جاري المسح...")
    
    def stop_scanner(self):
        """Stop the QR code scanner"""
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        self.is_scanning = False
        self.start_btn.setText("بدء المسح")
        self.start_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        self.status_label.setText("تم إيقاف المسح")
        
        # Clear the camera view
        blank_image = QImage(640, 480, QImage.Format_RGB888)
        blank_image.fill(Qt.black)
        self.camera_label.setPixmap(QPixmap.fromImage(blank_image))
    
    def update_frame(self):
        """Update the camera frame and scan for QR codes"""
        if not self.cap or not self.cap.isOpened():
            self.stop_scanner()
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.status_label.setText("خطأ في قراءة إطار الكاميرا!")
            return
        
        # Convert the frame to grayscale for QR detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Scan for QR codes
        qr_codes = decode(gray)
        
        # Draw rectangles around detected QR codes
        for qr in qr_codes:
            points = qr.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                cv2.polylines(frame, [hull], True, (0, 255, 0), 3)
            else:
                cv2.polylines(frame, [np.array(points)], True, (0, 255, 0), 3)
            
            # Draw QR code data
            code_data = qr.data.decode('utf-8')
            cv2.putText(frame, code_data, (qr.rect.left, qr.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Emit signal with the QR code data
            import time
            current_time = time.time()
            # Only emit if it's a new code or more than 2 seconds have passed
            if code_data != self.last_code or (current_time - self.last_detection_time) > 2:
                self.code_detected.emit(code_data)
                self.last_code = code_data
                self.last_detection_time = current_time
                self.status_label.setText(f"تم المسح: {code_data}")
        
        # Convert the frame to RGB for Qt display
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        # Convert to QImage and display
        image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(image))
    
    def closeEvent(self, event):
        """Clean up resources when the window is closed"""
        self.stop_scanner()
        event.accept()


# Example of how to use this class in a sales window
class SaleWindowWithQRScanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نافذة المبيعات مع ماسح QR")
        self.setGeometry(100, 100, 1200, 800)
        
        self.initUI()
        
        # Initialize QR scanner as a separate window
        self.qr_scanner = QRCodeScanner()
        self.qr_scanner.code_detected.connect(self.handle_scanned_code)
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Add controls to show/hide scanner
        scanner_controls = QHBoxLayout()
        
        self.scanner_btn = QPushButton("فتح ماسح QR")
        self.scanner_btn.clicked.connect(self.toggle_scanner)
        scanner_controls.addWidget(self.scanner_btn)
        
        layout.addLayout(scanner_controls)
        
        # Add a table for shopping cart
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["كود المنتج", "اسم المنتج", "السعر", "الكمية"])
        layout.addWidget(self.cart_table)
        
        self.setLayout(layout)
    
    def toggle_scanner(self):
        if self.qr_scanner.isVisible():
            self.qr_scanner.hide()
            self.scanner_btn.setText("فتح ماسح QR")
        else:
            self.qr_scanner.show()
            self.scanner_btn.setText("إغلاق ماسح QR")
    
    @pyqtSlot(str)
    def handle_scanned_code(self, code):
        # This method will be called when a QR code is scanned
        print(f"تم مسح: {code}")
        
        # Here you would typically:
        # 1. Parse the QR code (assuming it's a product code)
        # 2. Look up the product in the database
        # 3. Add it to the shopping cart
        
        # For demonstration, we'll just add it to the table
        try:
            row_position = self.cart_table.rowCount()
            self.cart_table.insertRow(row_position)
            
            # Set the product code
            self.cart_table.setItem(row_position, 0, QTableWidgetItem(code))
            self.cart_table.setItem(row_position, 1, QTableWidgetItem("منتج من المسح"))
            self.cart_table.setItem(row_position, 2, QTableWidgetItem("0.00"))
            self.cart_table.setItem(row_position, 3, QTableWidgetItem("1"))
            
            QMessageBox.information(self, "تم المسح", f"تمت إضافة المنتج: {code}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"حدث خطأ أثناء إضافة المنتج: {str(e)}")


# For testing only
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SaleWindowWithQRScanner()
    window.show()
    sys.exit(app.exec_())