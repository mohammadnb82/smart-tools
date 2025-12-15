import os
import subprocess

def deploy_face_scoring_app():
    print("--- BUILDING FACE SCORING APP (MOVENET) ---")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Face Scorer</title>
    <style>
        body { margin: 0; background: #111; font-family: 'Courier New', Courier, monospace; overflow: hidden; color: #0f0; }
        
        /* Main Container */
        #container { position: relative; width: 100vw; height: 100vh; display: flex; flex-direction: column; }
        
        /* Camera Feed */
        #cam-wrapper { position: relative; flex: 1; overflow: hidden; border-bottom: 2px solid #0f0; }
        video { width: 100%; height: 100%; object-fit: cover; opacity: 0.8; }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }

        /* Dashboard (Bottom) */
        #dashboard { height: 250px; background: #000; display: flex; align-items: center; padding: 10px; gap: 10px; border-top: 2px solid #0f0; }
        
        /* Best Shot Box */
        .best-shot-box { 
            width: 140px; height: 180px; 
            border: 2px dashed #0f0; 
            display: flex; flex-direction: column; 
            align-items: center; justify-content: center;
            background: #222;
            position: relative;
        }
        .best-shot-box img { width: 100%; height: 100%; object-fit: cover; display: none; }
        .best-shot-label { position: absolute; bottom: 0; background: #0f0; color: #000; width: 100%; text-align: center; font-weight: bold; font-size: 12px; }
        
        /* Stats Area */
        .stats { flex: 1; display: flex; flex-direction: column; gap: 5px; }
        .stat-row { display: flex; justify-content: space-between; font-size: 14px; border-bottom: 1px solid #333; padding-bottom: 2px; }
        .score-big { font-size: 40px; font-weight: bold; color: #0f0; text-align: center; margin-top: 10px; text-shadow: 0 0 10px #0f0; }
        
        /* Loading */
        #loading { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 100; display: flex; justify-content: center; align-items: center; flex-direction: column; }
        .spinner { width: 50px; height: 50px; border: 5px solid #333; border-top: 5px solid #0f0; border-radius: 50%; animation: spin 1s infinite linear; }
        
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- CLASSIC LOADING (Working Method) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <div id="loading">
        <div class="spinner"></div>
        <p>INITIALIZING AI SYSTEMS...</p>
    </div>

    <div id="container">
        <div id="cam-wrapper">
            <video id="video" playsinline muted autoplay></video>
            <canvas id="output"></canvas>
        </div>
        
        <div id="dashboard">
            <div class="best-shot-box">
                <img id="best-img" src="" alt="Best Shot">
                <div class="best-shot-label">BEST SHOT</div>
            </div>
            
            <div class="stats">
                <div class="stat-row"><span>NOSE:</span> <span id="s-nose">--</span></div>
                <div class="stat-row"><span>EYES (L/R):</span> <span id="s-eyes">--</span></div>
                <div class="stat-row"><span>EARS (L/R):</span> <span id="s-ears">--</span></div>
                <div class="stat-row" style="margin-top:5px; color:#fff;">CURRENT SCORE:</div>
                <div id="current-score" class="score-big">0</div>
            </div>
        </div>
    </div>

    <!-- Hidden canvas for cropping -->
    <canvas id="crop-canvas" style="display:none;"></canvas>

    <script>
        let detector;
        let video = document.getElementById('video');
        let canvas = document.getElementById('output');
        let ctx = canvas.getContext('2d');
        let cropCanvas = document.getElementById('crop-canvas');
        let cropCtx = cropCanvas.getContext('2d');
        
        let bestImg = document.getElementById('best-img');
        let scoreDisplay = document.getElementById('current-score');
        
        // Stats elements
        let sNose = document.getElementById('s-nose');
        let sEyes = document.getElementById('s-eyes');
        let sEars = document.getElementById('s-ears');

        let maxScore = 0;

        async function setupCamera() {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: 640, height: 480 },
                audio: false
            });
            video.srcObject = stream;
            return new Promise(resolve => {
                video.onloadedmetadata = () => {
                    video.play();
                    resolve();
                };
            });
        }

        async function loadModel() {
            await tf.ready();
            detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {
                modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING
            });
            document.getElementById('loading').style.display = 'none';
            detect();
        }

        async function detect() {
            if (video.readyState === 4) {
                // Resize main canvas
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                const poses = await detector.estimatePoses(video);
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (poses.length > 0) {
                    processPose(poses[0]);
                }
            }
            requestAnimationFrame(detect);
        }

        function processPose(pose) {
            const k = pose.keypoints;
            
            // MoveNet Keypoint IDs:
            // 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear
            
            let currentScore = 0;
            let parts = { nose: 0, l_eye: 0, r_eye: 0, l_ear: 0, r_ear: 0 };
            const THRESHOLD = 0.3;

            // 1. Calculate Score
            if (k[0].score > THRESHOLD) { currentScore += 20; parts.nose = 1; }
            if (k[1].score > THRESHOLD) { currentScore += 20; parts.l_eye = 1; }
            if (k[2].score > THRESHOLD) { currentScore += 20; parts.r_eye = 1; }
            if (k[3].score > THRESHOLD) { currentScore += 20; parts.l_ear = 1; }
            if (k[4].score > THRESHOLD) { currentScore += 20; parts.r_ear = 1; }

            // 2. Update Stats UI
            sNose.innerText = parts.nose ? "✅" : "❌";
            sEyes.innerText = (parts.l_eye ? "✅" : "❌") + " / " + (parts.r_eye ? "✅" : "❌");
            sEars.innerText = (parts.l_ear ? "✅" : "❌") + " / " + (parts.r_ear ? "✅" : "❌");
            scoreDisplay.innerText = currentScore;

            // 3. Draw Skeleton on Face
            drawFaceOverlay(k);

            // 4. Capture Best Shot
            // We only capture if score is high AND better than previous
            if (currentScore > maxScore && currentScore >= 60) {
                maxScore = currentScore;
                captureFace(k);
                scoreDisplay.style.color = '#fff'; // Flash white
                setTimeout(() => scoreDisplay.style.color = '#0f0', 200);
            }
        }

        function drawFaceOverlay(keypoints) {
            const faceIndices = [0, 1, 2, 3, 4];
            ctx.fillStyle = 'red';
            
            faceIndices.forEach(i => {
                if (keypoints[i].score > 0.3) {
                    ctx.beginPath();
                    ctx.arc(keypoints[i].x, keypoints[i].y, 5, 0, 2 * Math.PI);
                    ctx.fill();
                }
            });
        }

        function captureFace(keypoints) {
            // Find bounding box of face points
            const facePoints = keypoints.slice(0, 5).filter(p => p.score > 0.3);
            if (facePoints.length === 0) return;

            const xs = facePoints.map(p => p.x);
            const ys = facePoints.map(p => p.y);
            
            let minX = Math.min(...xs);
            let maxX = Math.max(...xs);
            let minY = Math.min(...ys);
            let maxY = Math.max(...ys);

            // Add padding (zoom out a bit)
            const padX = (maxX - minX) * 0.8; 
            const padY = (maxY - minY) * 1.0;

            minX = Math.max(0, minX - padX);
            minY = Math.max(0, minY - padY);
            maxX = Math.min(video.videoWidth, maxX + padX);
            maxY = Math.min(video.videoHeight, maxY + padY);
            
            const w = maxX - minX;
            const h = maxY - minY;

            // Draw to hidden canvas
            cropCanvas.width = w;
            cropCanvas.height = h;
            cropCtx.drawImage(video, minX, minY, w, h, 0, 0, w, h);

            // Show in UI
            bestImg.src = cropCanvas.toDataURL('image/jpeg');
            bestImg.style.display = 'block';
        }

        setupCamera().then(loadModel);

    </script>
</body>
</html>"""
    
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)

    print("Pushing to GitHub...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Face Scoring System"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("DONE! Refreshed with Face Scorer.")

if __name__ == "__main__":
    deploy_face_scoring_app()

