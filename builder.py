import os
import shutil
import subprocess

# --- تنظیمات ---
ROOT_DIR = "smart-tools"

def clean_and_setup():
    """پاکسازی و آماده‌سازی محیط"""
    if os.path.exists(ROOT_DIR):
        shutil.rmtree(ROOT_DIR)
    os.makedirs(ROOT_DIR, exist_ok=True)

def create_diagnostic_tool():
    """ساخت ابزار تست خط به خط (Unit Test در مرورگر)"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Diagnostics</title>
    <style>
        body { background: #121212; color: #fff; font-family: monospace; padding: 20px; }
        h2 { border-bottom: 1px solid #333; padding-bottom: 10px; }
        .step { margin: 10px 0; padding: 10px; background: #1e1e1e; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .step.pending { border-left: 4px solid #888; }
        .step.success { border-left: 4px solid #0f0; background: #1a2e1a; }
        .step.error { border-left: 4px solid #f00; background: #2e1a1a; }
        .status { font-weight: bold; }
        #final-result { margin-top: 20px; padding: 15px; text-align: center; display: none; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; margin-bottom: 20px;}
    </style>
    
    <!-- لود اسکریپت‌ها به صورت دستی در کد انجام می‌شود تا تست شود -->
</head>
<body>
    <h2>🔍 Step-by-Step Diagnostics</h2>
    <p>Press "Start Test" to execute code line-by-line.</p>
    <button onclick="runDiagnostics()">▶ Start Test</button>

    <div id="steps-container"></div>
    <div id="final-result"></div>

    <script>
        // لیست مراحل تست
        const steps = [
            { id: 'cdn', name: '1. Check CDN Connection (Internet)' },
            { id: 'camera', name: '2. Check Camera Access' },
            { id: 'tf_load', name: '3. Load TensorFlow.js Library' },
            { id: 'backend', name: '4. Initialize WebGL Backend' },
            { id: 'model_load', name: '5. Download MoveNet Model' },
            { id: 'inference', name: '6. Run Test Prediction' }
        ];

        const container = document.getElementById('steps-container');
        
        // ساخت UI مراحل
        steps.forEach(step => {
            container.innerHTML += `
                <div id="step-${step.id}" class="step pending">
                    <span>${step.name}</span>
                    <span class="status" id="status-${step.id}">WAITING</span>
                </div>`;
        });

        function updateStep(id, status, msg = '') {
            const el = document.getElementById(`step-${id}`);
            const st = document.getElementById(`status-${id}`);
            el.className = `step ${status}`;
            st.innerHTML = status === 'success' ? '✅ OK' : '❌ FAILED';
            if(msg) st.innerHTML += `<br><small>${msg}</small>`;
        }

        async function loadScript(url) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = url;
                script.onload = resolve;
                script.onerror = () => reject(new Error(`Failed to load ${url}`));
                document.head.appendChild(script);
            });
        }

        async function runDiagnostics() {
            // --- STEP 1: CDN Check ---
            try {
                const response = await fetch('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js', { method: 'HEAD' });
                if(!response.ok) throw new Error("HTTP " + response.status);
                updateStep('cdn', 'success');
            } catch (e) {
                updateStep('cdn', 'error', 'VPN Required! ' + e.message);
                return; // Stop execution
            }

            // --- STEP 2: Camera ---
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                updateStep('camera', 'success');
                // Stop stream immediately
                stream.getTracks().forEach(track => track.stop());
            } catch (e) {
                updateStep('camera', 'error', 'Permission Denied or Insecure Context (Use HTTPS)');
                return;
            }

            // --- STEP 3: Load Libraries ---
            try {
                await loadScript('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js');
                await loadScript('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js');
                await loadScript('https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js');
                
                if(typeof tf === 'undefined') throw new Error("tf object missing");
                updateStep('tf_load', 'success');
            } catch (e) {
                updateStep('tf_load', 'error', e.message);
                return;
            }

            // --- STEP 4: Backend ---
            try {
                await tf.ready();
                const backend = tf.getBackend();
                updateStep('backend', 'success', `Backend: ${backend}`);
            } catch (e) {
                updateStep('backend', 'error', e.message);
                return;
            }

            // --- STEP 5: Model Load ---
            let detector;
            try {
                const modelType = poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING;
                detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, { modelType });
                updateStep('model_load', 'success');
            } catch (e) {
                updateStep('model_load', 'error', 'Model download failed. Check VPN.');
                console.error(e);
                return;
            }

            // --- STEP 6: Inference Test ---
            try {
                // Create a dummy image (black square)
                const dummyCanvas = document.createElement('canvas');
                dummyCanvas.width = 640; dummyCanvas.height = 480;
                const poses = await detector.estimatePoses(dummyCanvas);
                updateStep('inference', 'success', `Detected: ${poses.length} poses`);
                
                // Show Success Message
                document.getElementById('final-result').style.display = 'block';
                document.getElementById('final-result').innerHTML = '<h3 style="color:#0f0">🎉 SYSTEM FULLY OPERATIONAL</h3><a href="human_cam.html" style="color:#fff; text-decoration:underline;">Go to Main Camera</a>';
                
            } catch (e) {
                updateStep('inference', 'error', e.message);
            }
        }
    </script>
</body>
</html>"""
    with open(os.path.join(ROOT_DIR, "diagnostic.html"), "w") as f:
        f.write(html_content)

def create_main_app():
    """نسخه اصلی برنامه (Human Cam) - در صورت موفقیت تست، کاربر به اینجا می‌آید"""
    content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Human Detection</title>
    <style>body{margin:0;background:#000;overflow:hidden}video,canvas{position:absolute;width:100%;height:100%;object-fit:cover}</style>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.18.0/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl@3.18.0/dist/tf-backend-webgl.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.0.0/dist/pose-detection.js"></script>
</head>
<body>
    <video id="video" playsinline muted autoplay></video>
    <canvas id="canvas"></canvas>
    <script>
        async function start() {
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            
            const stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});
            video.srcObject = stream;
            await new Promise(r => video.onloadedmetadata = r);
            video.play();
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            await tf.ready();
            const detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING});
            
            async function render() {
                if(canvas.width !== video.videoWidth) { canvas.width = video.videoWidth; canvas.height = video.videoHeight; }
                const poses = await detector.estimatePoses(video);
                ctx.clearRect(0,0,canvas.width,canvas.height);
                poses.forEach(pose => {
                    pose.keypoints.forEach(k => {
                        if(k.score > 0.3) {
                            ctx.beginPath(); ctx.arc(k.x, k.y, 5, 0, 2*Math.PI);
                            ctx.fillStyle='aqua'; ctx.fill();
                        }
                    });
                });
                requestAnimationFrame(render);
            }
            render();
        }
        start();
    </script>
</body>
</html>"""
    with open(os.path.join(ROOT_DIR, "human_cam.html"), "w") as f:
        f.write(content)

def create_index():
    content = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: sans-serif; background: #222; color: white; text-align: center; padding-top: 50px; }
a { display: block; background: #FF9800; padding: 20px; color: white; margin: 20px auto; width: 80%; max-width: 300px; text-decoration: none; border-radius: 10px; font-size: 1.2rem;}
</style>
</head>
<body>
    <h1>AI Tools Hub</h1>
    <p>Please run the Diagnostic first to identify issues.</p>
    <a href="diagnostic.html">🛠 Run System Diagnostics</a>
    <a href="human_cam.html" style="background:#444">👤 Direct Camera Link</a>
</body>
</html>"""
    with open(os.path.join(ROOT_DIR, "index.html"), "w") as f:
        f.write(content)

def push_changes():
    subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=False)
    subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=False)
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Add Step-by-Step Diagnostic Tool"], check=False)
    subprocess.run(["git", "push"], check=False)

if __name__ == "__main__":
    clean_and_setup()
    create_diagnostic_tool()
    create_main_app()
    create_index()
    push_changes()
