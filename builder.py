import os
import shutil
import urllib.request
import json
import subprocess
import time

# ================= تنظیمات =================
PROJECT_NAME = "smart-tools"
OUTPUT_DIR = PROJECT_NAME  # پوشه خروجی (همان پوشه‌ای که پروژه در آن است)

# مسیرهای دانلود
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")
MOVENET_DIR = os.path.join(ASSETS_DIR, "movenet")

# لینک‌های دانلود
libs = {
    "tf-core.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-core@3.11.0/dist/tf-core.min.js",
    "tf-converter.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-converter@3.11.0/dist/tf-converter.min.js",
    "tf-backend-webgl.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.11.0/dist/tf-backend-webgl.min.js",
    "pose-detection.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@0.0.6/dist/pose-detection.min.js",
    "coco-ssd.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd", 
}

MOVENET_BASE_URL = "https://storage.googleapis.com/tfjs-models/savedmodel/movenet/singlepose/lightning/4/"

# ================= محتوای فایل‌های HTML =================

index_html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ابزارهای هوشمند - نسخه کامل</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f0f0f0; text-align: center; padding: 20px; }
        .btn { display: block; width: 80%; max-width: 300px; margin: 15px auto; padding: 15px; 
               background: #007bff; color: white; text-decoration: none; border-radius: 10px; font-size: 18px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>منوی ابزارهای هوشمند</h1>
    <p>نسخه آفلاین و اصلاح شده</p>
    <a href="human_cam.html" class="btn">تشخیص هویت و آناتومی</a>
    <a href="general_cam.html" class="btn">تشخیص اشیاء</a>
</body>
</html>
"""

human_cam_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تشخیص هویت (چهره و بدن)</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: black; font-family: sans-serif; }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }
        .back-btn {
            position: absolute; top: 20px; left: 20px; pointer-events: auto;
            background: rgba(0,0,0,0.6); color: white; padding: 10px 20px;
            border: 1px solid white; border-radius: 20px; text-decoration: none; font-size: 14px;
        }
        .controls {
            position: absolute; top: 20px; right: 20px; pointer-events: auto;
            background: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; color: white;
            display: flex; align-items: center; gap: 10px;
        }
        #status-msg {
            position: absolute; top: 80px; width: 100%; text-align: center;
            color: yellow; font-size: 18px; text-shadow: 1px 1px 2px black;
        }
        #error-log {
            position: absolute; bottom: 10px; left: 10px; width: 90%; 
            color: red; font-size: 12px; background: rgba(0,0,0,0.8); 
            padding: 5px; display: none; z-index: 20; text-align: left; direction: ltr;
        }
    </style>
    <script src="./assets/tf-core.js"></script>
    <script src="./assets/tf-converter.js"></script>
    <script src="./assets/tf-backend-webgl.js"></script>
    <script src="./assets/pose-detection.js"></script>
</head>
<body>
    <video id="video" playsinline style="display: none;"></video>
    <canvas id="output"></canvas>
    <div id="ui-layer">
        <a href="index.html" class="back-btn">BACK</a>
        <div class="controls">
            <input type="range" id="threshold" min="0" max="100" value="50">
            <span id="thresh-val">حساسیت: 50%</span>
        </div>
        <div id="status-msg">...در حال بارگذاری مدل آفلاین...</div>
        <div id="error-log"></div>
    </div>
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('output');
        const ctx = canvas.getContext('2d');
        const statusMsg = document.getElementById('status-msg');
        const errorLog = document.getElementById('error-log');
        let detector;

        function logError(err) {
            console.error(err);
            statusMsg.innerText = "خطا در اجرا";
            errorLog.style.display = 'block';
            errorLog.innerText = err;
        }

        async function setupCamera() {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: 640, height: 480 }, audio: false
            });
            video.srcObject = stream;
            return new Promise((resolve) => { video.onloadedmetadata = () => { video.play(); resolve(video); }; });
        }

        async function loadModel() {
            try {
                await tf.ready();
                // آدرس دهی دقیق به فایل لوکال
                const modelConfig = {
                    modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING,
                    modelUrl: './assets/movenet/model.json' 
                };
                detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, modelConfig);
                statusMsg.innerText = ""; 
                detectPose();
            } catch (e) {
                logError("Error Loading Model: " + e.message + " (Check assets/movenet folder)");
            }
        }

        async function detectPose() {
            if (!detector) return;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            try {
                const poses = await detector.estimatePoses(video);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                if (poses && poses.length > 0) {
                    const keypoints = poses[0].keypoints;
                    const threshold = document.getElementById('threshold').value / 100;
                    keypoints.forEach(kp => {
                        if (kp.score > threshold) {
                            ctx.beginPath();
                            ctx.arc(kp.x, kp.y, 5, 0, 2 * Math.PI);
                            ctx.fillStyle = '#00ff00';
                            ctx.fill();
                        }
                    });
                }
            } catch (err) {}
            requestAnimationFrame(detectPose);
        }

        (async function main() {
            try { await setupCamera(); await loadModel(); } catch(e) { logError(e); }
        })();
    </script>
</body>
</html>
"""

general_cam_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تشخیص اشیاء</title>
    <script src="./assets/tf-core.js"></script>
    <script src="./assets/tf-converter.js"></script>
    <script src="./assets/tf-backend-webgl.js"></script>
    <script src="./assets/coco-ssd.js"></script>
    <style>body{background:black;color:white;text-align:center;} .back-btn{background:white;color:black;padding:5px;position:fixed;top:10px;left:10px;}</style>
</head>
<body>
    <a href="index.html" class="back-btn">بازگشت</a>
    <video id="webcam" autoplay playsinline width="100%"></video>
    <canvas id="canvas" style="position:absolute;top:0;left:0;"></canvas>
    <p id="status">در حال لود...</p>
    <script>
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const status = document.getElementById('status');
        let model;
        async function run() {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
            video.srcObject = stream;
            await new Promise(r => video.onloadedmetadata = () => { video.play(); r(); });
            canvas.width = video.videoWidth; canvas.height = video.videoHeight;
            model = await cocoSsd.load();
            status.innerText = "";
            detectFrame();
        }
        function detectFrame() {
            model.detect(video).then(predictions => {
                ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
                predictions.forEach(prediction => {
                    const [x, y, width, height] = prediction.bbox;
                    ctx.strokeStyle = "#00FFFF"; ctx.strokeRect(x, y, width, height);
                    ctx.fillStyle = "#00FFFF"; ctx.fillText(prediction.class, x, y > 10 ? y - 5 : 10);
                });
                requestAnimationFrame(detectFrame);
            });
        }
        run();
    </script>
</body>
</html>
"""

# ================= توابع اجرایی =================

def run_command(command):
    """اجرای دستورات ترمینال از داخل پایتون"""
    print(f"Executing: {command}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error: {stderr.decode('utf-8')}")
        else:
            print(f"Output: {stdout.decode('utf-8')}")
    except Exception as e:
        print(f"Failed to run command: {e}")

def download_file(url, path):
    print(f"Downloading: {url} -> {path}")
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def download_movenet_full():
    """دانلود هوشمند مدل کامل (JSON + BIN)"""
    if not os.path.exists(MOVENET_DIR):
        os.makedirs(MOVENET_DIR)
    
    # 1. دانلود model.json
    json_path = os.path.join(MOVENET_DIR, "model.json")
    if not download_file(MOVENET_BASE_URL + "model.json", json_path):
        return

    # 2. خواندن JSON برای پیدا کردن فایل‌های وزن (.bin)
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # گشتن دنبال فایل‌های .bin در ساختار json
        if 'weightsManifest' in data:
            for group in data['weightsManifest']:
                if 'paths' in group:
                    for filename in group['paths']:
                        bin_url = MOVENET_BASE_URL + filename
                        bin_path = os.path.join(MOVENET_DIR, filename)
                        download_file(bin_url, bin_path)
    except Exception as e:
        print(f"Error parsing model json: {e}")

def main():
    # 1. ساختن ساختار فایل‌ها
    print("--- STEP 1: Building Files ---")
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)

    # دانلود کتابخانه‌ها
    for name, url in libs.items():
        download_file(url, os.path.join(ASSETS_DIR, name))

    # دانلود مدل کامل
    download_movenet_full()

    # نوشتن فایل‌های HTML
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(index_html_content)
    with open(os.path.join(OUTPUT_DIR, "human_cam.html"), "w", encoding="utf-8") as f: f.write(human_cam_content)
    with open(os.path.join(OUTPUT_DIR, "general_cam.html"), "w", encoding="utf-8") as f: f.write(general_cam_content)

    print("\n--- STEP 2: Auto-Upload to GitHub ---")
    # تغییر مسیر به پوشه پروژه
    os.chdir(OUTPUT_DIR)
    
    # اجرای دستورات گیت توسط پایتون
    run_command("git config --global user.email 'you@example.com'") # جلوگیری از خطای ایمیل (اختیاری)
    run_command("git config --global user.name 'Your Name'")       # جلوگیری از خطای نام (اختیاری)
    
    run_command("git add .")
    run_command("git commit -m 'Auto fix: Added missing model bin files'")
    run_command("git push")

    print("\n========================================")
    print("DONE! عملیات تمام شد.")
    print("لطفاً یک دقیقه صبر کنید و سپس سایت را در موبایل رفرش کنید.")
    print("========================================")

if __name__ == "__main__":
    main()
