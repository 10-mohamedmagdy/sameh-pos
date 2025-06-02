# اسم الملف: test_libraries.py
# قم بتشغيل هذا الملف للتحقق من المكتبات

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

print("\nTesting OpenCV:")
try:
    import cv2
    print(f"OpenCV version: {cv2.__version__}")
    print("OpenCV test successful!")
except Exception as e:
    print(f"OpenCV error: {e}")

print("\nTesting NumPy:")
try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
    print("NumPy test successful!")
except Exception as e:
    print(f"NumPy error: {e}")

print("\nTesting PyZbar:")
try:
    from pyzbar.pyzbar import decode
    test_array = np.zeros((100, 100), dtype=np.uint8)
    test_decode = decode(test_array)
    print("PyZbar test successful!")
except Exception as e:
    print(f"PyZbar error: {e}")

print("\nChecking for ZBar library:")
try:
    # Try different import approaches
    try:
        import zbar
        print("zbar imported directly")
    except ImportError:
        try:
            from pyzbar import zbar
            print("zbar imported from pyzbar")
        except ImportError:
            print("Could not import zbar directly")
except Exception as e:
    print(f"ZBar check error: {e}")

print("\nTest complete!")