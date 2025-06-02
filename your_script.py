from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import QSizeF
from PyQt5.QtPrintSupport import QPrinter

import sys

app = QApplication(sys.argv)  # 🔵 لازم Q(A)pplication علشان QPainter/QFont

# إعداد الطابعة
printer = QPrinter(QPrinter.HighResolution)
printer.setPrinterName("XPrinter_POS80")  # تأكد أن الاسم هو نفسه من lpstat -d
printer.setPageSize(QPrinter.Custom)
printer.setPaperSize(QSizeF(80, 297), QPrinter.Millimeter)  # 80mm × A4 طول (أو حسب طول الفاتورة)

# إنشاء الرسام
painter = QPainter()

if painter.begin(printer):
    painter.setFont(QFont("Arial", 12))
    painter.drawText(100, 100, "✅ تمت طباعة الفاتورة بنجاح")
    painter.end()
else:
    print("❌ لم يتم بدء QPainter بشكل صحيح - تأكد من الطابعة")

app.quit()
