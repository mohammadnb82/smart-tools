import os
import requests
import json
import shutil

# --- تنظیمات ---
ASSETS_DIR = "assets"
MOVENET_DIR = os.path.join(ASSETS_DIR, "movenet")

# لیست کتابخانه‌های JS
LIBRARIES = {
    "tf-core.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-core",
    "tf-converter.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-converter",
    "tf-backend-webgl.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-webgl",
    "pose-detection.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection",
    "tf.min.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs", 
    "coco-ssd.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd"
}

# آدرس مدل MoveNet Lightning (نسخه سبک و سریع)
MOVENET_BASE_URL = "https://storage.googleapis.com/tfjs-models/savedmodel/movenet/singlepose/lightning/4/"
MOVENET_JSON = "model.json"

# --- 1. دانلودر هوشمند (JS + AI Models) ---
def manage_assets():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
    
    # الف) دانلود کتابخانه‌های JS
    print("[-] Checking JS Libraries...")
    for filename, url in LIBRARIES.items():
        filepath = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"   [Downloading Lib] {filename}...")
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(r.content)
                else:
                    print(f"   [!] Error downloading {filename}")
            except Exception as e:
                print(f"   [!] Exception: {e}")
        else:
            print(f"   [OK] {filename}")

    # ب) دانلود مدل هوش مصنوعی (MoveNet) بصورت کامل
    if not os.path.exists(MOVENET_DIR):
        os.makedirs(MOVENET_DIR)
    
    print("[-] Checking MoveNet AI Model...")
    model_json_path = os.path.join(MOVENET_DIR, "model.json")
    
    # 1. دانلود فایل JSON مدل
    if not os.path.exists(model_json_path):
        print("   [Downloading Model JSON]...")
        r = requests.get(MOVENET_BASE_URL + MOVENET_JSON)
        if r.status_code == 200:
            with open(model_json_path, "wb") as f:
                f.write(r.content)
            print("   [Saved] model.json")
        else:
            print("   [FATAL] Could not download model.json")
            return

    # 2. خواندن JSON برای پیدا کردن فایل‌های باینری (Weights)
    try:
        with open(model_json_path, "r") as f:
            model_data = json.load(f)
            
        # استخراج نام فایل‌های باینری (.bin)
        if 'weightsManifest' in model_data:
            for manifest in model_data['weightsManifest']:
                for bin_filename in manifest['paths']:
                    bin_path = os.path.join(MOVENET_DIR, bin_filename)
                    if not os.path.exists(bin_path):
                        print(f"   [Downloading Weight] {bin_filename}...")
                        bin_url = MOVENET_BASE_URL + bin_filename
                        r = requests.get(bin_url)
                        if r.status_code == 200:
                            with open(bin_path, "wb") as bf:
                                bf.write(r.content)
                        else:
                            print(f"   [!] Failed to download weight: {bin_filename}")
            print("   [OK] All MoveNet files are ready.")
    except Exception as e:
        print(f"   [!] Error parsing model: {e}")


# --- 2. تولید صفحات HTML (با آدرس دهی لوکال دقیق) ---

def generate_human_cam():
    # نکته مهم: در اینجا modelUrl را به فایل لوکال ارجاع می‌دهیم
    html_content = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>تشخیص آناتومی انسان</title>
    <style>
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; user-select: none; }}
        body {{
            margin: 0; padding: 0; background: #000; color: #fff;
            font-family: sans-serif; height: 100vh; width: 100vw;
            display: flex; flex-direction: column; overflow: hidden;
        }}
        #header {{
            position: absolute; top: 0; left: 0; right: 0; padding: 10px;
            background: linear-gradient(to bottom, rgba(0,0,0,0.9), transparent);
            z-index: 100; display: flex; justify-content: space-between; align-items: center;
        }}
        .controls {{ display: flex; align-items: center; gap: 10px; }}
        .btn {{ border: 1px solid #555; color: #eee; padding: 5px 10px; border-radius: 15px; text-decoration: none; font-size: 12px; background: rgba(0,0,0,0.5); }}
        #viewport {{
            flex: 1; position: relative; display: flex; justify-content: center; align-items: center; background: #111;
        }}
        video, canvas {{ position: absolute; max-width: 100%; max-height: 100%; width: auto; height: auto; }}
        #gallery {{
            height: 140px; background: #111; border-top: 1px solid #333;
            display: flex; align-items: center; padding: 5px; overflow-x: auto; gap: 8px; z-index: 101;
        }}
        .card {{
            position: relative; flex: 0 0 auto; width: 100px; height: 120px;
            background: #000; border-radius: 8px; overflow: hidden; border: 2px solid #333;
        }}
        .card img {{ width: 100%; height: 90px; object-fit: cover; }}
        .card-meta {{
            height: 30px; font-size: 9px; padding: 2px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            background: #222; color: #aaa; text-align: center;
        }}
        .score-high {{ color: #0f0; font-weight: bold; }}
        #error-log {{
            position: absolute; bottom: 150px; left: 10px; right: 10px;
            color: red; background: rgba(0,0,0,0.8); padding: 5px; font-size: 10px;
            display: none; z-index: 200; pointer-events: none;
        }}
    </style>
    
    <script src="{ASSETS_DIR}/tf-core.js"></script>
    <script src="{ASSETS_DIR}/tf-converter.js"></script>
    <script src="{ASSETS_DIR}/tf-backend-webgl.js"></script>
    <script src="{ASSETS_DIR}/pose-detection.js"></script>
</head>
<body>
    <div id="header">
        <div class="controls">
            <span id="mute-btn">🔊</span>
            <div style="font-size:10px;">
                حساسیت: <b id="sen-txt">50%</b>
                <input type="range" id="sensitivity" min="20" max="90" value="50" style="width:70px">
            </div>
        </div>
        <div style="color:#ff0055; font-weight:bold; font-size:14px;">تشخیص هویت (چهره)</div>
        <a href="index.html" class="btn">BACK</a>
    </div>
    
    <div id="status" style="position:absolute; top:60px; right:10px; z-index:90; font-size:12px; color:yellow;">Initializing System...</div>
    <div id="error-log"></div>

    <div id="viewport">
        <video id="video" autoplay playsinline muted></video>
        <canvas id="canvas"></canvas>
    </div>

    <div id="gallery"></div>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const gallery = document.getElementById('gallery');
        const statusEl = document.getElementById('status');
        const errorLog = document.getElementById('error-log');
        
        let detector = null;
        let isMuted = false;
        let sensitivity = 0.5;
        let subjects = []; 

        function logError(msg) {{
            errorLog.style.display = 'block';
            errorLog.innerText += "\\n" + msg;
            console.error(msg);
        }}

        // Audio Context
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function beep() {{
            if(isMuted) return;
            if(audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.frequency.value = 600;
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);
            osc.stop(audioCtx.currentTime + 0.1);
        }}
        document.getElementById('mute-btn').onclick = function() {{ isMuted = !isMuted; this.innerText = isMuted ? '🔇' : '🔊'; }};
        document.getElementById('sensitivity').oninput = (e) => {{ sensitivity = e.target.value / 100; document.getElementById('sen-txt').innerText = e.target.value+'%'; }};

        async function setupCamera() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ 
                    video: {{ facingMode: 'environment', width: {{ ideal: 640 }}, height: {{ ideal: 480 }} }}, 
                    audio: false 
                }});
                video.srcObject = stream;
                return new Promise(resolve => {{ video.onloadedmetadata = () => {{ video.play(); resolve(); }}; }});
            }} catch(e) {{
                logError("Camera Error: " + e.message);
                statusEl.innerText = "Camera Fail";
            }}
        }}

        function analyzePose(keypoints) {{
            let faceScore = 0;
            let bodyScore = 0;
            
            // 0:nose, 1:left_eye, 2:right_eye, 3:left_ear, 4:right_ear
            keypoints.forEach((kp, index) => {{
                if (kp.score > sensitivity) {{
                    if (index <= 4) {{
                        faceScore += 100; 
                    }} else {{
                        bodyScore += 1;
                    }}
                }}
            }});
            
            const totalScore = faceScore + bodyScore;
            
            let sumX = 0, count = 0;
            keypoints.forEach(kp => {{ if(kp.score > sensitivity) {{ sumX += kp.x; count++; }} }});
            const centerX = count > 0 ? sumX / count : 0;

            return {{ totalScore, faceScore, bodyScore, centerX, keypoints }};
        }}

        function updateGallery(poseData, videoEl) {{
            if (poseData.totalScore < 1) return; 

            let matchIndex = -1;
            let minDist = 100; 

            for(let i=0; i<subjects.length; i++) {{
                if (Math.abs(subjects[i].centerX - poseData.centerX) < minDist) {{
                    matchIndex = i;
                    break;
                }}
            }}

            if (matchIndex !== -1) {{
                const sub = subjects[matchIndex];
                sub.centerX = poseData.centerX;
                sub.lastSeen = Date.now();

                if (poseData.totalScore > sub.bestTotalScore) {{
                    sub.bestTotalScore = poseData.totalScore;
                    captureImage(sub.id, poseData, "UPDATED");
                }}
            }} else {{
                const newId = 'person-' + Date.now();
                subjects.push({{
                    id: newId,
                    centerX: poseData.centerX,
                    bestTotalScore: poseData.totalScore,
                    lastSeen: Date.now()
                }});
                createCard(newId);
                captureImage(newId, poseData, "NEW");
                beep();
            }}
        }}

        function createCard(id) {{
            const d = document.createElement('div');
            d.className = 'card'; d.id = id;
            d.innerHTML = `<img src=""><div class="card-meta">Analyzing...</div>`;
            gallery.prepend(d);
        }}

        function captureImage(id, poseData, statusLabel) {{
            const card = document.getElementById(id);
            if(!card) return;
            
            let minX=video.videoWidth, minY=video.videoHeight, maxX=0, maxY=0;
            poseData.keypoints.forEach(kp => {{
                if(kp.score > 0.3) {{
                    if(kp.x < minX) minX = kp.x;
                    if(kp.x > maxX) maxX = kp.x;
                    if(kp.y < minY) minY = kp.y;
                    if(kp.y > maxY) maxY = kp.y;
                }}
            }});
            const pad = 30;
            minX = Math.max(0, minX - pad);
            minY = Math.max(0, minY - pad);
            const w = Math.min(video.videoWidth - minX, (maxX - minX) + 2*pad);
            const h = Math.min(video.videoHeight - minY, (maxY - minY) + 2*pad);

            if (w <= 0 || h <= 0) return;

            const tCanvas = document.createElement('canvas');
            tCanvas.width = w; tCanvas.height = h;
            tCanvas.getContext('2d').drawImage(video, minX, minY, w, h, 0, 0, w, h);
            
            card.querySelector('img').src = tCanvas.toDataURL('image/jpeg');
            
            let desc = "";
            let scoreClass = "";
            
            if (poseData.faceScore >= 100) {{
                desc = "چهره شناسایی شد!";
                scoreClass = "score-high";
            }} else {{
                desc = "فقط بدن";
                scoreClass = "";
            }}
            
            const facePartsCount = poseData.faceScore / 100;
            card.querySelector('.card-meta').innerHTML = `<span class="${{scoreClass}}">${{desc}}</span><br>Parts: ${{Math.floor(facePartsCount)}}`;
            
            card.style.borderColor = '#fff';
            setTimeout(() => card.style.borderColor = poseData.faceScore > 0 ? '#0f0' : '#ff0055', 300);
        }}

        async function detect() {{
            if (!detector) return;
            
            try {{
                const poses = await detector.estimatePoses(video, {{
                    maxPoses: 1,
                    flipHorizontal: false
                }});
                
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                poses.forEach(pose => {{
                    drawSkeleton(pose.keypoints);
                    const data = analyzePose(pose.keypoints);
                    if (data.totalScore > 0) {{
                        updateGallery(data, video);
                    }}
                }});
            }} catch(err) {{
                logError("Detect Error: " + err);
            }}
            
            requestAnimationFrame(detect);
        }}
        
        function drawSkeleton(keypoints) {{
            keypoints.forEach((kp, index) => {{
                if(kp.score > sensitivity) {{
                   ctx.beginPath();
                   ctx.arc(kp.x, kp.y, 4, 0, 2*Math.PI);
                   ctx.fillStyle = index <= 4 ? '#00ff00' : '#ff0055';
                   ctx.fill();
                }}
            }});
            
            const adjacentPairs = poseDetection.util.getAdjacentPairs(poseDetection.SupportedModels.MoveNet);
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1;
            adjacentPairs.forEach(([i, j]) => {{
                const kp1 = keypoints[i];
                const kp2 = keypoints[j];
                if(kp1.score > sensitivity && kp2.score > sensitivity) {{
                    ctx.beginPath();
                    ctx.moveTo(kp1.x, kp1.y);
                    ctx.lineTo(kp2.x, kp2.y);
                    ctx.stroke();
                }}
            }});
        }}

        async function main() {{
            statusEl.innerText = "Camera Start...";
            await setupCamera();
            
            statusEl.innerText = "Loading AI Core...";
            try {{
                await tf.ready();
                await tf.setBackend('webgl');
                
                statusEl.innerText = "Loading Local Model...";
                
                // --- بارگذاری مدل از پوشه لوکال ---
                detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {{
                    modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING,
                    modelUrl: '{ASSETS_DIR}/movenet/model.json' 
                }});
                
                statusEl.innerText = "";
                detect();
            }} catch(e) {{
                statusEl.innerText = "AI FAILED";
                logError("Setup Error: " + e.message + "\\n" + e.stack);
                alert("خطا در بارگذاری هوش مصنوعی: " + e.message);
            }}
        }}

        main();
    </script>
</body>
</html>
    """
    with open("human_cam.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[Generate] human_cam.html created (OFFLINE MODE).")

# (بخش general_cam و index تغییر خاصی لازم ندارند اما برای تکمیل بودن کد دوباره می‌آورم)
def generate_general_cam():
    html_content = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>دوربین عمومی</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; background: #000; color: #fff; height: 100vh; display: flex; flex-direction: column; overflow: hidden; font-family: sans-serif; }}
        #header {{ position: absolute; top:0; left:0; right:0; padding:10px; background:rgba(0,0,0,0.7); z-index:10; display:flex; justify-content:space-between; }}
        #viewport {{ flex:1; position:relative; display:flex; justify-content:center; align-items:center; background:#111; }}
        video, canvas {{ position:absolute; max-width:100%; max-height:100%; }}
        #gallery {{ height:130px; background:#111; display:flex; overflow-x:auto; padding:5px; gap:5px; z-index:11; }}
        .card {{ width:100px; height:120px; background:#222; border:1px solid #00aaff; border-radius:5px; flex:0 0 auto; overflow:hidden; }}
        .card img {{ width:100%; height:90px; object-fit:cover; }}
        .card div {{ font-size:10px; text-align:center; padding:2px; color:#00aaff; }}
        .btn {{ color:#fff; text-decoration:none; border:1px solid #fff; padding:3px 8px; border-radius:10px; font-size:12px; }}
    </style>
    <script src="{ASSETS_DIR}/tf.min.js"></script>
    <script src="{ASSETS_DIR}/coco-ssd.js"></script>
</head>
<body>
    <div id="header">
        <div style="color:#00aaff;">دوربین عمومی</div>
        <a href="index.html" class="btn">بازگشت</a>
    </div>
    <div id="status" style="position:absolute; top:50px; left:10px; color:yellow; font-size:12px;">Loading Model...</div>
    <div id="viewport">
        <video id="webcam" autoplay playsinline muted></video>
        <canvas id="canvas"></canvas>
    </div>
    <div id="gallery"></div>
    <script>
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const gallery = document.getElementById('gallery');
        const statusEl = document.getElementById('status');
        let model = null;

        async function setup() {{
            const stream = await navigator.mediaDevices.getUserMedia({{video:{{facingMode:'environment'}}, audio:false}});
            video.srcObject = stream;
            return new Promise(r => {{ video.onloadedmetadata = () => {{ video.play(); r(); }} }});
        }}

        function addCard(prediction) {{
            const d = document.createElement('div');
            d.className = 'card';
            const [x,y,w,h] = prediction.bbox;
            const tCanvas = document.createElement('canvas');
            tCanvas.width = w; tCanvas.height = h;
            tCanvas.getContext('2d').drawImage(video, x, y, w, h, 0, 0, w, h);
            d.innerHTML = `<img src="${{tCanvas.toDataURL()}}"><div>${{prediction.class}} ${{Math.round(prediction.score*100)}}%</div>`;
            gallery.prepend(d);
        }}

        async function run() {{
            await setup();
            statusEl.innerText = "Loading COCO-SSD...";
            // توجه: کوکو-اس‌اس‌دی هنوز تلاش می‌کند از اینترنت مدل بگیرد چون مدیریت آن پیچیده‌تر است
            // اما چون فایل‌های اصلی JS لوکال هستند سرعت لود بهتر است
            try {{
                model = await cocoSsd.load();
                statusEl.innerText = "";
                setInterval(async () => {{
                    const preds = await model.detect(video);
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.clearRect(0,0,canvas.width,canvas.height);
                    preds.forEach(p => {{
                        if(p.score > 0.6) {{
                            ctx.strokeStyle = '#00aaff'; ctx.lineWidth = 2; ctx.strokeRect(...p.bbox);
                            if (Math.random() > 0.98) addCard(p); 
                        }}
                    }});
                }}, 100);
            }} catch(e) {{
                statusEl.innerText = "Load Failed (Need Internet for Model)";
            }}
        }}
        run();
    </script>
</body>
</html>
    """
    with open("general_cam.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[Generate] general_cam.html created.")

def generate_index():
    html_content = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل امنیتی هوشمند</title>
    <style>
        body { background: #111; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .btn {
            display: block; width: 85%; max-width: 400px; margin: 20px auto; padding: 25px;
            border-radius: 20px; text-decoration: none; font-size: 20px; font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: transform 0.2s;
        }
        .btn:active { transform: scale(0.95); }
        .human { background: linear-gradient(45deg, #ff0055, #ff5500); color: white; }
        .general { background: linear-gradient(45deg, #0055ff, #00aaff); color: white; }
    </style>
</head>
<body>
    <h2>سیستم نظارتی هوشمند</h2>
    <a href="human_cam.html" class="btn human">تشخیص آناتومی و چهره 🧠<br><span style="font-size:12px; opacity:0.8">(کاملاً آفلاین و سریع)</span></a>
    <a href="general_cam.html" class="btn general">تشخیص عمومی اشیاء 📷<br><span style="font-size:12px; opacity:0.8">(ماشین، کیف، حیوانات)</span></a>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[Generate] index.html created.")

# --- اجرای برنامه ---
if __name__ == "__main__":
    manage_assets() 
    generate_human_cam()
    generate_general_cam()
    generate_index()
    print("\n--- SYSTEM READY FOR GITHUB UPLOAD ---")
