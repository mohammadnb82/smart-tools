import os
import subprocess
import time

def deploy_final_v4():
    print("--- STARTING FINAL DEPLOYMENT (v4.0) ---")

    # 1. Create .nojekyll to speed up GitHub Pages
    with open(".nojekyll", "w") as f:
        f.write("")
    print("Created .nojekyll file.")

    # 2. Create index.html with BLUE background (Visual Indicator)
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Face Scorer v4.0</title>
    <style>
        /* DARK BLUE BACKGROUND -> Visual proof of new version */
        body { margin: 0; background: #000022; font-family: sans-serif; overflow: hidden; color: #fff; }
        
        #loader { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: #000022; z-index: 999; 
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center; 
        }
        .spinner { 
            width: 50px; height: 50px; border: 5px solid #111; 
            border-top: 5px solid #00aaff; border-radius: 50%; 
            animation: spin 1s infinite linear; 
        }
        .status { margin-top: 20px; color: #00aaff; font-size: 18px; font-weight: bold; }
        .sub-status { margin-top: 5px; color: #8899aa; font-size: 14px; }
        
        #vpn-btn {
            display: none; margin-top: 30px; padding: 15px 30px;
            background: #ff3333; color: #fff; border: none; border-radius: 8px;
            font-size: 16px; font-weight: bold; cursor: pointer;
        }

        /* Main App */
        #app { display: none; width: 100vw; height: 100vh; flex-direction: column; }
        #cam-box { flex: 1; position: relative; overflow: hidden; background: #000; }
        video, canvas { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; transform: scaleX(-1); }
        
        #bottom-panel { 
            height: 200px; background: #111; border-top: 4px solid #00aaff; 
            display: flex; align-items: center; justify-content: center;
        }
        .score-circle {
            width: 120px; height: 120px; border-radius: 50%;
            border: 6px solid #00aaff;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            background: #222;
        }
        .score-val { font-size: 50px; font-weight: bold; color: #fff; }
        .score-lbl { font-size: 10px; color: #aaa; }

        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- CLASSIC LOADING (Fixes iPhone Module Error) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <div id="loader">
        <div class="spinner"></div>
        <div id="status" class="status">CONNECTING v4.0...</div>
        <div id="sub" class="sub-status">Downloading AI (Needs VPN)</div>
        <button id="vpn-btn" onclick="retry()">VPN ON? CLICK HERE</button>
    </div>

    <div id="app">
        <div id="cam-box">
            <video id="vid" playsinline muted autoplay></video>
            <canvas id="cvs"></canvas>
        </div>
        <div id="bottom-panel">
            <div class="score-circle">
                <div id="score" class="score-val">--</div>
                <div class="score-lbl">SCORE</div>
            </div>
        </div>
    </div>

    <script>
        const statusEl = document.getElementById('status');
        const subEl = document.getElementById('sub');
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
                vpnBtn.style.display = 'none';
                statusEl.innerText = "LOADING AI...";
                statusEl.style.color = "#00aaff";
                
                await tf.ready();
                detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet,
                    { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
                );

                statusEl.innerText = "OPENING CAMERA...";
                initCamera();
                
            } catch (e) {
                statusEl.innerText = "DOWNLOAD FAILED";
                statusEl.style.color = "red";
                subEl.innerText = "Please enable VPN.";
                vpnBtn.style.display = 'block';
            }
        }

        function retry() { start(); }

        async function initCamera() {
            try {
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
                statusEl.innerText = "CAMERA BLOCKED";
                subEl.innerText = "Allow camera access in settings.";
            }
        }

        async function runAI() {
            if(video.readyState === 4) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                const poses = await detector.estimatePoses(video);
                ctx.clearRect(0,0,canvas.width,canvas.height);

                if(poses.length > 0) {
                    const kp = poses[0].keypoints;
                    const face = kp.slice(0,5);
                    let conf = 0;
                    let count = 0;
                    
                    ctx.fillStyle = "#00aaff";
                    face.forEach(p => {
                        if(p.score > 0.3) {
                            ctx.beginPath();
                            ctx.arc(p.x, p.y, 5, 0, 2*Math.PI);
                            ctx.fill();
                            conf += p.score;
                            count++;
                        }
                    });

                    if(count >= 3) {
                        let s = Math.floor((conf/5)*110);
                        if(s>100) s=98;
                        scoreEl.innerText = s;
                    }
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

    print("Created index.html (Blue Theme).")

    # 3. Git Push
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Deploy v4.0 Blue Theme"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("DONE. Pushed to GitHub.")

if __name__ == "__main__":
    deploy_final_v4()
