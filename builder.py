import os
import shutil
import requests

# --- تنظیمات ---
ASSETS_DIR = "assets"
HTML_OUTPUT = "index.html"

# لیست فایل‌هایی که باید در پوشه assets باشند.
# منطق: اگر فایل در روت پروژه (کنار این اسکریپت) باشد، کپی می‌شود.
# اگر نباشد، از اینترنت دانلود می‌شود.
LIBRARIES = {
    # 1. حیاتی برای گیت‌هاب (حل مشکل امنیتی SharedArrayBuffer)
    "coi-serviceworker.js": "https://cdnjs.cloudflare.com/ajax/libs/coi-serviceworker/0.1.7/coi-serviceworker.min.js",
    
    # 2. کتابخانه‌های هوش مصنوعی (طبق درخواست قبلی)
    "tf.min.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs/dist/tf.min.js",
    "pose-detection.min.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection",
    "coco-ssd.min.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd",
    
    # 3. کتابخانه‌های FFmpeg
    # (لینک‌ها به عنوان Fallback هستند، اگر شما فایل‌ها را در ریپو گذاشته باشید، اولویت با فایل شماست)
    "ffmpeg-lib.js": "https://unpkg.com/@ffmpeg/ffmpeg@0.11.6/dist/ffmpeg.min.js",
    "ffmpeg-core.js": "https://unpkg.com/@ffmpeg/core@0.11.0/dist/ffmpeg-core.js",
    "ffmpeg-core.wasm": "https://unpkg.com/@ffmpeg/core@0.11.0/dist/ffmpeg-core.wasm"
}

def setup_directories():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        print(f"[+] Directory '{ASSETS_DIR}' created/verified.")

def manage_assets():
    print("[-] Processing assets...")
    
    for filename, url in LIBRARIES.items():
        dest_path = os.path.join(ASSETS_DIR, filename)
        
        # حالت 1: آیا فایل را در روت پروژه آپلود کرده‌اید؟ (اولویت بالا)
        if os.path.exists(filename):
            print(f"[*] Local file found: {filename}. Copying to assets...")
            shutil.copy(filename, dest_path)
            continue
            
        # حالت 2: آیا قبلاً دانلود شده؟
        if os.path.exists(dest_path):
            print(f"[v] {filename} exists in assets.")
            continue

        # حالت 3: دانلود از اینترنت (Fallback)
        print(f"[*] Downloading {filename}...")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(dest_path, 'wb') as f:
                    f.write(response.content)
                print(f"[+] Downloaded {filename}.")
            else:
                print(f"[!] Download failed for {filename}: {response.status_code}")
        except Exception as e:
            print(f"[!] Error processing {filename}: {e}")

def generate_html():
    # محتوای HTML با دو نکته کلیدی:
    # 1. فراخوانی coi-serviceworker در خط اول (برای فعال‌سازی هدرهای امنیتی در گیت‌هاب)
    # 2. تنظیم corePath به صورت لوکال برای FFmpeg
    
    html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FFmpeg + AI Processor</title>
    
    <!-- [حیاتی] این اسکریپت محیط امنیتی لازم برای FFmpeg را در گیت‌هاب ایجاد می‌کند -->
    <script src="assets/coi-serviceworker.js"></script>

    <style>
        body { font-family: sans-serif; background: #222; color: #fff; padding: 20px; text-align: center; }
        .box { background: #333; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
        button { padding: 10px 20px; background: #0d6efd; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:disabled { background: #555; cursor: not-allowed; }
        #log { background: #000; color: #0f0; height: 200px; overflow-y: auto; text-align: left; padding: 10px; margin-top: 10px; font-family: monospace; direction: ltr; }
        video { width: 100%; margin-top: 10px; }
    </style>
    
    <!-- بارگذاری FFmpeg -->
    <script src="assets/ffmpeg-lib.js"></script>
    
    <!-- بارگذاری TensorFlow (آماده برای استفاده‌های بعدی) -->
    <script src="assets/tf.min.js"></script>
    <script src="assets/pose-detection.min.js"></script>
    <script src="assets/coco-ssd.min.js"></script>
</head>
<body>
    <div class="box">
        <h2>پردازشگر ویدیو (GitHub Pages Compatible)</h2>
        <p id="status" style="color: yellow;">در حال آماده‌سازی...</p>
        
        <input type="file" id="uploader" accept="video/*" disabled>
        <br>
        <button id="btn-run" disabled>تست پردازش (5 ثانیه برش)</button>
        
        <div id="log"></div>
        <video id="output-video" controls></video>
    </div>

    <script>
        const { createFFmpeg, fetchFile } = FFmpeg;
        let ffmpeg = null;
        const logArea = document.getElementById('log');
        const statusEl = document.getElementById('status');
        const uploader = document.getElementById('uploader');
        const btnRun = document.getElementById('btn-run');

        function log(msg) {
            logArea.innerHTML += `> ${msg}<br>`;
            logArea.scrollTop = logArea.scrollHeight;
        }

        async function initApp() {
            try {
                // بررسی وضعیت امنیتی برای اطمینان
                if (window.crossOriginIsolated) {
                    log("وضعیت امنیتی: فعال (Secure Context) ✅");
                } else {
                    log("⚠️ هشدار: هدرهای امنیتی فعال نیستند. اسکریپت COI تلاش می‌کند صفحه را ریلود کند...");
                }

                statusEl.innerText = "در حال لود هسته FFmpeg...";
                
                // ایجاد نمونه FFmpeg با اشاره صریح به فایل لوکال
                ffmpeg = createFFmpeg({
                    log: true,
                    corePath: 'assets/ffmpeg-core.js', // نکته کلیدی برای اجرای آفلاین/لوکال
                    logger: ({ message }) => log(`[FFmpeg] ${message}`)
                });

                await ffmpeg.load();
                
                statusEl.innerText = "آماده به کار";
                statusEl.style.color = "#0f0";
                uploader.disabled = false;
                log("FFmpeg با موفقیت بارگذاری شد.");

            } catch (error) {
                statusEl.innerText = "خطا در بارگذاری";
                statusEl.style.color = "red";
                log(`[ERROR] ${error.message}`);
            }
        }

        uploader.addEventListener('change', (e) => {
            if(e.target.files[0]) {
                uploader.file = e.target.files[0];
                btnRun.disabled = false;
                log(`فایل انتخاب شد: ${uploader.file.name}`);
            }
        });

        btnRun.addEventListener('click', async () => {
            if(!ffmpeg) return;
            btnRun.disabled = true;
            statusEl.innerText = "در حال پردازش...";
            
            try {
                // نوشتن فایل در مموری
                ffmpeg.FS('writeFile', 'input.mp4', await fetchFile(uploader.file));
                
                // اجرای دستور (مثال: کات کردن 5 ثانیه اول بدون انکود مجدد)
                await ffmpeg.run('-i', 'input.mp4', '-t', '5', '-c', 'copy', 'out.mp4');
                
                // خواندن خروجی
                const data = ffmpeg.FS('readFile', 'out.mp4');
                const videoUrl = URL.createObjectURL(new Blob([data.buffer], {type: 'video/mp4'}));
                document.getElementById('output-video').src = videoUrl;
                
                log("✅ پردازش تمام شد.");
                statusEl.innerText = "پایان";
            } catch (e) {
                log(`❌ خطا: ${e.message}`);
            } finally {
                btnRun.disabled = false;
            }
        });

        initApp();
    </script>
</body>
</html>
"""
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] Generated {HTML_OUTPUT}")

if __name__ == "__main__":
    setup_directories()
    manage_assets()
    generate_html()
    print("[SUCCESS] Builder script finished.")
