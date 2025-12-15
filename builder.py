import os

def generate_static_index():
    # تنظیمات دکمه‌های خاص (۱ تا ۳)
    special_buttons = {
        1: {
            "title": "دوربین تشخیص حرکت",
            "link": "tools/motion-cam/index.html",
            "icon": "fa-video",
            "status_color": "bg-yellow-500", # وضعیت تست
            "status_dot": True,
            "opacity": "card-active cursor-pointer",
            "text_color": "text-orange-400",
            "sub_text": "/tools/motion-cam"
        },
        2: {
            "title": "دوربین تشخیص انسان",
            "link": "tools/human-detection/index.html", # فرض بر این مسیر
            "icon": "fa-user-secret",
            "status_color": "bg-blue-500", # وضعیت در حال ساخت
            "status_dot": True,
            "opacity": "card-active cursor-pointer",
            "text_color": "text-orange-400",
            "sub_text": "/tools/human-detection"
        },
        3: {
            "title": "ماشین حساب",
            "link": "tools/calculator/index.html",
            "icon": "fa-calculator",
            "status_color": "bg-green-500", # وضعیت پایدار
            "status_dot": True,
            "opacity": "card-active cursor-pointer",
            "text_color": "text-orange-400",
            "sub_text": "/tools/calculator"
        }
    }

    # شروع ساخت محتوای HTML
    html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کارخانه ابزار هوشمند | نسخه توسعه</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #1a1a1a; color: #e5e5e5; font-family: 'Segoe UI', Tahoma, sans-serif; }
        .tech-card {
            background: linear-gradient(145deg, #262626, #1f1f1f);
            border: 1px solid #333;
            box-shadow: 5px 5px 10px #141414, -5px -5px 10px #2e2e2e;
            transition: all 0.2s ease;
        }
        .card-active:hover {
            border-color: #f97316;
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba(249, 115, 22, 0.2);
        }
        .card-empty { opacity: 0.4; border-style: dashed; }
        .status-dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; }
    </style>
</head>
<body class="min-h-screen p-6 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]">

    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-center mb-10 border-b border-gray-700 pb-4">
            <div>
                <h1 class="text-3xl font-bold text-orange-500">
                    <i class="fas fa-cogs ml-2"></i>کارخانه ابزارسازی
                </h1>
                <p class="text-gray-500 text-sm mt-1">محیط توسعه و تست ماژولار (Dev Environment)</p>
            </div>
            <div class="bg-gray-800 px-4 py-2 rounded text-xs font-mono text-orange-300">
                STATUS: READY FOR BOT
            </div>
        </header>

        <!-- شبکه ابزارها با ۵۰ دکمه استاتیک -->
        <div id="factory-grid" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
"""

    # حلقه پایتون برای تولید ۵۰ بلاک HTML (نتیجه نهایی در فایل بدون حلقه خواهد بود)
    for i in range(1, 51):
        if i in special_buttons:
            # دکمه‌های ۱، ۲ و ۳
            data = special_buttons[i]
            btn_html = f"""
            <!-- دکمه {i}: {data['title']} -->
            <a href="{data['link']}" id="btn-{i}" class="block h-full group text-decoration-none">
                <div class="tech-card h-32 rounded-lg p-4 relative flex flex-col justify-between {data['opacity']}">
                    <div class="flex justify-between items-start">
                        <i id="icon-{i}" class="fas {data['icon']} text-2xl {data['text_color']}"></i>
                        <span id="status-{i}" class="{data['status_color']} status-dot shadow-lg shadow-current"></span>
                    </div>
                    <div>
                        <h3 id="title-{i}" class="font-bold text-sm text-gray-200">{data['title']}</h3>
                        <p id="path-{i}" class="text-[10px] text-gray-500 font-mono mt-1">{data['sub_text']}</p>
                    </div>
                </div>
            </a>
            """
        else:
            # دکمه‌های خالی (۴ تا ۵۰)
            btn_html = f"""
            <!-- دکمه {i}: خالی -->
            <a href="#" id="btn-{i}" class="block h-full group text-decoration-none">
                <div class="tech-card h-32 rounded-lg p-4 relative flex flex-col justify-between card-empty">
                    <div class="flex justify-between items-start">
                        <i id="icon-{i}" class="fas fa-cube text-2xl text-gray-600"></i>
                        <!-- وضعیت خاموش است -->
                    </div>
                    <div>
                        <h3 id="title-{i}" class="font-bold text-sm text-gray-500">پروژه {i}</h3>
                        <!-- مسیر ندارد -->
                    </div>
                </div>
            </a>
            """
        html_content += btn_html

    # بستن تگ‌ها
    html_content += """
        </div>
    </div>
</body>
</html>
"""

    # ذخیره فایل
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ فایل index.html با موفقیت بازسازی شد.")
    print("✅ ۵۰ دکمه به صورت استاتیک (بدون جاوا اسکریپت) ساخته شدند.")
    print("✅ دکمه‌های ۱ (حرکت)، ۲ (انسان) و ۳ (ماشین حساب) تنظیم شدند.")
    print("✅ اکنون ربات می‌تواند با استفاده از id='btn-X' هر دکمه‌ای را جداگانه ویرایش کند.")

if __name__ == "__main__":
    generate_static_index()
