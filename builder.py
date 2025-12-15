import os

# ==========================================
# ⚙️ تنظیمات کارخانه (Factory Settings)
# ==========================================
BASE_DIR = "tools"

def create_tool(folder_name, file_name, content):
    """
    این تابع هوشمند است:
    ۱. بررسی می‌کند پوشه ابزار وجود دارد یا نه.
    ۲. اگر نبود، آن را می‌سازد.
    ۳. فایل را در جای درست ذخیره می‌کند.
    """
    # مسیر کامل: tools/folder_name
    full_folder_path = os.path.join(BASE_DIR, folder_name)
    
    # ساخت پوشه (اگر وجود نداشته باشد)
    os.makedirs(full_folder_path, exist_ok=True)
    
    # مسیر نهایی فایل
    full_file_path = os.path.join(full_folder_path, file_name)
    
    # نوشتن فایل
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ [SUCCESS] Created: {full_file_path}")

# ==========================================
# 🧪 محتوای تستی (برای اطمینان از کارکرد ربات)
# ==========================================
calculator_code = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ماشین حساب تست</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white flex flex-col items-center justify-center h-screen">
    <div class="p-10 border border-gray-700 rounded-xl bg-gray-800 text-center">
        <h1 class="text-3xl text-orange-500 mb-4">ماشین حساب (نسخه ربات)</h1>
        <p class="mb-6">این ابزار به صورت خودکار توسط builder.py در پوشه tools ساخته شد.</p>
        <a href="../../index.html" class="px-4 py-2 bg-blue-600 rounded hover:bg-blue-500">بازگشت به کارخانه</a>
    </div>
</body>
</html>
"""

# ==========================================
# 🚀 شروع عملیات (Main Execution)
# ==========================================
if __name__ == "__main__":
    print("🤖 Robot started working...")
    
    # اطمینان از وجود پوشه اصلی tools
    os.makedirs(BASE_DIR, exist_ok=True)
    
    # دستور ساخت یک ابزار تستی (ماشین حساب)
    create_tool("calculator", "index.html", calculator_code)
    
    print("🏁 Mission Complete.")
