import os
import subprocess

def deploy_final_app():
    print("--- BUILDING FINAL SECURITY CAMERA APP ---")
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Smart CCTV</title>
    <style>
        body { margin: 0; background: #000; overflow: hidden; font-family: sans-serif; }
        #video-container { position: relative; width: 100vw; height: 100vh; }
        video { width: 100%; height: 100%; object-fit: cover; }
        canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        
        /* UI Overlay */
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; display: flex; flex-direction: column; justify-content: space-between; padding: 20px; box-sizing: border-box; }
        
        .header { display: flex; justify-content: space-between; align-items: center; }
        .status-badge { background: rgba(0, 255, 0, 0.2); color: #0f0; padding: 5px 15px; border-radius: 4px; border: 1px solid #0f0; font-weight: bold; text-shadow: 0 0 5px #0f0; }
        .status-danger { background: rgba(255, 0, 0, 0.3); color: #ff0000; border-color: #ff0000; text-shadow: 0 0 10px #ff0000; animation: pulse 0.5s infinite alternate; }
        
        .footer { text-align: center; pointer-events: auto; }
        button { background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid white; padding: 15px 30px; border-radius: 30px; font-size: 16px; backdrop-filter: blur(5px); cursor: pointer; transition: 0.3s; }
        button:active { background: white; color: black; }

        @keyframes pulse { from { opacity: 0.5; } to { opacity: 1; } }
        
        #loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00bcd4; font-size: 20px; font-weight: bold; }
    </style>
    <!-- Load AI Libraries from CDN (Verified Working) -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>

    <div id="video-container">
        <video id="cam" playsinline muted autoplay></video>
        <canvas id="output"></canvas>
        <div id="loading">INITIALIZING AI SYSTEM...</div>
        
        <div id="ui-layer">
            <div class="header">
                <div style="color:white; font-size:14px;">CAM-01 • LIVE</div>
                <div id="status" class="status-badge">SECURE</div>
            </div>
            <div class="footer">
                <button onclick="switchCamera()">🔄 Switch Camera</button>
            </div>
        </div>
    </div>

    <script>
        let detector;
        let video = document.getElementById('cam');
        let canvas = document.getElementById('output');
        let ctx = canvas.getContext('2d');
        let statusEl = document.getElementById('status');
        let currentStream = null;
        let isFrontCam = false;

        async function setupCamera() {
            const constraints = {
                video: {
                    facingMode: isFrontCam ? 'user' : 'environment',
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: false
            };
            
            if (currentStream) {
                currentStream.getTracks().forEach(t => t.stop());
            }

            currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = currentStream;
            
            return new Promise((resolve) => {
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
            detectFrame();
        }

        async function detectFrame() {
            // Resize canvas to match video
            if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            }

            const poses = await detector.estimatePoses(video);
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            let humanDetected = false;

            poses.forEach(pose => {
                // If we see points with high confidence, consider it a human
                const goodPoints = pose.keypoints.filter(k => k.score > 0.3);
                
                if (goodPoints.length > 5) { // At least 5 body parts visible
                    humanDetected = true;
                    drawSkeleton(pose.keypoints);
                }
            });

            updateStatus(humanDetected);
            requestAnimationFrame(detectFrame);
        }

        function drawSkeleton(keypoints) {
            // Draw connections
            const adj = poseDetection.util.getAdjacentPairs(poseDetection.SupportedModels.MoveNet);
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 2;
            
            adj.forEach(([i, j]) => {
                const kp1 = keypoints[i];
                const kp2 = keypoints[j];
                if (kp1.score > 0.3 && kp2.score > 0.3) {
                    ctx.beginPath();
                    ctx.moveTo(kp1.x, kp1.y);
                    ctx.lineTo(kp2.x, kp2.y);
                    ctx.stroke();
                }
            });

            // Draw Box around detected person roughly
            const x = keypoints.map(k => k.x);
            const y = keypoints.map(k => k.y);
            const minX = Math.min(...x);
            const maxX = Math.max(...x);
            const minY = Math.min(...y);
            const maxY = Math.max(...y);
            
            ctx.strokeStyle = 'red';
            ctx.lineWidth = 4;
            ctx.strokeRect(minX - 20, minY - 20, (maxX - minX) + 40, (maxY - minY) + 40);
        }

        function updateStatus(detected) {
            if (detected) {
                statusEl.innerText = "⚠️ INTRUDER DETECTED";
                statusEl.className = "status-badge status-danger";
            } else {
                statusEl.innerText = "SECURE";
                statusEl.className = "status-badge";
            }
        }

        window.switchCamera = function() {
            isFrontCam = !isFrontCam;
            setupCamera();
        }

        // Start
        setupCamera().then(loadModel).catch(e => {
            alert("Camera Error: " + e.message);
        });

    </script>
</body>
</html>"""
    
    # Overwrite index.html directly
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)

    # Git commands
    print("Pushing to GitHub...")
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=False)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=False)
    subprocess.run(["git", "add", "index.html"], check=False)
    subprocess.run(["git", "commit", "-m", "Update to Full Security App"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("DONE! Website updated.")

if __name__ == "__main__":
    deploy_final_app()
