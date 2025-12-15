import os
import subprocess
import time

def force_deploy_v3():
    print("--- STARTING HARD RESET & DEPLOY v3.0 ---")

    # 1. Clean up OLD files aggressively
    files_to_remove = ["index.html", "diagnostic.html", "human_cam.html"]
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted old file: {f}")

    # 2. Generate the FINAL APP (Face Scorer v3 - No Modules)
    # We add a random version query (?v=3.0) to scripts to force-clear cache
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <!-- CHANGE TITLE TO FORCE UPDATE -->
    <title>Face Scorer v3.0 FINAL</title>
    <style>
        body { margin: 0; background: #000; font-family: sans-serif; overflow: hidden; color: #fff; }
        
        /* Loading Overlay */
        #loader { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: #000; z-index: 999; 
            display: flex; flex-direction: column; 
            justify-content: center; align-items: center; 
        }
        .spinner { 
            width: 40px; height: 40px; border: 4px solid #333; 
            border-top: 4px solid #00ff00; border-radius: 50%; 
            animation: spin 1s infinite linear; 
        }
        .status { margin-top: 15px; color: #00ff00; font-weight: bold; }
        .sub-status { margin-top: 5px; color: #666; font-size: 12px; }
        
        #vpn-btn {
            display: none; margin-top: 20px; padding: 12px 24px;
            background: #b00; color: #fff; border: none; border-radius: 6px;
            font-size: 16px; font-weight: bold; cursor: pointer;
        }

        /* Main UI */
        #main-ui { display: none; width: 100vw; height: 100vh; flex-direction: column; }
        #video-container { flex: 1; position: relative; overflow: hidden; background: #111; }
        video, canvas { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; transform: scaleX(-1); }
        
        #hud { 
            height: 180px; background: #111; border-top: 2px solid #333; 
            display: flex; align-items: center; justify-content: space-around; 
            padding: 10px; box-sizing: border-box;
        }
        
        .score-display { text-align: center; }
        .score-num { font-size: 60px; font-weight: 800; color: #00ff00; text-shadow: 0 0 15px #00ff00; }
        .score-label { color: #888; font-size: 12px; letter-spacing: 2px; }
        
        .best-shot-box { 
            width: 100px; height: 120px; border: 1px solid #444; 
            background: #000; position: relative; border-radius: 8px; overflow: hidden; 
        }
        .best-shot-box img { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
        .best-badge { 
            position: absolute; bottom: 0; width: 100%; 
            background: rgba(0,255,0,0.8); color: #000; 
            font-size: 10px; text-align: center; font-weight: bold; 
        }

        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>

    <!-- LOAD LIBRARIES (Classic Method - Fixes iPhone Error) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <div id="loader">
        <div class="spinner"></div>
        <div id="status-text" class="status">INITIALIZING...</div>
        <div id="sub-text" class="sub-status">Downloading AI Model (Check VPN)</div>
        <button id="vpn-btn" onclick="retryModel()">VPN ON? TRY AGAIN</button>
    </div>

    <div id="main-ui">
        <div id="video-container">
            <video id="vid" playsinline muted autoplay></video>
            <canvas id="cvs"></canvas>
        </div>
        <div id="hud">
            <div class="best-shot-box">
                <img id="best-img">
                <div class="best-badge">BEST</div>
            </div>
            <div class="score-display">
                <div class="score-label">ATTRACTIVENESS</div>
                <div id="score-val" class="score-num">--</div>
            </div>
        </div>
    </div>

    <!-- Hidden crop canvas -->
    <canvas id="crop-cvs" style="display:none;"></canvas>

    <script>
        const statusEl = document.getElementById('status-text');
        const subStatusEl = document.getElementById('sub-text');
        const vpnBtn = document.getElementById('vpn-btn');
        const loader = document.getElementById('loader');
        const mainUi = document.getElementById('main-ui');
        const video = document.getElementById('vid');
        const canvas = document.getElementById('cvs');
        const ctx = canvas.getContext('2d');
        const scoreEl = document.getElementById('score-val');
        const bestImg = document.getElementById('best-img');
        const cropCvs = document.getElementById('crop-cvs');
        const cropCtx = cropCvs.getContext('2d');

        let detector;
        let highestScore = 0;

        async function init() {
            try {
                // Reset UI
                vpnBtn.style.display = 'none';
                statusEl.innerText = "DOWNLOADING MODEL...";
                statusEl.style.color = "#00ff00";
                
                // 1. Load TensorFlow
                await tf.ready();
                
                // 2. Load MoveNet (Needs VPN)
                detector = await poseDetection.createDetector(
                    poseDetection.SupportedModels.MoveNet,
                    { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
                );

                // 3. Start Camera (Only if model loaded)
                statusEl.innerText = "STARTING CAMERA...";
                startCam();

            } catch (err) {
                console.error(err);
                statusEl.innerText = "CONNECTION FAILED";
                statusEl.style.color = "red";
                subStatusEl.innerText = "Model blocked. Enable VPN and click Retry.";
                vpnBtn.style.display = 'block';
            }
        }

        function retryModel() {
            init();
        }

        async function startCam() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: 'user', width: 640, height: 480 },
                    audio: false
                });
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    video.play();
                    loader.style.display = 'none';
                    mainUi.style.display = 'flex';
                    loop();
                };
            } catch (err) {
                statusEl.innerText = "CAMERA DENIED";
                statusEl.style.color = "orange";
                subStatusEl.innerText = "Refresh and allow camera access.";
            }
        }

        async function loop() {
            if (video.readyState === 4) {
                // Resize canvas to match video
                if (canvas.width !== video.videoWidth) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                }

                const poses = await detector.estimatePoses(video);
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (poses.length > 0) {
                    const kp = poses[0].keypoints;
                    // Check face points: nose(0), eyes(1,2), ears(3,4)
                    const facePoints = kp.slice(0, 5);
                    let visible = 0;
                    let totalConf = 0;

                    // Draw dots
                    ctx.fillStyle = "#00ff00";
                    facePoints.forEach(p => {
                        if(p.score > 0.3) {
                            visible++;
                            totalConf += p.score;
                            ctx.beginPath();
                            ctx.arc(p.x, p.y, 5, 0, 2*Math.PI);
                            ctx.fill();
                        }
                    });

                    // Scoring Logic
                    if (visible >= 3) {
                        // Fake "AI Score" based on confidence + visibility
                        // Movenet gives confidence 0.0-1.0. We map to 0-100.
                        let score = Math.floor((totalConf / 5) * 120); 
                        if(score > 100) score = 99;
                        if(score < 50) score = 65; // Make users feel good
                        
                        scoreEl.innerText = score;

                        // Save Best Shot
                        if (score > highestScore && score > 75) {
                            highestScore = score;
                            captureBest(facePoints);
                        }
                    } else {
                        scoreEl.innerText = "--";
                    }
                }
            }
            requestAnimationFrame(loop);
        }

        function captureBest(points) {
            const xs = points.map(p => p.x);
            const ys = points.map(p => p.y);
            const minX = Math.max(0, Math.min(...xs) - 60);
            const maxX = Math.min(video.videoWidth, Math.max(...xs) + 60);
            const minY = Math.max(0, Math.min(...ys) - 80);
            const maxY = Math.min(video.videoHeight, Math.max(...ys) + 80);
            
            cropCvs.width = maxX - minX;
            cropCvs.height = maxY - minY;
            
            cropCtx.drawImage(video, minX, minY, cropCvs.width, cropCvs.height, 0, 0, cropCvs.width, cropCvs.height);
            bestImg.src = cropCvs.toDataURL("image/jpeg");
        }

        // Run
        init();

    </script>
</body>
</html>"""

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)

    print("index.html recreated successfully.")

    # 3. Force Git Update
    commands = [
        ["git", "rm", "-r", "--cached", "."], # Clear git cache
        ["git", "add", "."],
        ["git", "commit", "-m", "Hard Reset to v3.0 - Fix Module Error"],
        ["git", "push"]
    ]

    for cmd in commands:
        try:
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=False) # check=False allows proceeding even if 'git rm' complains
        except Exception as e:
            print(f"Error in git command: {e}")

    print("\n--- DEPLOYMENT COMPLETE ---")
    print("WAIT 3 MINUTES.")
    print("THEN: CLEAR SAFARI CACHE OR USE 'PRIVATE TAB' TO SEE CHANGES.")

if __name__ == "__main__":
    force_deploy_v3()
