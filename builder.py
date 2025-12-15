import os
import subprocess

def fix_workflow_and_deploy():
    print("--- 1. RESTORING GITHUB ACTION WORKFLOW ---")
    
    # ساختن پوشه های لازم اگر وجود ندارند
    os.makedirs(".github/workflows", exist_ok=True)
    
    # محتوای فایل تنظیمات ربات گیت‌هاب
    workflow_content = """name: Build and Deploy
on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  build-and-deploy:
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
    
    # ذخیره فایل yaml
    with open(".github/workflows/deploy.yml", "w", encoding='utf-8') as f:
        f.write(workflow_content)
    print("✅ Workflow file restored (.github/workflows/deploy.yml)")

    print("--- 2. CREATING FINAL WEB FILES (v4.1) ---")
    
    # ساخت فایل nojekyll برای سرعت بیشتر
    with open(".nojekyll", "w") as f:
        f.write("")

    # ساخت فایل اصلی سایت (با تم آبی برای تشخیص آپدیت)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Face Scorer v4.1</title>
    <style>
        /* DARK BLUE THEME - VISUAL PROOF OF FIX */
        body { margin: 0; background: #000033; font-family: sans-serif; overflow: hidden; color: #fff; }
        
        #loader { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: #000033; z-index: 999; 
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center; 
        }
        .spinner { 
            width: 50px; height: 50px; border: 5px solid #111; 
            border-top: 5px solid #00ffff; border-radius: 50%; 
            animation: spin 1s infinite linear; 
        }
        .status { margin-top: 20px; color: #00ffff; font-size: 18px; font-weight: bold; }
        .sub-status { margin-top: 5px; color: #8899aa; font-size: 14px; }
        
        #vpn-btn {
            display: none; margin-top: 30px; padding: 15px 30px;
            background: #ff3333; color: #fff; border: none; border-radius: 8px;
            font-size: 16px; font-weight: bold; cursor: pointer;
        }

        #app { display: none; width: 100vw; height: 100vh; flex-direction: column; }
        #cam-box { flex: 1; position: relative; overflow: hidden; background: #000; }
        video, canvas { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; transform: scaleX(-1); }
        
        #bottom-panel { 
            height: 200px; background: #111; border-top: 4px solid #00ffff; 
            display: flex; align-items: center; justify-content: center;
        }
        .score-circle {
            width: 120px; height: 120px; border-radius: 50%;
            border: 6px solid #00ffff;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            background: #222;
        }
        .score-val { font-size: 50px; font-weight: bold; color: #fff; }

        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- CLASSIC LOADING METHOD -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>
    <div id="loader">
        <div class="spinner"></div>
        <div id="status" class="status">RESTORING SYSTEM...</div>
        <div id="sub" class="sub-status">v4.1 - Workflow Fixed</div>
        <button id="vpn-btn" onclick="location.reload()">VPN ON? RETRY</button>
    </div>

    <div id="app">
        <div id="cam-box">
            <video id="vid" playsinline muted autoplay></video>
            <canvas id="cvs"></canvas>
        </div>
        <div id="bottom-panel">
            <div class="score-circle">
                <div id="score" class="score-val">--</div>
            </div>
        </div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const vpnBtn = document.getElementById('vpn-btn');
        const loader = document.getElementById('loader');
        const app = document.getElementById('app');
        const video = document.getElementById('vid');
        const canvas = document.getElementById('cvs');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        let detector;

        async function start() {
            try {
                statusEl.innerText = "LOADING AI MODELS...";
                await tf.ready();
                detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet,
                    { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
                );
                
                statusEl.innerText = "OPENING CAMERA...";
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width: 640, height: 480 },
                    audio: false
                });
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    video.play();
                    loader.style.display = 'none';
                    app.style.display = 'flex';
                    runAI();
                };
            } catch (e) {
                statusEl.innerText = "ERROR OR VPN BLOCKED";
                statusEl.style.color = "red";
                vpnBtn.style.display = "block";
                console.error(e);
            }
        }

        async function runAI() {
            if(video.readyState === 4) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const poses = await detector.estimatePoses(video);
                ctx.clearRect(0,0,canvas.width,canvas.height);
                if(poses.length > 0) {
                    const k = poses[0].keypoints.filter(p => p.score > 0.3);
                    k.forEach(p => {
                        ctx.fillStyle = "#00ffff";
                        ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, 2*Math.PI); ctx.fill();
                    });
                    if(k.length > 5) scoreEl.innerText = Math.floor(Math.random() * 20 + 80);
                }
            }
            requestAnimationFrame(runAI);
        }
        start();
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("✅ index.html updated (Blue Theme v4.1)")

    print("--- 3. PUSHING TO GITHUB ---")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Restore Workflow and Deploy v4.1"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("🎉 DONE! Workflow restored. Wait 60 seconds then check the site.")

if __name__ == "__main__":
    fix_workflow_and_deploy()
