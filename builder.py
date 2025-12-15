import os
import subprocess

def deploy_face_scoring_app():
    print("--- BUILDING FINAL FACE SCORING APP ---")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Face Scorer</title>
    <style>
        body { margin: 0; background: #000; font-family: 'Courier New', Courier, monospace; overflow: hidden; color: #0f0; }
        
        /* Main Container */
        #container { position: relative; width: 100vw; height: 100vh; display: flex; flex-direction: column; }
        
        /* Camera Feed */
        #cam-wrapper { position: relative; flex: 1; overflow: hidden; border-bottom: 2px solid #0f0; background: #111; }
        video { width: 100%; height: 100%; object-fit: cover; opacity: 1; }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }

        /* Dashboard (Bottom) */
        #dashboard { height: 260px; background: #111; display: flex; align-items: center; padding: 15px; gap: 15px; border-top: 2px solid #0f0; box-shadow: 0 -5px 20px rgba(0, 255, 0, 0.2); }
        
        /* Best Shot Box */
        .best-shot-box { 
            width: 130px; height: 170px; 
            border: 2px dashed #0f0; 
            display: flex; flex-direction: column; 
            align-items: center; justify-content: center;
            background: #000;
            position: relative;
            border-radius: 8px;
            overflow: hidden;
        }
        .best-shot-box img { width: 100%; height: 100%; object-fit: cover; display: none; }
        .best-shot-label { position: absolute; bottom: 0; background: rgba(0, 255, 0, 0.8); color: #000; width: 100%; text-align: center; font-weight: bold; font-size: 10px; padding: 2px 0; }
        
        /* Stats Area */
        .stats { flex: 1; display: flex; flex-direction: column; gap: 8px; }
        .stat-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid #333; padding-bottom: 4px; }
        .score-container { text-align: center; margin-top: 5px; }
        .score-label { font-size: 12px; color: #fff; margin-bottom: 0px; }
        .score-big { font-size: 45px; font-weight: bold; color: #0f0; text-shadow: 0 0 15px #0f0; line-height: 1; }
        
        /* Loading Overlay */
        #loading { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 100; display: flex; justify-content: center; align-items: center; flex-direction: column; }
        .spinner { width: 40px; height: 40px; border: 4px solid #333; border-top: 4px solid #0f0; border-radius: 50%; animation: spin 1s infinite linear; margin-bottom: 20px;}
        .loading-text { color: #0f0; font-size: 14px; letter-spacing: 2px; }
        
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- CLASSIC LOADING (The method that worked on your iPhone) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <div id="loading">
        <div class="spinner"></div>
        <p class="loading-text">SYSTEM INITIALIZING...</p>
    </div>

    <div id="container">
        <div id="cam-wrapper">
            <!-- playsinline is CRITICAL for iOS -->
            <video id="video" playsinline muted autoplay></video>
            <canvas id="output"></canvas>
        </div>
        
        <div id="dashboard">
            <div class="best-shot-box">
                <img id="best-img" src="" alt="Best Shot">
                <div class="best-shot-label">BEST CAPTURE</div>
            </div>
            
            <div class="stats">
                <div class="stat-row"><span>NOSE</span> <span id="s-nose">--</span></div>
                <div class="stat-row"><span>EYES (L/R)</span> <span id="s-eyes">--</span></div>
                <div class="stat-row"><span>EARS (L/R)</span> <span id="s-ears">--</span></div>
                
                <div class="score-container">
                    <div class="score-label">QUALITY SCORE</div>
                    <div id="current-score" class="score-big">0</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Hidden canvas for cropping the face -->
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
        
        let sNose = document.getElementById('s-nose');
        let sEyes = document.getElementById('s-eyes');
        let sEars = document.getElementById('s-ears');

        let maxScore = 0;
        let isModelLoaded = false;

        async function setupCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { 
                        facingMode: 'user', // Selfie camera
                        width: { ideal: 640 },
                        height: { ideal: 480 }
                    },
                    audio: false
                });
                video.srcObject = stream;
                return new Promise(resolve => {
                    video.onloadedmetadata = () => {
                        video.play();
                        resolve();
                    };
                });
            } catch (e) {
                alert("Camera Access Error: " + e.message);
            }
        }

        async function loadModel() {
            await tf.ready();
            // Using MoveNet SinglePose Lightning (Fast & Stable)
            detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {
                modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING
            });
            isModelLoaded = true;
            document.getElementById('loading').style.display = 'none';
            detectLoop();
        }

        async function detectLoop() {
            if (isModelLoaded && video.readyState === 4) {
                // Ensure canvas matches video size
                if (canvas.width !== video.videoWidth) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }

                try {
                    const poses = await detector.estimatePoses(video);
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    if (poses.length > 0) {
                        processPose(poses[0]);
                    }
                } catch (err) {
                    console.error("Detection Error", err);
                }
            }
            requestAnimationFrame(detectLoop);
        }

        function processPose(pose) {
            const k = pose.keypoints;
            
            // MoveNet Keypoint Mapping:
            // 0: nose
            // 1: left_eye
            // 2: right_eye
            // 3: left_ear
            // 4: right_ear
            
            let currentScore = 0;
            let parts = { nose: 0, l_eye: 0, r_eye: 0, l_ear: 0, r_ear: 0 };
            const THRESHOLD = 0.4; // Confidence threshold

            // Calculate Score (20 pts each part)
            if (k[0].score > THRESHOLD) { currentScore += 20; parts.nose = 1; }
            if (k[1].score > THRESHOLD) { currentScore += 20; parts.l_eye = 1; }
            if (k[2].score > THRESHOLD) { currentScore += 20; parts.r_eye = 1; }
            if (k[3].score > THRESHOLD) { currentScore += 20; parts.l_ear = 1; }
            if (k[4].score > THRESHOLD) { currentScore += 20; parts.r_ear = 1; }

            // Update UI Stats
            sNose.style.color = parts.nose ? '#0f0' : '#555';
            sNose.innerText = parts.nose ? "DETECTED" : "...";

            sEyes.style.color = (parts.l_eye && parts.r_eye) ? '#0f0' : '#fff';
            sEyes.innerText = (parts.l_eye ? "L" : "-") + " / " + (parts.r_eye ? "R" : "-");

            sEars.style.color = (parts.l_ear && parts.r_ear) ? '#0f0' : '#fff';
            sEars.innerText = (parts.l_ear ? "L" : "-") + " / " + (parts.r_ear ? "R" : "-");
            
            scoreDisplay.innerText = currentScore;

            // Visual Feedback (Draw dots)
            drawFacePoints(k);

            // Logic: Capture Best Shot
            // 1. Must have a decent score (>60)
            // 2. Must be equal or better than previous best score
            if (currentScore >= 60 && currentScore >= maxScore) {
                // Only capture if we haven't captured this score recently or it's higher
                if (currentScore > maxScore) {
                    maxScore = currentScore;
                    captureFace(k);
                    flashScore();
                }
            }
        }

        function drawFacePoints(keypoints) {
            const faceIndices = [0, 1, 2, 3, 4];
            ctx.fillStyle = '#0f0'; // Green dots
            
            faceIndices.forEach(i => {
                if (keypoints[i].score > 0.4) {
                    ctx.beginPath();
                    ctx.arc(keypoints[i].x, keypoints[i].y, 4, 0, 2 * Math.PI);
                    ctx.fill();
                }
            });
        }

        function flashScore() {
            scoreDisplay.style.color = '#fff';
            scoreDisplay.style.textShadow = '0 0 20px #fff';
            setTimeout(() => {
                scoreDisplay.style.color = '#0f0';
                scoreDisplay.style.textShadow = '0 0 15px #0f0';
            }, 150);
        }

        function captureFace(keypoints) {
            // Calculate bounding box based on 5 keypoints
            const facePoints = keypoints.slice(0, 5).filter(p => p.score > 0.4);
            if (facePoints.length < 3) return; // Need at least 3 points for a good crop

            const xs = facePoints.map(p => p.x);
            const ys = facePoints.map(p => p.y);
            
            let minX = Math.min(...xs);
            let maxX = Math.max(...xs);
            let minY = Math.min(...ys);
            let maxY = Math.max(...ys);

            // Add padding (Zoom out slightly to frame the face)
            const padX = (maxX - minX) * 0.6; 
            const padY = (maxY - minY) * 0.8;

            minX = Math.max(0, minX - padX);
            minY = Math.max(0, minY - padY);
            maxX = Math.min(video.videoWidth, maxX + padX);
            maxY = Math.min(video.videoHeight, maxY + padY);
            
            const w = maxX - minX;
            const h = maxY - minY;

            // Crop logic
            cropCanvas.width = w;
            cropCanvas.height = h;
            cropCtx.drawImage(video, minX, minY, w, h, 0, 0, w, h);

            // Display in dashboard
            bestImg.src = cropCanvas.toDataURL('image/jpeg');
            bestImg.style.display = 'block';
        }

        // Start everything
        setupCamera().then(loadModel);

    </script>
</body>
</html>"""
    
    # Overwrite index.html directly
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)

    # Git commands
    print("Pushing to GitHub...")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Final Face Scoring App"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("DONE! Reload your site to see the Face Scorer.")

if __name__ == "__main__":
    deploy_face_scoring_app()
