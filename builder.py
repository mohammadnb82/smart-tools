import os
import shutil
import urllib.request
import json
import subprocess

# ================= تنظیمات =================
PROJECT_NAME = "smart-tools"
OUTPUT_DIR = PROJECT_NAME  # پوشه خروجی

# مسیرهای حیاتی (دقت کنید: movenet داخل assets است)
ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")
MOVENET_DIR = os.path.join(ASSETS_DIR, "movenet")

# لینک‌های دانلود کتابخانه‌ها
libs = {
    "tf-core.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-core@3.11.0/dist/tf-core.min.js",
    "tf-converter.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-converter@3.11.0/dist/tf-converter.min.js",
    "tf-backend-webgl.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.11.0/dist/tf-backend-webgl.min.js",
    "pose-detection.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@0.0.6/dist/pose-detection.min.js",
    "coco-ssd.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd", 
}

MOVENET_BASE_URL = "https://storage.googleapis.com/tfjs-models/savedmodel/movenet/singlepose/lightning/4/"

# ================= HTML CONTENT =================
# نکته مهم: در اینجا آدرس مدل به صورت ./assets/movenet/model.json تنظیم شده است
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
        #status-msg {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: yellow; font-size: 20px; text-align: center; text-shadow: 2px 2px 4px #000;
        }
        #error-log {
            position: absolute; bottom: 10px; left: 10px; width: 90%; 
            color: red; font-size: 12px; background: rgba(0,0,0,0.8); 
            padding: 5px; display: none; z-index: 20; text-align: left; direction: ltr;
        }
    </style>
    <!-- لود کتابخانه‌ها از مسیر لوکال -->
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
        <div id="status-msg">در حال بارگذاری مدل آفلاین...<br>(لطفا صبر کنید)</div>
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
            errorLog.innerText = "Error: " + err;
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
                console.log("TF Ready.");
                
                // تنظیم دقیق آدرس مدل
                const modelConfig = {
                    modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING,
                    modelUrl: './assets/movenet/model.json' 
                };
                
                console.log("Loading model from:", modelConfig.modelUrl);
                detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, modelConfig);
                
                console.log("Model Loaded Successfully!");
                statusMsg.style.display = 'none'; // مخفی کردن پیام لودینگ
                detectPose();
            } catch (e) {
                logError(e.message + "\\nCheck if assets/movenet/model.json exists.");
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
                    keypoints.forEach(kp => {
                        if (kp.score > 0.3) {
                            ctx.beginPath();
                            ctx.arc(kp.x, kp.y, 6, 0, 2 * Math.PI);
                            ctx.fillStyle = '#00ff00';
                            ctx.fill();
                            ctx.strokeStyle = '#ffffff';
                            ctx.stroke();
                        }
                    });
                }
            } catch (err) { console.log(err); }
            requestAnimationFrame(detectPose);
        }

        (async function main() {
            try { await setupCamera(); await loadModel(); } catch(e) { logError(e); }
        })();
    </script>
</body>
</html>
"""

index_html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منوی ابزار</title>
    <style>
        body { font-family: Tahoma; background: #222; color: white; text-align: center; padding-top: 50px; }
        .btn { display: block; width: 80%; margin: 20px auto; padding: 15px; background: #444; color: white; text-decoration: none; border-radius: 8px; border: 1px solid #666; }
    </style>
</head>
<body>
    <h1>انتخاب ابزار</h1>
    <a href="human_cam.html" class="btn">دوربین هوشمند (MoveNet)</a>
    <a href="general_cam.html" class="btn">تشخیص اشیاء</a>
</body>
</html>
"""

general_cam_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><title>General Cam</title></head>
<body style="background:black;color:white;text-align:center;">
    <h1>General Cam (Placeholder)</h1>
    <a href="index.html" style="color:yellow;">بازگشت</a>
</body></html>
"""

# ================= توابع =================

def download_file(url, path):
    if os.path.exists(path):
        print(f"  [OK] Exists: {os.path.basename(path)}")
        return True
    print(f"  [DOWNLOADING] {url} -> {path}")
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def download_movenet_structure():
    print("\n--- Checking MoveNet Structure ---")
    if not os.path.exists(MOVENET_DIR):
        print(f"Creating directory: {MOVENET_DIR}")
        os.makedirs(MOVENET_DIR)
    
    # 1. دانلود فایل اصلی JSON
    json_path = os.path.join(MOVENET_DIR, "model.json")
    if download_file(MOVENET_BASE_URL + "model.json", json_path):
        # 2. خواندن فایل برای پیدا کردن فایل‌های باینری
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            print("Reading model.json to find weights...")
            if 'weightsManifest' in data:
                for group in data['weightsManifest']:
                    if 'paths' in group:
                        for filename in group['paths']:
                            bin_url = MOVENET_BASE_URL + filename
                            bin_path = os.path.join(MOVENET_DIR, filename)
                            download_file(bin_url, bin_path)
        except Exception as e:
            print(f"Error parsing model.json: {e}")

def run_git_commands():
    print("\n--- Running Git Commands ---")
    os.chdir(OUTPUT_DIR)
    commands = [
        "git add .",
        "git commit -m 'Fix directory structure: Moved model.json to assets/movenet/'",
        "git push"
    ]
    for cmd in commands:
        print(f"Exec: {cmd}")
        subprocess.run(cmd, shell=True)

def main():
    # ساخت پوشه‌های اصلی
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    # 1. دانلود کتابخانه‌های JS
    print("--- Downloading JS Libraries ---")
    for name, url in libs.items():
        download_file(url, os.path.join(ASSETS_DIR, name))

    # 2. دانلود مدل در پوشه درست (assets/movenet)
    download_movenet_structure()

    # 3. ساخت فایل‌های HTML
    print("\n--- Generating HTML Files ---")
    with open(os.path.join(OUTPUT_DIR, "human_cam.html"), "w", encoding="utf-8") as f:
        f.write(human_cam_content)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html_content)
    with open(os.path.join(OUTPUT_DIR, "general_cam.html"), "w", encoding="utf-8") as f:
        f.write(general_cam_content)

    # 4. آپلود خودکار
    run_git_commands()
    
    print("\n\n✅ DONE! عملیات تمام شد.")
    print("نکته مهم: اگر فایل model.json قبلی در پوشه assets مانده، دستی پاکش کنید (اختیاری).")
    print("لطفاً چند دقیقه صبر کنید تا GitHub Pages آپدیت شود.")

if __name__ == "__main__":
    main()
