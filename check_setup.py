# -*- coding: utf-8 -*-
"""
سكريبت للتحقق من تثبيت المكتبات المطلوبة
Script to verify required libraries installation
"""

import sys

def check_installation():
    """التحقق من تثبيت جميع المكتبات المطلوبة"""
    
    print("=" * 60)
    print("التحقق من تثبيت المكتبات المطلوبة")
    print("Checking required libraries installation")
    print("=" * 60)
    print()
    
    required_packages = [
        ('flask', 'Flask'),
        ('requests', 'Requests'),
        ('moviepy.editor', 'MoviePy'),
        ('PIL', 'Pillow'),
        ('gtts', 'gTTS'),
        ('arabic_reshaper', 'arabic-reshaper'),
        ('bidi.algorithm', 'python-bidi'),
    ]
    
    all_installed = True
    
    for package_name, display_name in required_packages:
        try:
            __import__(package_name)
            print(f"✅ {display_name:20} - مثبت بنجاح / Installed")
        except ImportError:
            print(f"❌ {display_name:20} - غير مثبت / Not Installed")
            all_installed = False
    
    print()
    print("=" * 60)
    
    if all_installed:
        print("✅ جميع المكتبات مثبتة بنجاح!")
        print("✅ All libraries are installed successfully!")
        print()
        print("يمكنك الآن تشغيل التطبيق:")
        print("You can now run the application:")
        print("    python main.py")
    else:
        print("❌ بعض المكتبات غير مثبتة")
        print("❌ Some libraries are not installed")
        print()
        print("قم بتثبيت المكتبات المطلوبة:")
        print("Install required libraries:")
        print("    pip install -r requirements.txt")
    
    print("=" * 60)
    print()
    
    # التحقق من إصدار Python
    print("إصدار Python / Python Version:", sys.version)
    print()
    
    return all_installed


def check_config():
    """التحقق من إعدادات config.py"""
    
    print("=" * 60)
    print("التحقق من الإعدادات")
    print("Checking Configuration")
    print("=" * 60)
    print()
    
    try:
        import config
        
        # التحقق من مفتاح Pexels
        if config.PEXELS_API_KEY == "YOUR_PEXELS_API_KEY_HERE":
            print("⚠️  تحذير: لم يتم تعيين مفتاح Pexels API")
            print("⚠️  Warning: Pexels API key not set")
            print("   الرجاء تعديل ملف config.py وإضافة مفتاحك")
            print("   Please edit config.py and add your API key")
            print("   احصل على مفتاح من: https://www.pexels.com/api/")
        else:
            print("✅ مفتاح Pexels API موجود / Pexels API key is set")
        
        print()
        
        # التحقق من وجود المجلدات
        import os
        folders = ['templates', 'static', 'temp', 'outputs']
        for folder in folders:
            if os.path.exists(folder):
                print(f"✅ المجلد موجود / Folder exists: {folder}/")
            else:
                print(f"⚠️  المجلد غير موجود / Folder missing: {folder}/")
        
        print()
        print("=" * 60)
        
    except ImportError:
        print("❌ خطأ: لا يمكن تحميل ملف config.py")
        print("❌ Error: Cannot load config.py")
    
    print()


if __name__ == "__main__":
    # التحقق من المكتبات
    installed = check_installation()
    
    # التحقق من الإعدادات إذا كانت المكتبات مثبتة
    if installed:
        check_config()
    
    print()
    print("للمساعدة، راجع:")
    print("For help, check:")
    print("  - README.md")
    print("  - QUICKSTART.md")
    print("  - USER_GUIDE.md")
    print()
