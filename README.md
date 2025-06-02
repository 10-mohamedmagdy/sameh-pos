# نظام إدارة السوبر ماركت

## متطلبات النظام
- Python 3.8 أو أحدث
- نظام تشغيل Windows 10
- مساحة تخزين كافية (500 ميجابايت على الأقل)
- ذاكرة وصول عشوائي (RAM) 4 جيجابايت على الأقل

## خطوات التثبيت على Windows 10

1. تثبيت Python:
   - قم بتحميل Python من الموقع الرسمي: https://www.python.org/downloads/
   - تأكد من تفعيل خيار "Add Python to PATH" أثناء التثبيت

2. تثبيت المكتبات المطلوبة:
   ```bash
   # تحديث pip أولاً
   python -m pip install --upgrade pip

   # تثبيت المكتبات الأساسية
   pip install -r requirements.txt

   # تثبيت المكتبات الإضافية
   pip install pywin32
   pip install pyinstaller
   pip install win32print
   pip install python-barcode
   pip install Pillow
   pip install reportlab
   pip install arabic-reshaper
   pip install python-bidi
   pip install PyQt5
   pip install PyQt5-tools
   pip install opencv-python
   pip install pyzbar
   pip install python-dateutil
   pip install numpy
   ```

3. تثبيت متطلبات Windows:
   - قم بتثبيت Microsoft Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - قم بتثبيت SQLite: https://www.sqlite.org/download.html

4. التحقق من التثبيت:
   ```bash
   # التحقق من إصدار Python
   python --version

   # التحقق من تثبيت المكتبات
   pip list

   # تشغيل البرنامج
   python main.py
   ```

5. في حالة وجود مشاكل:
   ```bash
   # إعادة تثبيت المكتبات
   pip install --force-reinstall -r requirements.txt

   # تحديث جميع المكتبات
   pip install --upgrade -r requirements.txt

   # مسح ذاكرة التخزين المؤقت وإعادة التثبيت
   pip cache purge
   pip install -r requirements.txt
   ```

## ملاحظات مهمة للتثبيت
1. تأكد من تشغيل موجه الأوامر (Command Prompt) كمسؤول (Run as Administrator)
2. تأكد من تفعيل خيار "Add Python to PATH" أثناء تثبيت Python
3. إذا واجهت مشاكل مع مكتبة معينة، جرب تثبيتها بشكل منفصل
4. تأكد من وجود اتصال بالإنترنت أثناء التثبيت
5. إذا ظهرت أي رسائل خطأ، قم بنسخها والبحث عنها في Google للحصول على حل

## حل المشاكل الشائعة

### مشاكل قاعدة البيانات
- إذا ظهرت رسالة "لم يتم العثور على قاعدة البيانات":
  1. تأكد من وجود ملف `sales_inventory.db` في نفس مجلد البرنامج
  2. تأكد من وجود صلاحيات الكتابة في المجلد
  3. تأكد من عدم استخدام قاعدة البيانات من قبل برنامج آخر

### مشاكل المكتبات
- إذا ظهرت رسالة خطأ تتعلق بمكتبة:
  1. تأكد من تثبيت جميع المكتبات المطلوبة
  2. قم بتشغيل الأمر: `pip install --upgrade -r requirements.txt`
  3. إذا استمرت المشكلة، قم بإعادة تثبيت Python

### مشاكل الواجهة
- إذا لم تظهر الواجهة بشكل صحيح:
  1. تأكد من تثبيت PyQt5 بشكل صحيح
  2. تأكد من تثبيت Microsoft Visual C++ Redistributable
  3. قم بإعادة تشغيل البرنامج

## الدعم الفني
إذا واجهت أي مشاكل، يرجى:
1. قراءة رسائل الخطأ بعناية
2. التأكد من تثبيت جميع المتطلبات
3. التأكد من وجود الصلاحيات المناسبة
4. إعادة تشغيل البرنامج والكمبيوتر 