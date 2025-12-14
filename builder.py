import os
import requests
import json
import subprocess
import shutil

# --- تنظیمات و آدرس‌ها ---
ASSETS_DIR = "smart-tools/assets"  # مسیر اصلاح شده برای ساختار فولدر شما
MOVENET_DIR = os.path.join(ASSETS_DIR, "movenet")
ROOT_DIR = "smart-tools"

# لینک‌های اصلی کتابخانه‌های مورد نیاز (نسخه‌های هماهنگ)
TF_JS_URL = "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"
TF_BACKEND_URL = "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"
TF_CONVERTER_URL = "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-converter@3.18.0/dist/tf-converter.js"
POSE_DETECTION_URL = "https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"

# لینک مدل MoveNet Lightning
MODEL_BASE_URL = "https://storage.googleapis.com/tfjs-models/savedmodel/movenet/singlepose/lightning/"
MODEL_JSON_URL = MODEL_BASE_URL + "model.json"

def download_file(url, dest_path):
    print(f"Downloading {url} -> {dest_path} ...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Downloaded.")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

def setup_directories():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
    if not os.path.exists(MOVENET_DIR):
        os.makedirs(MOVENET_DIR)

def download_assets():
    # 1. دانلود کتابخانه‌های JS
    download_file(TF_JS_URL, os.path.join(ASSETS_DIR, "tf.min.js"))
    download_file(TF_BACKEND_URL, os.path.join(ASSETS_DIR, "tf-backend-webgl.js"))
    download_file(TF_CONVERTER_URL, os.path.join(ASSETS_DIR, "tf-converter.js"))
    download_file(POSE_DETECTION_URL, os.path.join(ASSETS_DIR, "pose-detection.js"))

    # 2. دانلود مدل MoveNet (JSON + Binary shards)
    json_path = os.path.join(MOVENET_DIR, "model.json")
    download_file(MODEL_JSON_URL, json_path)
    
    try:
        with open(json_path, 'r') as f:
            model_data = json.load(f)
            weights_manifest = model_data.get('weightsManifest', [])
            for manifest in weights_manifest:
                paths = manifest.get('paths', [])
                for filename in paths:
                    bin_url = MODEL_BASE_URL + filename
                    bin_path = os.path.join(MOVENET_DIR, filename)
                    download_file(bin_url, bin_path)
    except Exception as e:
        print(f"❌ Error parsing model.json: {e}")

def create_html_files():
    # محتوای اصلاح شده human_cam.html
    human_cam_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human Camera - MoveNet</title>
    <style>
        body { margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #f0f0f0; font-family: sans-serif; height: 100vh; }
        h1 { margin-bottom: 10px; }
        #canvas-wrapper { position: relative; width: 640px; height: 480px; background: #000; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        video { position: absolute; top: 0; left: 0; width: 640px; height: 480px; object-fit: cover; transform: scaleX(-1); }
        canvas { position: absolute; top: 0; left: 0; width: 640px; height: 480px; transform: scaleX(-1); }
        #status { margin-top: 10px; font-weight: bold; color: #333; }
        #error-log { margin-top: 10px; color: red; font-size: 0.9rem; white-space: pre-wrap; }
    </style>
    
    <!-- کتابخانه‌ها -->
    <script src="./assets/tf.min.js"></script>
    <script src="./assets/tf-backend-webgl.js"></script>
    <script src="./assets/tf-converter.js"></script>
    <script src="./assets/pose-detection.js"></script>
</head>
<body>
    <h1>Smart Human Cam</h1>
    <div id="canvas-wrapper">
        <video id="video" playsinline></video>
        <canvas id="output"></canvas>
    </div>
    <div id="status">Initializing...</div>
    <div id="error-log"></div>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('output');
        const ctx = canvas.getContext('2d');
        const statusDiv = document.getElementById('status');
        const errorLog = document.getElementById('error-log');
        let detector;

        function logError(msg) {
            console.error(msg);
            errorLog.textContent += msg + "\\n";
            statusDiv.textContent = "Error occurred.";
        }

        async function setupCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480, facingMode: 'user' }
                });
                video.srcObject = stream;
                return new Promise((resolve) => {
                    video.onloadedmetadata = () => {
                        video.play();
                        resolve(video);
                    };
                });
            } catch (err) {
                logError("Camera Error: " + err.message);
                throw err;
            }
        }

        async function loadModel() {
            try {
                statusDiv.textContent = "Loading TensorFlow...";
                if (typeof tf === 'undefined') throw new Error("tf is undefined");
                
                await tf.setBackend('webgl');
                await tf.ready();
                
                statusDiv.textContent = "Loading Detector (Local)...";
                const detectorConfig = {
                    modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING,
                    modelUrl: './assets/movenet/model.json'
                };
                detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, detectorConfig);
                
                statusDiv.textContent = "Running...";
                detectPose();
            } catch (err) {
                logError("Setup Error: " + err.message);
            }
        }

        async function detectPose() {
            if (!detector) return;
            try {
                const poses = await detector.estimatePoses(video);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                if (poses && poses.length > 0) {
                    poses[0].keypoints.forEach(keypoint => {
                        if (keypoint.score > 0.3) {
                            ctx.beginPath();
                            ctx.arc(keypoint.x, keypoint.y, 5, 0, 2 * Math.PI);
                            ctx.fillStyle = 'aqua';
                            ctx.fill();
                        }
                    });
                }
                requestAnimationFrame(detectPose);
            } catch (err) {
                 requestAnimationFrame(detectPose);
            }
        }

        setupCamera().then(loadModel);
    </script>
</body>
</html>"""

    # فایل ایندکس
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Tools Hub</title>
    <style>body{text-align:center;padding:50px;font-family:sans-serif;} a{display:block;margin:20px;font-size:1.5rem;}</style>
</head>
<body>
    <h1>Select Tool</h1>
    <a href="human_cam.html">Human Detection (MoveNet)</a>
    <a href="general_cam.html">General Camera</a>
</body>
</html>"""

    general_cam_content = """<!DOCTYPE html><html><body><h1>General Cam</h1></body></html>"""

    with open(os.path.join(ROOT_DIR, "human_cam.html"), "w") as f:
        f.write(human_cam_content)
    with open(os.path.join(ROOT_DIR, "index.html"), "w") as f:
        f.write(index_content)
    with open(os.path.join(ROOT_DIR, "general_cam.html"), "w") as f:
        f.write(general_cam_content)
    
    print("✅ HTML files generated.")

def configure_git_and_push():
    print("🚀 Configuring Git and Pushing changes...")
    try:
        # تنظیمات هویت برای گیت در محیط Actions
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
        
        # اضافه کردن تمام فایل‌ها
        subprocess.run(["git", "add", "."], check=True)
        
        # کامیت کردن (اگر تغییری نباشد ارور نمی‌دهد)
        subprocess.run(["git", "commit", "-m", "Auto-build assets and HTML via GitHub Action"], check=False)
        
        # پوش کردن
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Changes pushed to repo.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Operation Failed: {e}")

if __name__ == "__main__":
    print("--- Starting Auto-Builder (GitHub Actions Mode) ---")
    setup_directories()
    download_assets()
    create_html_files()
    configure_git_and_push()
    print("--- Finished ---")
