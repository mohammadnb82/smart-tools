import os
import shutil
import subprocess

# --- تنظیمات ---
ROOT_DIR = "smart-tools"
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

def clean_and_setup():
    """پاکسازی فایل‌های قدیمی و ساخت پوشه ریشه"""
    # اگر پوشه assets وجود دارد، پاکش کن تا تداخل ایجاد نشود
    if os.path.exists(ASSETS_DIR):
        print("🧹 Cleaning old assets...")
        shutil.rmtree(ASSETS_DIR)
    
    os.makedirs(ROOT_DIR, exist_ok=True)

def create_human_cam():
    """ساخت فایل تشخیص حرکت (انسان) - بهینه شده برای iOS"""
    content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Human Detection (Fix)</title>
    <style>
        body { margin: 0; background-color: #000; overflow: hidden; display: flex; flex-direction: column; height: 100vh; }
        #canvas-wrapper { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
        video { position: absolute; min-width: 100%; min-height: 100%; object-fit: cover; }
        canvas { position: absolute; min-width: 100%; min-height: 100%; object-fit: cover; }
        #overlay { position: absolute; top: 10px; left: 10px; z-index: 10; color: #0f0; font-family: monospace; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 4px; pointer-events: none;}
    </style>
    
    <!-- کتابخانه‌های آنلاین -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>
    <div id="overlay">
        Status: Initializing...<br>
        FPS: <span id="fps">0</span>
    </div>
    <div id="canvas-wrapper">
        <!-- نکته مهم برای آیفون: playsinline و muted و autoplay -->
        <video id="video" playsinline muted autoplay></video>
        <canvas id="output"></canvas>
    </div>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('output');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('overlay');
        const fpsSpan = document.getElementById('fps');
        let detector;
        let lastFrameTime = 0;
        let isRunning = true;

        function updateStatus(msg) {
            overlay.innerHTML = msg + "<br>FPS: <span id='fps'>...</span>";
        }

        async function setupCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } },
                    audio: false
                });
                video.srcObject = stream;
                
                return new Promise((resolve) => {
                    video.onloadedmetadata = () => {
                        video.play();
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        resolve(video);
                    };
                });
            } catch (err) {
                alert("Camera Error: " + err.message);
            }
        }

        async function loadModel() {
            try {
                updateStatus("Loading AI...");
                await tf.ready();
                const detectorConfig = { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING };
                detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, detectorConfig);
                updateStatus("System Ready");
                detectLoop();
            } catch (err) {
                updateStatus("AI Error: " + err.message);
                console.error(err);
            }
        }

        async function detectLoop() {
            if (!isRunning) return;
            
            const now = performance.now();
            const fps = 1000 / (now - lastFrameTime);
            lastFrameTime = now;
            if(fpsSpan) fpsSpan.innerText = Math.round(fps);

            // اطمینان از اینکه کانواس هم‌اندازه ویدیو است
            if (canvas.width !== video.videoWidth) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }

            // پاک کردن کانواس
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            try {
                if (detector) {
                    const poses = await detector.estimatePoses(video);
                    if (poses && poses.length > 0) {
                        drawSkeleton(poses[0].keypoints);
                    }
                }
            } catch (error) {
                console.log("Detection skip:", error);
            }

            requestAnimationFrame(detectLoop);
        }

        function drawSkeleton(keypoints) {
            keypoints.forEach(point => {
                if (point.score > 0.3) {
                    ctx.beginPath();
                    ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
                    ctx.fillStyle = 'aqua';
                    ctx.fill();
                    ctx.stroke();
                }
            });
        }

        setupCamera().then(loadModel);
    </script>
</body>
</html>"""
    with open(os.path.join(ROOT_DIR, "human_cam.html"), "w") as f:
        f.write(content)

def create_object_cam():
    """بازسازی فایل تشخیص اشیا (Coco-SSD) با CDN"""
    content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Object Detection (Coco-SSD)</title>
    <style>
        body { margin: 0; background: #222; overflow: hidden; display: flex; flex-direction: column; height: 100vh; }
        video { position: absolute; min-width: 100%; min-height: 100%; object-fit: cover; }
        canvas { position: absolute; min-width: 100%; min-height: 100%; object-fit: cover; }
        #info { position: absolute; top: 10px; left: 10px; z-index: 20; color: yellow; background: rgba(0,0,0,0.7); padding: 5px; }
    </style>
    <!-- لود کتابخانه‌ها -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd"></script>
</head>
<body>
    <div id="info">Loading Object Detection...</div>
    <video id="video" playsinline muted autoplay></video>
    <canvas id="canvas"></canvas>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const info = document.getElementById('info');
        let model;

        async function start() {
            try {
                // 1. راه اندازی دوربین
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' }, 
                    audio: false 
                });
                video.srcObject = stream;
                
                await new Promise(r => video.onloadedmetadata = r);
                video.play();
                
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // 2. لود مدل
                info.innerText = "Loading Model...";
                model = await cocoSsd.load();
                info.innerText = "Running...";
                
                predict();
            } catch (e) {
                info.innerText = "Error: " + e.message;
            }
        }

        async function predict() {
            // اصلاح سایز کانواس در صورت چرخش گوشی
            if (canvas.width !== video.videoWidth) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // کشیدن مستطیل‌ها
            if(model) {
                const predictions = await model.detect(video);
                predictions.forEach(prediction => {
                    const [x, y, width, height] = prediction.bbox;
                    
                    ctx.strokeStyle = '#00FFFF';
                    ctx.lineWidth = 4;
                    ctx.strokeRect(x, y, width, height);
                    
                    ctx.fillStyle = '#00FFFF';
                    ctx.font = '18px Arial';
                    ctx.fillText(prediction.class + ' ' + Math.round(prediction.score * 100) + '%', x, y > 10 ? y - 5 : 10);
                });
            }

            requestAnimationFrame(predict);
        }

        start();
    </script>
</body>
</html>"""
    with open(os.path.join(ROOT_DIR, "general_cam.html"), "w") as f:
        f.write(content)

def create_index():
    content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Tools Hub</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; text-align: center; padding: 20px; background: #1a1a1a; color: white; }
        h1 { margin-bottom: 30px; }
        .btn { display: block; background: #007AFF; color: white; padding: 20px; margin: 15px auto; border-radius: 12px; text-decoration: none; font-size: 1.2rem; max-width: 300px; }
        .btn:active { opacity: 0.8; transform: scale(0.98); }
    </style>
</head>
<body>
    <h1>Smart AI Tools</h1>
    <a href="human_cam.html" class="btn">👤 Human Detection (MoveNet)</a>
    <a href="general_cam.html" class="btn">📦 Object Detection (Coco-SSD)</a>
    <p style="color: #666; font-size: 0.8rem; margin-top: 50px;">Running in CDN Mode (Requires VPN)</p>
</body>
</html>"""
    with open(os.path.join(ROOT_DIR, "index.html"), "w") as f:
        f.write(content)

def push_changes():
    print("🚀 Pushing to GitHub...")
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=False)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=False)
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Fix: iOS video freeze and restore object detection"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("✅ Done.")

if __name__ == "__main__":
    clean_and_setup()
    create_human_cam()
    create_object_cam()
    create_index()
    push_changes()
