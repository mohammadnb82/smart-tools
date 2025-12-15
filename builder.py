import os
import subprocess
import requests
from datetime import datetime

# --- تنظیمات رنگ و لاگ ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def log(message, level="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if level == "info":
        print(f"{Colors.BLUE}[INFO - {timestamp}] {message}{Colors.ENDC}")
    elif level == "success":
        print(f"{Colors.GREEN}[SUCCESS - {timestamp}] {message}{Colors.ENDC}")
    elif level == "error":
        print(f"{Colors.FAIL}[ERROR - {timestamp}] {message}{Colors.ENDC}")

# --- بخش 1: تولید وب‌سایت (نسخه آبی تیره V5) ---
def create_professional_site():
    log("Starting to build the HTML structure...")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>پنل هوشمند | Smart Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{
                --primary-bg: #0f172a;
                --secondary-bg: #1e293b;
                --accent-color: #38bdf8;
                --text-color: #f1f5f9;
            }}
            body {{
                background-color: var(--primary-bg);
                color: var(--text-color);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .glass-card {{
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }}
            .glass-card:hover {{
                transform: translateY(-5px);
                border-color: var(--accent-color);
            }}
            .status-badge {{
                background-color: rgba(56, 189, 248, 0.2);
                color: var(--accent-color);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
            }}
            .btn-glow {{
                background: linear-gradient(45deg, #0ea5e9, #2563eb);
                border: none;
                color: white;
                box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
            }}
            footer {{
                text-align: center;
                margin-top: 50px;
                padding: 20px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="container py-5">
            <header class="text-center mb-5">
                <h1 class="display-4 fw-bold"><i class="fas fa-robot me-2"></i>سامانه هوشمند نسخه 5.0</h1>
                <p class="lead text-muted">این سایت توسط ربات پایتون در GitHub Actions ساخته شده است</p>
                <div class="mt-3">
                    <span class="status-badge">وضعیت: آنلاین</span>
                    <span class="status-badge ms-2">آخرین آپدیت: {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
                </div>
            </header>

            <div class="row">
                <!-- پنل آمار -->
                <div class="col-md-4">
                    <div class="glass-card text-center">
                        <i class="fas fa-server fa-3x mb-3 text-warning"></i>
                        <h3>سرور بیلد</h3>
                        <p>اجرا شده روی Ubuntu Latest</p>
                        <button class="btn btn-sm btn-outline-light w-100">مشاهده لاگ</button>
                    </div>
                </div>
                
                <!-- پنل دسترسی -->
                <div class="col-md-4">
                    <div class="glass-card text-center">
                        <i class="fas fa-shield-alt fa-3x mb-3 text-success"></i>
                        <h3>سطح دسترسی</h3>
                        <p>God Mode Active</p>
                        <button class="btn btn-sm btn-outline-light w-100">بررسی امنیت</button>
                    </div>
                </div>

                <!-- پنل ابزار -->
                <div class="col-md-4">
                    <div class="glass-card text-center">
                        <i class="fas fa-rocket fa-3x mb-3 text-danger"></i>
                        <h3>دیپلوی خودکار</h3>
                        <p>انتشار همزمان در Dev و Prod</p>
                        <button class="btn btn-sm btn-glow w-100">جزئیات</button>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-12">
                    <div class="glass-card">
                        <h4><i class="fas fa-terminal me-2"></i>گزارش عملیات اخیر</h4>
                        <hr class="border-secondary">
                        <ul class="list-unstyled">
                            <li class="mb-2">✅ دریافت کد از مخزن اصلی</li>
                            <li class="mb-2">✅ نصب کتابخانه‌های Selenium و WebDriver</li>
                            <li class="mb-2">✅ تولید فایل index.html جدید</li>
                            <li class="mb-2 text-info">🚀 در حال ارسال به مخزن دوم (Production)...</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            <small>Powered by Python & GitHub Actions | Auto-Generated</small>
        </footer>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    log("index.html created successfully!", "success")

# --- بخش 2: اتصال به مخزن دوم (God Mode Feature) ---
def deploy_to_external_repo():
    token = os.environ.get('PERSONAL_TOKEN')
    
    # تنظیمات مخزن دوم (اینجا را می‌توانید تغییر دهید)
    # مثلا اگر نام مخزن دوم شما stable-site است
    target_repo_name = "stable-site"  
    # نام کاربری گیت‌هاب شما (به صورت خودکار از محیط گرفته می‌شود یا دستی وارد کنید)
    github_user = os.environ.get('GITHUB_ACTOR') 
    
    if not token:
        log("No PERSONAL_TOKEN found. Skipping external deploy.", "warning")
        return

    log(f"Preparing to deploy to external repo: {target_repo_name}...", "info")

    repo_url = f"https://{github_user}:{token}@github.com/{github_user}/{target_repo_name}.git"
    
    try:
        # 1. تنظیم هویت گیت
        subprocess.run(["git", "config", "--global", "user.email", "bot@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Python Bot"], check=True)
        
        # 2. کلون کردن مخزن دوم
        log("Cloning target repository...")
        if os.path.exists("temp_repo"):
            subprocess.run(["rm", "-rf", "temp_repo"], check=True)
            
        subprocess.run(["git", "clone", repo_url, "temp_repo"], check=True)
        
        # 3. کپی کردن فایل index.html ساخته شده به مخزن دوم
        log("Copying files...")
        subprocess.run(["cp", "index.html", "temp_repo/index.html"], check=True)
        
        # 4. کامیت و پوش
        os.chdir("temp_repo") # رفتن به داخل پوشه مخزن دوم
        subprocess.run(["git", "add", "."], check=True)
        
        # بررسی تغییرات
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", f"Auto-update by Python Bot: {datetime.now()}"], check=True)
            subprocess.run(["git", "push"], check=True)
            log("Successfully deployed to SECOND repository! 🚀", "success")
        else:
            log("No changes detected in second repo.", "info")
            
    except Exception as e:
        log(f"Error in external deploy: {e}", "er")
    finally:
        # برگشتن به مسیر اصلی (اختیاری)
        pass

# --- اجرای اصلی ---
if __name__ == "__main__":
    log("--- PYTHON GOD MODE STARTED ---")
    
    # 1. ساخت سایت
    create_professional_site()e()
