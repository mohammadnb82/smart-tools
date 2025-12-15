import os
import subprocess

def restore_workflow_engine():
    print("--- 1. REPAIRING GITHUB ACTIONS ENGINE ---")
    
    # اطمینان از وجود پوشه مخفی ورک‌فلو
    os.makedirs(".github/workflows", exist_ok=True)
    
    # بازسازی دقیق فایلی که باعث می‌شد گزینه builder.py در لیست دیده شود
    # نام آن را در خط اول 'builder.py' می‌گذاریم تا در لیست شما مثل قبل دیده شود
    workflow_yaml = """name: builder.py

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout 🛎️
        uses: actions/checkout@v3

      - name: Deploy to GitHub Pages 🚀
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          folder: .
          clean: true
"""
    
    # نوشتن فایل تنظیمات
    with open(".github/workflows/main.yml", "w", encoding='utf-8') as f:
        f.write(workflow_yaml)
    print("✅ Workflow file restored (.github/workflows/main.yml)")

    print("--- 2. UPDATING SITE TO BLUE THEME (v5.0) ---")
    
    # فایل nojekyll
    with open(".nojekyll", "w") as f:
        f.write("")

    # فایل اصلی سایت (نسخه آبی جدید)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Fixed Engine v5.0</title>
    <style>
        /* DEEP NAVY BLUE -> Proof that workflow is back */
        body { margin: 0; background: #001133; font-family: sans-serif; overflow: hidden; color: #fff; }
        
        #loader { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: #001133; z-index: 999; 
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center; 
        }
        .spinner { 
            width: 50px; height: 50px; border: 5px solid #000; 
            border-top: 5px solid #00ffaa; border-radius: 50%; 
            animation: spin 1s infinite linear; 
        }
        .status { margin-top: 20px; color: #00ffaa; font-size: 20px; font-weight: bold; }
        .sub { margin-top: 10px; color: #8899aa; font-size: 14px; }
        
        #vpn-btn {
            display: none; margin-top: 30px; padding: 15px 30px;
            background: #ff4444; color: #fff; border: none; border-radius: 8px;
            font-size: 16px; font-weight: bold; cursor: pointer;
        }

        #app { display: none; width: 100vw; height: 100vh; flex-direction: column; }
        #cam-box { flex: 1; position: relative; overflow: hidden; background: #000; }
        video, canvas { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; transform: scaleX(-1); }
        
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
    
    <!-- Using Classic Scripts to prevent Module Error on iOS -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>
    <div id="loader">
        <div class="spinner"></div>
        <div id="status">RESTORING WORKFLOW...</div>
        <div class="sub">v5.0 - Engine Fixed</div>
        <button id="vpn-btn" onclick="location.reload()">VPN ON? RETRY</button>
    </div>

    <div id="app">
        <div id="cam-box">
            <video id="vid" playsinline muted autoplay></video>
            <canvas id="cvs"></canvas>
        </div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const vpnBtn = document.getElementById('vpn-btn');
        const loader = document.getElementById('loader');
        const app = document.getElementById('app');
        const video = document.getElementById('vid');
        
        async function start() {
            try {
                statusEl.innerText = "CHECKING AI ENGINE...";
                await tf.ready();
                const detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet,
                    { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
                );
                
                statusEl.innerText = "STARTING CAMERA...";
                const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    video.play();
                    loader.style.display = 'none';
                    app.style.display = 'flex';
                };
            } catch (e) {
                statusEl.innerText = "CONNECTION FAILED";
                statusEl.style.color = "red";
                vpnBtn.style.display = "block";
            }
        }
        start();
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print("--- 3. PUSHING TO GITHUB ---")
    # Force adding .github folder
    subprocess.run(["git", "add", ".github"], check=False)
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Restore builder.py workflow"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("🎉 DONE! Check GitHub Actions tab. You should see 'builder.py' appear shortly.")

if __name__ == "__main__":
    restore_workflow_engine()
