import os
import subprocess

def deploy_vpn_ready_app():
    print("--- DEPLOYING v2.1 (VPN READY + SEQUENTIAL) ---")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Face Scorer v2.1</title>
    <style>
        body { margin: 0; background: #000; font-family: 'Courier New', Courier, monospace; overflow: hidden; color: #0f0; }
        
        /* Loading Screen */
        #loading-screen { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background: #000; z-index: 100; 
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center; 
            text-align: center;
            padding: 20px;
        }
        .spinner { 
            width: 50px; height: 50px; 
            border: 5px solid #333; border-top: 5px solid #0f0; 
            border-radius: 50%; animation: spin 1s infinite linear; 
            margin-bottom: 20px;
        }
        .status-text { font-size: 16px; color: #fff; margin-top: 10px; font-weight: bold; }
        .sub-text { font-size: 12px; color: #888; margin-top: 5px; max-width: 80%; }
        
        /* Retry Button (Hidden by default) */
        #retry-btn {
            display: none;
            margin-top: 20px;
            padding: 15px 30px;
            background: #222;
            border: 2px solid #f00;
            color: #f00;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 8px;
        }

        /* Main App (Hidden initially) */
        #app-container { display: none; width: 100vw; height: 100vh; flex-direction: column; }
        
        #cam-wrapper { position: relative; flex: 1; overflow: hidden; background: #111; border-bottom: 2px solid #0f0; }
        video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; transform: scaleX(-1); }

        /* Dashboard */
        #dashboard { height: 240px; background: #111; display: flex; padding: 10px; gap: 10px; align-items: center; }
        
        .score-box { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #333; border-radius: 8px; }
        .score-val { font-size: 70px; font-weight: bold; color: #0f0; text-shadow: 0 0 10px #0f0; }
        .score-title { font-size: 12px; color: #888; letter-spacing: 2px; }
        
        .best-shot { width: 100px; height: 100%; border: 2px solid #0f0; border-radius: 8px; overflow: hidden; position: relative; background: #000; }
        .best-shot img { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); display:none; }
        .best-label { position: absolute; bottom: 0; width: 100%; background: rgba(0,255,0,0.8); color: #000; font-size: 10px; text-align: center; }

        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- CLASSIC SCRIPTS (Stable) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <!-- LOADING / ERROR SCREEN -->
    <div id="loading-screen">
        <div id="spinner" class="spinner"></div>
        <div id="status-msg" class="status-text">CONNECTING TO AI...</div>
        <div id="sub-status" class="sub-text">Please ensure VPN is ON for first load.</div>
        <button id="retry-btn" onclick="retryLoad()">VPN ON? TRY AGAIN</button>
    </div>

    <!-- MAIN APP -->
    <div id="app-container">
        <div id="cam-wrapper">
            <video id="video" playsinline muted autoplay></video>
            <canvas id="output"></canvas>
        </div>
        <div id="dashboard">
            <div class="best-shot">
                <img id="best-img" src="">
                <div class="best-label">BEST</div>
            </div>
            <div class="score-box">
                <div class="score-title">SCORE</div>
                <div id="score" class="score-val">--</div>
            </div>
        </div>
    </div>

    <!-- Canvas for cropping -->
    <canvas id="crop-canvas" style="display:none;"></canvas>

    <script>
        // DOM Elements
        const statusMsg = document.getElementById('status-msg');
        const subStatus = document.getElementById('sub-status');
        const retryBtn = document.getElementById('retry-btn');
        const spinner = document.getElementById('spinner');
        const loadingScreen = document.getElementById('loading-screen');
        const appContainer = document.getElementById('app-container');
        const video = document.getElementById('video');
        const canvas = document.getElementById('output');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const bestImgEl = document.getElementById('best-img');
        const cropCanvas = document.getElementById('crop-canvas');
        const cropCtx = cropCanvas.getContext('2d');

        let detector;
        let maxScore = 0;

        // --- STEP 1: LOAD AI MODEL ---
        async function initApp() {
            try {
                // Reset UI
                spinner.style.display = 'block';
                retryBtn.style.display = 'none';
                statusMsg.innerText = "DOWNLOADING MODEL...";
                statusMsg.style.color = "#fff";
                subStatus.innerText = "Connecting to Google Servers (~10MB)...";
                
                await tf.ready();
                
                // This is the part that needs VPN
                detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet, 
                    { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
                );
                
                statusMsg.innerText = "MODEL READY!";
                subStatus.innerText = "Starting Camera...";
                
                // Success! Now start camera
                setTimeout(startCamera, 1000);
                
            } catch (e) {
                console.error(e);
                spinner.style.display = 'none';
                statusMsg.innerText = "DOWNLOAD FAILED";
                statusMsg.style.color = "red";
                subStatus.innerText = "The AI model was blocked. Please turn on VPN.";
                retryBtn.style.display = 'block'; // Show Retry Button
            }
        }

        function retryLoad() {
            initApp();
        }

        // --- STEP 2: START CAMERA ---
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width: 640, height: 480 },
                    audio: false
                });
                video.srcObject = stream;
                
                video.onloadedmetadata = () => {
                    video.play();
                    loadingScreen.style.display = 'none';
                    appContainer.style.display = 'flex';
                    detectLoop();
                };
            } catch (e) {
                statusMsg.innerText = "CAMERA DENIED";
                statusMsg.style.color = "orange";
                subStatus.innerText = "Please allow camera access and Refresh.";
                retryBtn.style.display = 'none';
            }
        }

        // --- STEP 3: LOGIC ---
        async function detectLoop() {
            if (video.readyState === 4) {
                if (canvas.width !== video.videoWidth) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }

                const poses = await detector.estimatePoses(video);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                if (poses.length > 0) {
                    processPose(poses[0]);
                }
            }
            requestAnimationFrame(detectLoop);
        }

        function processPose(pose) {
            const k = pose.keypoints;
            const facePoints = k.slice(0, 5); // Nose, Eyes, Ears
            
            // Draw Dots
            ctx.fillStyle = "#0f0";
            let visibleCount = 0;
            let rawScore = 0;

            facePoints.forEach(p => {
                if(p.score > 0.3) {
                    visibleCount++;
                    rawScore += p.score;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 5, 0, 2*Math.PI);
                    ctx.fill();
                }
            });

            if (visibleCount >= 3) {
                // Calculate Score (0-100)
                let finalScore = Math.min(Math.floor((rawScore / 5) * 115), 100);
                scoreEl.innerText = finalScore;

                if (finalScore > maxScore && finalScore > 60) {
                    maxScore = finalScore;
                    captureFace(facePoints);
                }
            } else {
                scoreEl.innerText = "--";
            }
        }

        function captureFace(facePoints) {
            // Smart Crop Logic
            const xs = facePoints.map(p => p.x);
            const ys = facePoints.map(p => p.y);
            const minX = Math.max(0, Math.min(...xs) - 50);
            const maxX = Math.min(video.videoWidth, Math.max(...xs) + 50);
            const minY = Math.max(0, Math.min(...ys) - 80);
            const maxY = Math.min(video.videoHeight, Math.max(...ys) + 80);
            
            const w = maxX - minX;
            const h = maxY - minY;

            cropCanvas.width = w;
            cropCanvas.height = h;
            cropCtx.drawImage(video, minX, minY, w, h, 0, 0, w, h);
            
            bestImgEl.src = cropCanvas.toDataURL('image/jpeg');
            bestImgEl.style.display = 'block';
        }

        // Start
        initApp();

    </script>
</body>
</html>"""

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)

    if os.path.exists("diagnostic.html"):
        os.remove("diagnostic.html")

    print("Deploying v2.1 with VPN Retry Button...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Deploy v2.1 VPN Ready"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("DONE. Wait 3 mins.")

if __name__ == "__main__":
    deploy_vpn_ready_app()
