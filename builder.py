import os
import shutil
import subprocess

# --- تنظیمات ---
ASSETS_DIR = "smart-tools/assets"
ROOT_DIR = "smart-tools"

def clean_assets():
    """پوشه assets را کامل حذف می‌کند تا از فایل‌های لوکال استفاده نشود"""
    if os.path.exists(ASSETS_DIR):
        print(f"🧹 Cleaning up local assets: {ASSETS_DIR}...")
        shutil.rmtree(ASSETS_DIR)
        print("✅ Assets folder removed.")
    else:
        print("ℹ️ Assets folder not found, skipping cleanup.")

def create_html_files():
    # محتوای human_cam.html با استفاده از CDN آنلاین
    human_cam_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human Camera - MoveNet (Online)</title>
    <style>
        body { margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #f0f0f0; font-family: sans-serif; height: 100vh; }
        h1 { margin-bottom: 10px; font-size: 1.2rem; }
        #canvas-wrapper { position: relative; width: 640px; height: 480px; background: #000; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        video { position: absolute; top: 0; left: 0; width: 640px; height: 480px; object-fit: cover; transform: scaleX(-1); }
        canvas { position: absolute; top: 0; left: 0; width: 640px; height: 480px; transform: scaleX(-1); }
        #status { margin-top: 10px; font-weight: bold; color: #333; }
        #error-log { margin-top: 10px; color: red; font-size: 0.8rem; white-space: pre-wrap; max-width: 90%; text-align: left; }
    </style>
    
    <!-- لود کردن کتابخانه‌ها از CDN (نیاز به اینترنت/VPN) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>
    <h1>Smart Human Cam (Online Mode)</h1>
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
            errorLog.textContent += "❌ " + msg + "\\n";
            statusDiv.textContent = "Error occurred.";
        }

        async function setupCamera() {
            try {
                // تلاش برای دوربین پشت و سپس جلو
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { 
                        width: 640, 
                        height: 480, 
                        facingMode: 'environment' 
                    }
                });
                video.srcObject = stream;
                return new Promise((resolve) => {
                    video.onloadedmetadata = () => {
                        video.play();
                        // تنظیم ابعاد کانواس بر اساس سایز واقعی ویدیو
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        video.width = video.videoWidth;
                        video.height = video.videoHeight;
                        resolve(video);
                    };
                });
            } catch (err) {
                logError("Camera Access Error: " + err.message);
                throw err;
            }
        }

        async function loadModel() {
            try {
                statusDiv.textContent = "Loading TensorFlow (Online)...";
                
                // بررسی لود شدن TF
                if (typeof tf === 'undefined') {
                    throw new Error("TensorFlow JS failed to load from CDN.");
                }
                console.log("TF Version:", tf.version.tfjs);

                await tf.setBackend('webgl');
                await tf.ready();
                
                statusDiv.textContent = "Loading MoveNet Model (Online)...";
                
                // تنظیمات مدل برای دانلود از سرور گوگل
                const detectorConfig = {
                    modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING
                };
                
                // ساخت دتکتور (خودکار مدل را دانلود می‌کند)
                detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet, 
                    detectorConfig
                );
                
                statusDiv.textContent = "Running AI...";
                detectPose();
            } catch (err) {
                logError("Model Loading Error: " + err.message);
            }
        }

        async function detectPose() {
            if (!detector) return;
            try {
                const poses = await detector.estimatePoses(video);
                
                // پاک کردن و رسم مجدد
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                if (poses && poses.length > 0) {
                    poses[0].keypoints.forEach(keypoint => {
                        // فقط نقاط با دقت بالای 30% را رسم کن
                        if (keypoint.score > 0.3) {
                            const x = keypoint.x;
                            const y = keypoint.y;
                            
                            ctx.beginPath();
                            ctx.arc(x, y, 6, 0, 2 * Math.PI);
                            ctx.fillStyle = '#00FF00'; // سبز روشن
                            ctx.fill();
                            ctx.strokeStyle = '#FFFFFF';
                            ctx.stroke();
                        }
                    });
                }
                
                requestAnimationFrame(detectPose);
            } catch (err) {
                 console.error(err);
                 requestAnimationFrame(detectPose);
            }
        }

        // شروع برنامه
        setupCamera().then(loadModel).catch(e => logError("Init failed: " + e.message));
    </script>
</body>
</html>"""

    # فایل ایندکس ساده
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Tools Hub</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{text-align:center; padding:50px; font-family:sans-serif; background:#333; color:white;} 
        a{display:block; margin:20px auto; padding:15px; background:#007bff; color:white; text-decoration:none; border-radius:8px; max-width:300px;}
    </style>
</head>
<body>
    <h1>Select Tool</h1>
    <a href="human_cam.html">Human Detection (Online Mode)</a>
</body>
</html>"""

    # نوشتن فایل‌ها
    os.makedirs(ROOT_DIR, exist_ok=True)
    
    with open(os.path.join(ROOT_DIR, "human_cam.html"), "w") as f:
        f.write(human_cam_content)
    
    with open(os.path.join(ROOT_DIR, "index.html"), "w") as f:
        f.write(index_content)
    
    print("✅ HTML files generated (CDN Mode).")

def configure_git_and_push():
    print("🚀 Configuring Git and Pushing changes...")
    try:
        # تنظیم هویت گیت‌هاب اکشن
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
        
        # استیج کردن همه تغییرات (شامل حذف assets)
        subprocess.run(["git", "add", "."], check=True)
        
        # کامیت
        subprocess.run(["git", "commit", "-m", "Switch to Online CDN mode and clean local assets"], check=False)
        
        # پوش
        subprocess.run(["git", "push"], check=True)
        print("✅ Done! Changes pushed to repo.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Operation Failed: {e}")

if __name__ == "__main__":
    print("--- Starting Auto-Builder (CDN Mode) ---")
    clean_assets()
    create_html_files()
    configure_git_and_push()
    print("--- Finished ---")
