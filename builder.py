import os

# ---------------------------------------------------------
# بخش اول: تعریف کدهای سایت (تم آبی تیره - نسخه ۵)
# ---------------------------------------------------------

index_html_content = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Tools V5 - Auto Built</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f1f5f9;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }

        h1 {
            color: var(--accent);
            text-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
            margin-bottom: 30px;
            text-align: center;
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 800px;
        }

        .tool-card {
            background-color: var(--card-bg);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            border: 1px solid #334155;
            text-decoration: none;
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 120px;
        }

        .tool-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            border-color: var(--accent);
        }

        .icon {
            font-size: 40px;
            margin-bottom: 10px;
        }

        .status {
            margin-top: 30px;
            font-size: 0.9em;
            color: #94a3b8;
            text-align: center;
        }
        
        .footer-note {
            margin-top: 10px;
            font-size: 0.8em;
            color: #64748b;
        }
    </style>
</head>
<body>

    <h1>🛠️ جعبه ابزار هوشمند</h1>

    <div class="container">
        <!-- ابزار ۱: ضبط صفحه -->
        <a href="#" class="tool-card" onclick="alert('قابلیت ضبط صفحه به زودی فعال می‌شود')">
            <div class="icon">🎥</div>
            <div>ضبط صفحه</div>
        </a>

        <!-- ابزار ۲: دوربین -->
        <a href="camera.html" class="tool-card">
            <div class="icon">📷</div>
            <div>دوربین هوشمند</div>
        </a>

        <!-- ابزار ۳: ضبط صدا -->
        <a href="#" class="tool-card">
            <div class="icon">🎙️</div>
            <div>ضبط صدا</div>
        </a>

        <!-- ابزار ۴: تبدیل فرمت -->
        <a href="#" class="tool-card">
            <div class="icon">🔄</div>
            <div>تبدیل فرمت</div>
        </a>
    </div>

    <div class="status">
        وضعیت سیستم: <span style="color: #4ade80">آنلاین</span> | نسخه ۵.۰
    </div>
    <div class="footer-note">
        ساخته شده توسط Python Builder 🐍
    </div>

</body>
</html>
"""

camera_html_content = """
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دوربین هوشمند</title>
    <style>
        body { background-color: #0f172a; color: white; text-align: center; font-family: sans-serif; }
        video { width: 90%; max-width: 600px; border-radius: 10px; border: 2px solid #3b82f6; margin-top: 20px; }
        button { background-color: #3b82f6; color: white; border: none; padding: 10px 20px; margin-top: 20px; border-radius: 5px; cursor: pointer; }
        a { color: #94a3b8; display: block; margin-top: 20px; text-decoration: none; }
    </style>
</head>
<body>
    <h2>📷 دوربین فعال است</h2>
    <video id="video" autoplay playsinline></video>
    <br>
    <button id="snap">گرفتن عکس</button>
    <canvas id="canvas" style="display:none"></canvas>
    
    <a href="index.html">بازگشت به خانه</a>

    <script>
        const video = document.getElementById('video');
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
                .then(function (stream) {
                    video.srcObject = stream;
                    video.play();
                })
                .catch(function (error) {
                    alert("دسترسی به دوربین داده نشد!");
                });
        }
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# بخش دوم: توابع ساخت فایل (Generator Functions)
# ---------------------------------------------------------

def write_file(filename, content):
    """این تابع محتوا را درون فایل می‌نویسد و اگر فایل وجود نداشته باشد آن را می‌سازد"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ فایل {filename} با موفقیت ساخته/آپدیت شد.")
    except Exception as e:
        print(f"❌ خطا در نوشتن فایل {filename}: {e}")

# ---------------------------------------------------------
# بخش سوم: اجرای اصلی
# ---------------------------------------------------------

def main():
    print("🚀 شروع فرآیند ساخت سایت توسط پایتون...")
    
    # ساختن فایل اصلی
    write_file("index.html", index_html_content)
    
    # ساختن فایل دوربین
    write_file("camera.html", camera_html_content)
    
    print("🎉 تمام فایل‌ها آماده شدند. آماده برای انتشار.")

if __name__ == "__main__":
    main()
