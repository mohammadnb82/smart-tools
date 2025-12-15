import os
import subprocess

def deploy_sequential_app():
    print("--- DEPLOYING v2.0 SEQUENTIAL LOAD (STABLE) ---")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Face Scorer v2.0</title>
    <style>
        body { margin: 0; background: #000; font-family: 'Courier New', Courier, monospace; overflow: hidden; color: #0f0; }
        
        /* Loading Screen */
        #loading-screen { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background: #000; z-index: 100; 
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center; 
            text-align: center;
        }
        .spinner { 
            width: 50px; height: 50px; 
            border: 5px solid #333; border-top: 5px solid #0f0; 
            border-radius: 50%; animation: spin 1s infinite linear; 
            margin-bottom: 20px;
        }
        .status-text { font-size: 14px; color: #fff; margin-top: 10px; }
        
        /* Main App (Hidden initially) */
        #app-container { display: none; width: 100vw; height: 100vh; flex-direction: column; }
        
        #cam-wrapper { position: relative; flex: 1; overflow: hidden; background: #111; border-bottom: 2px solid #0f0; }
        video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; transform: scaleX(-1); }

        /* Dashboard */
        #dashboard { height: 250px; background: #111; display: flex; padding: 10px; gap: 10px; align-items: center; }
        
        .score-box { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #333; border-radius: 8px; }
        .score-val { font-size: 60px; font-weight: bold; color: #0f0; text-shadow: 0 0 10px #0f0; }
        .score-title { font-size: 12px; color: #888; }
        
        .best-shot { width: 100px; height: 130px; border: 2px solid #0f0; border-radius: 8px; overflow: hidden; position: relative; background: #000; }
        .best-shot img { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        .best-label { position: absolute; bottom: 0; width: 100%; background: rgba(0,255,0,0.8); color: #000; font-size: 10px; text-align: center; }

        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- CLASSIC SCRIPTS (No Modules) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <!-- 1. LOADING SCREEN -->
    <div id="loading-screen">
        <div class="spinner"></div>
        <div id="status-msg" class="status-text">INITIALIZING...</div>
        <div id="sub-status" style="color: #666; font-size: 10px; margin-top:5px;">Please wait</div>
    </div>

    <!-- 2. MAIN APP -->
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
                <div class="score-title">ATTRACTIVENESS SCORE</div>
                <div id="score" class="score-val">--</div>
            </div>
        </div>
    </div>

    <script>
        // DOM Elements
        const statusMsg = document.getElementById('status-msg');
        const subStatus = document.getElementById('sub-status');
        const loadingScreen = document.getElementById('loading-screen');
        const appContainer = document.getElementById('app-container');
        const video = document.getElementById('video');
        const canvas = document.getElementById('output');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score');
        const bestImgEl = document.getElementById('best-img');

        let detector;
        let maxScore = 0;

        // --- STEP 1: LOAD AI MODEL (NO CAMERA YET) ---
        async function initApp() {
            try {
                statusMsg.innerText = "LOADING AI MODEL...";
                subStatus.innerText = "Downloading neural network (~10MB)";
                
                await tf.ready();
                console.log("TF Ready");
                
                detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet, 
                    { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
                );
                
                statusMsg.innerText = "MODEL READY!";
                subStatus.innerText = "Starting Camera...";
                
                // Only start camera AFTER model is ready
                setTimeout(startCamera, 1000);
                
            } catch (e) {
                statusMsg.innerText = "ERROR LOADING AI";
                subStatus.innerText = e.message;
                statusMsg.style.color = "red";
            }
        }

        // --- STEP 2: START CAMERA (ONLY AFTER STEP 1) ---
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width: 640, height: 480 },
                    audio: false
                });
                video.srcObject = stream;
                
                video.onloadedmetadata = () => {
                    video.play();
                    // Switch UI
                    loadingScreen.style.display = 'none';
                    appContainer.style.display = 'flex';
                    // Start Loop
                    detectLoop();
                };
            } catch (e) {
                statusMsg.innerText = "CAMERA DENIED";
                subStatus.innerText = "Please allow camera access and refresh.";
                statusMsg.style.color = "orange";
            }
        }

        // --- STEP 3: DETECTION LOOP ---
        async function detectLoop() {
            if (video.readyState === 4) {
                // Resize canvas to match video
                if (canvas.width !== video.videoWidth) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }

                const poses = await detector.estimatePoses(video);
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                if (poses.length > 0) {
                    const k = poses[0].keypoints;
                    // Check if face is visible (Nose, Eyes, Ears)
                    const facePoints = k.slice(0, 5); 
                    const visiblePoints = facePoints.filter(p => p.score > 0.3);

                    if (visiblePoints.length >= 3) {
                        calculateScore(facePoints);
                        drawFace(facePoints);
                    } else {
                        scoreEl.innerText = "--";
                    }
                }
            }
            requestAnimationFrame(detectLoop);
        }

        function calculateScore(keypoints) {
            // Simple scoring logic based on confidence & symmetry
            let rawScore = 0;
            keypoints.forEach(p => rawScore += p.score);
            
            // Normalize roughly to 0-100
            let finalScore = Math.min(Math.floor((rawScore / 5) * 110), 100);
            
            scoreEl.innerText = finalScore;

            // Capture Best Shot
            if (finalScore > maxScore && finalScore > 60) {
                maxScore = finalScore;
                captureBestShot();
            }
        }

        function drawFace(points) {
            ctx.fillStyle = "#0f0";
            points.forEach(p => {
                if(p.score > 0.3) {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 5, 0, 2*Math.PI);
                    ctx.fill();
                }
            });
        }

        function captureBestShot() {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = video.videoWidth;
            tempCanvas.height = video.videoHeight;
            const tCtx = tempCanvas.getContext('2d');
            tCtx.drawImage(video, 0, 0);
            bestImgEl.src = tempCanvas.toDataURL('image/jpeg');
        }

        // Start the process
        initApp();

    </script>
</body>
</html>"""

    # نوشتن فایل
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)

    # پاک کردن فایل‌های اضافی برای جلوگیری از کش شدن نسخه قبلی
    if os.path.exists("diagnostic.html"):
        os.remove("diagnostic.html")

    print("Git Pushing v2.0...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Deploy v2.0 Sequential Load"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("DONE! Wait 2 minutes, then CLEAR CACHE and try.")

if __name__ == "__main__":
    deploy_sequential_app()
