import os
import shutil
import subprocess

def hard_reset_and_build():
    print("--- STARTING HARD RESET & BUILD ---")
    
    # 1. CLEANUP: Delete everything except .git and this script
    # این بخش تضمین می‌کند که فایل index.html قدیمی که دکمه‌های قرمز/آبی داشت حتما پاک شود
    current_dir = os.getcwd()
    print("Step 1: Cleaning up old files...")
    for item in os.listdir(current_dir):
        if item == ".git" or item.endswith(".py"):
            continue
        
        item_path = os.path.join(current_dir, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"   Warning: Could not delete {item}: {e}")

    # 2. CREATE DIAGNOSTIC TOOL (Root Directory)
    print("Step 2: Creating Diagnostic Tool...")
    diag_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Check</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        .step { border: 1px solid #333; margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { color: #0f0; border-color: #0f0; }
        .error { color: #f00; border-color: #f00; }
        button { width: 100%; padding: 15px; font-size: 1.2rem; background: #333; color: white; border: none; margin-bottom: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <h2>SYSTEM DIAGNOSTICS</h2>
    <button onclick="runTest()">START TEST</button>
    <div id="logs"></div>
    <script>
        const log = (msg, type='neutral') => {
            const div = document.createElement('div');
            div.className = 'step ' + type;
            div.innerHTML = msg;
            document.getElementById('logs').appendChild(div);
        }

        async function runTest() {
            document.getElementById('logs').innerHTML = '';
            
            // Test 1: CDN
            log('Checking Internet/CDN...');
            try {
                await fetch('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js', {method:'HEAD'});
                log('CDN Connection: OK', 'success');
            } catch(e) {
                log('CDN Failed (Check VPN): ' + e.message, 'error');
                return;
            }

            // Test 2: Camera
            log('Checking Camera Permissions...');
            try {
                const stream = await navigator.mediaDevices.getUserMedia({video:true});
                stream.getTracks().forEach(t=>t.stop());
                log('Camera Access: OK', 'success');
            } catch(e) {
                log('Camera Blocked: ' + e.message, 'error');
                return;
            }

            // Test 3: TFJS
            log('Loading TensorFlow...');
            try {
                await import('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js');
                await import('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js');
                await import('https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js');
                log('Libraries Loaded: OK', 'success');
            } catch(e) {
                log('Library Load Failed: ' + e.message, 'error');
                return;
            }

            // Test 4: Model
            log('Downloading AI Model...');
            try {
                await tf.ready();
                const detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING});
                log('Model Downloaded: OK', 'success');
                
                // Final Success
                log('ALL SYSTEMS GO. <a href="camera.html" style="color:white;font-weight:bold;">[ OPEN CAMERA ]</a>', 'success');
            } catch(e) {
                log('Model Error (VPN?): ' + e.message, 'error');
            }
        }
    </script>
</body>
</html>"""
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(diag_content)

    # 3. CREATE CAMERA TOOL
    print("Step 3: Creating Camera Tool...")
    cam_content = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
    <style>body{margin:0;background:black;overflow:hidden} video,canvas{position:absolute;width:100%;height:100%}</style>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>
    <video id="v" playsinline muted autoplay></video>
    <canvas id="c"></canvas>
    <script>
        async function run() {
            const v = document.getElementById('v');
            const c = document.getElementById('c');
            const ctx = c.getContext('2d');
            
            const stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'}});
            v.srcObject = stream;
            await new Promise(r => v.onloadedmetadata = r);
            v.play();
            c.width = v.videoWidth; c.height = v.videoHeight;

            await tf.ready();
            const detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING});

            async function frame() {
                const poses = await detector.estimatePoses(v);
                ctx.clearRect(0,0,c.width,c.height);
                poses.forEach(p => {
                    p.keypoints.forEach(k => {
                        if(k.score > 0.3) {
                            ctx.beginPath(); ctx.arc(k.x, k.y, 8, 0, 2*Math.PI);
                            ctx.fillStyle = '#00ff00'; ctx.fill();
                        }
                    });
                });
                requestAnimationFrame(frame);
            }
            frame();
        }
        run();
    </script>
</body>
</html>"""
    with open("camera.html", "w", encoding='utf-8') as f:
        f.write(cam_content)

    # 4. GIT PUSH
    print("Step 4: Pushing changes...")
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=False)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=False)
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Hard Reset: Clean Root Install"], check=False)
    subprocess.run(["git", "push"], check=False)
    
    print("\n--- DONE. Website should update in 1-2 minutes. ---")
    print("Please clear browser cache if you still see the red/blue buttons.")

if __name__ == "__main__":
    hard_reset_and_build()
