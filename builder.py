import os
import datetime

# تنظیمات
ROOT_DIR = "."
ASSETS_DIR = "assets"
TOOLS_DIR = "tools"
OUTPUT_FILE = "index.html"

def get_file_list(directory):
    """لیست فایل‌های موجود در یک پوشه را برمی‌گرداند"""
    if not os.path.exists(directory):
        os.makedirs(directory) # اگر پوشه نبود، آن را می‌سازد
        return []
    
    files = []
    for f in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, f)):
            files.append(f)
    return files

def generate_html():
    """تولید کد HTML کامل سایت"""
    
    # دریافت لیست فایل‌ها برای نمایش در سایت
    assets_files = get_file_list(ASSETS_DIR)
    tools_files = get_file_list(TOOLS_DIR)
    
    # زمان بروزرسانی
    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # قالب HTML (طراحی سایت در دل پایتون)
    html_content = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل هوشمند پایتون</title>
    <style>
        body {{
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: Tahoma, sans-serif;
            margin: 0;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #1e293b;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #334155;
        }}
        h1 {{ color: #38bdf8; }}
        .badge {{
            background-color: #22c55e;
            color: black;
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .section {{
            margin-top: 30px;
            text-align: right;
        }}
        .section h3 {{ border-bottom: 1px solid #475569; padding-bottom: 10px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{
            background: #334155;
            margin: 5px 0;
            padding: 10px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
        }}
        a {{ color: #fbbf24; text-decoration: none; }}
        .footer {{ margin-top: 40px; font-size: 0.8em; color: #94a3b8; }}
    </style>
</head>
<body>

    <div class="container">
        <h1>سیستم مانیتورینگ خودکار</h1>
        <span class="badge">وضعیت: آنلاین</span>
        <p>این صفحه توسط پایتون تولید شده است.</p>

        <div class="section">
            <h3>📂 فایل‌های Assets ({len(assets_files)})</h3>
            <ul>
                {''.join([f'<li><a href="{ASSETS_DIR}/{f}">{f}</a></li>' for f in assets_files]) or '<li>خالی</li>'}
            </ul>
        </div>

        <div class="section">
            <h3>🛠 ابزارها ({len(tools_files)})</h3>
            <ul>
                {''.join([f'<li><a href="{TOOLS_DIR}/{f}">{f}</a></li>' for f in tools_files]) or '<li>خالی</li>'}
            </ul>
        </div>

        <div class="footer">
            آخرین اسکن و بروزرسانی:<br>
            {update_time} UTC
        </div>
    </div>

</body>
</html>
    """
    
    # ذخیره فایل
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Site generated successfully at {update_time}")

if __name__ == "__main__":
    generate_html()

