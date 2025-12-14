import os
import requests
import datetime

# --- تنظیمات ---
ASSETS_DIR = "assets"
INDEX_FILE = "index.html"
HUMAN_CAM_FILE = "human_cam.html"
GENERAL_CAM_FILE = "general_cam.html"

# لینک‌های فایل‌های هوش مصنوعی
FILES_TO_DOWNLOAD = {
    "tf.min.js": "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs/dist/tf.min.js",
    "coco-ssd.min.js": "https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd/dist/coco-ssd.min.js"
}

def download_assets():
    """دانلود فایل‌های مورد نیاز"""
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    for filename, url in FILES_TO_DOWNLOAD.items():
        filepath = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            try:
                response = requests.get(url)
                with open(filepath, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print(f"Error: {e}")

def create_dashboard():
    """ساخت منوی اصلی"""
    html = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل امنیتی مرکزی</title>
    <style>
        body {{ background-color: #0f172a; color: white; font-family: Tahoma, sans-serif; text-align: center; padding: 20px; }}
        .container {{ max-width: 500px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; margin-bottom: 40px; }}
        .btn {{
            display: block; width: 100%; padding: 25px; margin: 20px 0;
            background: #1e293b; color: #fff; text-decoration: none;
            border: 2px solid #334155; border-radius: 15px; font-size: 1.3em;
            transition: 0.3s; display: flex; align-items: center; justify-content: space-between;
        }}
        .btn:hover {{ transform: scale(1.02); }}
        .btn-human:hover {{ background: #334155; border-color: #ef4444; }} /* قرمز برای امنیت */
        .btn-general:hover {{ background: #334155; border-color: #38bdf8; }} /* آبی برای عمومی */
        
        .icon {{ font-size: 1.5em; }}
        .footer {{ margin-top: 50px; color: #64748b; font-size: 0.8em; }}
        .badge {{ background: #000; padding: 5px 10px; border-radius: 10px; font-size: 0.7em; opacity: 0.7; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ انتخاب دوربین نظارتی</h1>
        
        <!-- دکمه دوربین انسان -->
        <a href="{HUMAN_CAM_FILE}" class="btn btn-human">
            <div style="text-align:right">
                <div>📷 تشخیص انسان</div>
                <div class="badge">مود امنیتی</div>
            </div>
            <span class="icon">👤</span>
        </a>
        
        <!-- دکمه دوربین عمومی -->
        <a href="{GENERAL_CAM_FILE}" class="btn btn-general">
            <div style="text-align:right">
                <div>🎥 تشخیص اشیاء</div>
                <div class="badge">مود عمومی (General)</div>
            </div>
            <span class="icon">🌍</span>
        </a>

        <div class="footer">
            سیستم نظارت خودکار | {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        </div>
    </div>
</body>
</html>
    """
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard generated.")

def get_camera_html_content(mode):
    """
    تولید محتوای HTML برای دوربین
    mode = 'human' یا 'general'
    """
    
    if mode == 'human':
        page_title = "دوربین امنیتی (انسان)"
        theme_color = "#ef4444" # قرمز
        # فقط کلاس person را فیلتر می‌کند
        js_filter_logic = 'if (prediction.class === "person" && prediction.score > detectionThreshold)'
        box_color = "#FF0000"
    else:
        page_title = "دوربین عمومی (همه اشیاء)"
        theme_color = "#38bdf8" # آبی
        # همه کلاس‌ها را قبول می‌کند به شرط حساسیت
        js_filter_logic = 'if (prediction.score > detectionThreshold)'
        box_color = "#00FFFF"

    html = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{page_title}</title>
    <script src="{ASSETS_DIR}/tf.min.js"></script>
    <script src="{ASSETS_DIR}/coco-ssd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; background: #000; color: white; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
        
        /* Toolbar */
        .toolbar {{
            background: #111; padding: 5px 10px; display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid {theme_color}; height: 60px;
        }}
        .control-group {{ display: flex; align-items: center; gap: 10px; }}
        label {{ font-size: 11px; color: #aaa; }}
        input[type=range] {{ width: 80px; accent-color: {theme_color}; }}
        button {{
            background: #222; color: white; border: 1px solid #444; padding: 5px 10px; border-radius: 5px; cursor: pointer;
        }}
        
        /* Camera Area */
        #camera-wrapper {{
            flex: 1; position: relative; background: #000; display: flex; align-items: center; justify-content: center; overflow: hidden;
        }}
        video {{ width: 100%; height: 100%; object-fit: contain; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
        
        /* Best Shot Panel */
        #best-shot-panel {{
            height: 160px; background: #0a0a0a; border-top: 1px solid #333; display: flex;
            align-items: center; padding: 10px; gap: 15px;
        }}
        .panel-info {{ flex: 1; font-size: 13px; color: #ccc; padding-right: 5px; }}
        .panel-info h3 {{ margin: 0 0 5px 0; color: {theme_color}; font-size: 16px; }}
        .shot-container {{
            width: 110px; height: 110px; background: #000; border: 2px dashed #444;
            border-radius: 8px; overflow: hidden; position: relative; display: flex; align-items: center; justify-content: center;
        }}
        .shot-container img {{ width: 100%; height: 100%; object-fit: cover; }}
        .score-badge {{
            position: absolute; bottom: 0; right: 0; background: rgba(0,0,0,0.8);
            color: {theme_color}; font-size: 10px; padding: 2px 4px; border-top-left-radius: 5px;
        }}
        
        #status-overlay {{
            position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6);
            color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; z-index: 10;
        }}
    </style>
</head>
<body>

    <div class="toolbar">
        <a href="{INDEX_FILE}" style="text-decoration: none; font-size: 20px;">🔙</a>
        <div style="font-weight: bold; color: {theme_color}; font-size: 14px;">{page_title}</div>
        <div class="control-group">
            <div style="text-align: center;">
                <label>حساسیت: <span id="sense-val">50%</span></label><br>
                <input type="range" id="sensitivity" min="10" max="90" value="50" oninput="updateSense()">
            </div>
            <button id="mute-btn" onclick="toggleMute()">🔊</button>
        </div>
    </div>

    <div id="camera-wrapper">
        <div id="status-overlay">در حال بارگذاری هوش مصنوعی...</div>
        <video id="webcam" autoplay playsinline muted></video>
        <canvas id="canvas"></canvas>
    </div>

    <div id="best-shot-panel">
        <div class="panel-info">
            <h3>شکار لحظه‌ها 🎯</h3>
            <p id="shot-desc">منتظر تشخیص...</p>
        </div>
        <div class="shot-container" id="best-shot-box">
            <span style="color: #444; font-size: 30px;">Wait</span>
        </div>
    </div>

    <script>
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('canvas');
        const statusOverlay = document.getElementById('status-overlay');
        const senseLabel = document.getElementById('sense-val');
        const senseInput = document.getElementById('sensitivity');
        const muteBtn = document.getElementById('mute-btn');
        const bestShotBox = document.getElementById('best-shot-box');
        const shotDesc = document.getElementById('shot-desc');

        let model = undefined;
        let isMuted = false;
        let detectionThreshold = 0.5;
        let bestScore = 0; 
        
        // صدا
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function beep() {{
            if (isMuted) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.frequency.value = { "600" if mode == "human" else "1200" }; // صدای متفاوت برای هر مود
            gain.gain.value = 0.05;
            osc.start();
            setTimeout(() => osc.stop(), 100);
        }}

        function toggleMute() {{
            isMuted = !isMuted;
            muteBtn.innerText = isMuted ? "🔇" : "🔊";
            muteBtn.style.opacity = isMuted ? "0.5" : "1";
        }}

        function updateSense() {{
            const val = senseInput.value;
            senseLabel.innerText = val + "%";
            detectionThreshold = val / 100;
        }}

        cocoSsd.load().then(loadedModel => {{
            model = loadedModel;
            statusOverlay.innerText = "✅ AI فعال شد";
            startCamera();
        }});

        async function startCamera() {{
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                try {{
                    const stream = await navigator.mediaDevices.getUserMedia({{
                        'audio': false,
                        'video': {{ facingMode: 'environment' }}
                    }});
                    video.srcObject = stream;
                    video.onloadedmetadata = () => {{
                        video.play();
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        detectFrame();
                    }};
                }} catch (err) {{
                    statusOverlay.innerText = "❌ خطا: دوربین در دسترس نیست";
                }}
            }}
        }}

        function detectFrame() {{
            if (!model) return;

            model.detect(video).then(predictions => {{
                renderPredictions(predictions);
                requestAnimationFrame(detectFrame);
            }});
        }}

        function renderPredictions(predictions) {{
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

            let objectFound = false;

            predictions.forEach(prediction => {{
                // منطق فیلتر بر اساس مود (تزریق شده توسط پایتون)
                {js_filter_logic} {{
                    
                    objectFound = true;
                    const [x, y, width, height] = prediction.bbox;
                    
                    // رسم کادر
                    ctx.strokeStyle = "{box_color}";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(x, y, width, height);
                    
                    // نوشتن نام شیء بالای کادر
                    ctx.fillStyle = "{box_color}";
                    ctx.font = "16px Arial";
                    ctx.fillText(prediction.class + " (" + Math.round(prediction.score*100) + "%)", x, y > 10 ? y - 5 : 10);

                    // محاسبه امتیاز برای Best Shot
                    const frameScore = prediction.score * (width * height);

                    if (frameScore > bestScore) {{
                        bestScore = frameScore;
                        updateBestShot(x, y, width, height, prediction.score, prediction.class);
                        beep();
                    }}
                }}
            }});
            
            // کاهش امتیاز تدریجی برای ریست شدن
            if (!objectFound && bestScore > 0) {{
                bestScore -= 500; 
                if(bestScore < 0) bestScore = 0;
            }}
        }}

        function updateBestShot(x, y, w, h, score, label) {{
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = w;
            tempCanvas.height = h;
            const tCtx = tempCanvas.getContext('2d');
            tCtx.drawImage(video, x, y, w, h, 0, 0, w, h);
            
            const imgUrl = tempCanvas.toDataURL('image/jpeg');

            bestShotBox.innerHTML = `
                <img src="${{imgUrl}}">
                <div class="score-badge">${{label}}</div>
            `;
            
            const time = new Date().toLocaleTimeString();
            shotDesc.innerHTML = `
                <span style="color:{theme_color}">✅ ${{label}}</span><br>
                دقت: ${{Math.round(score * 100)}}%<br>
                <span style="color:#666; font-size:10px">${{time}}</span>
            `;
        }}
    </script>
</body>
</html>
    """
    return html

def create_camera_files():
    """تولید دو فایل دوربین جداگانه"""
    
    # 1. ساخت دوربین انسان
    print("Generating Human Camera...")
    human_html = get_camera_html_content("human")
    with open(HUMAN_CAM_FILE, "w", encoding="utf-8") as f:
        f.write(human_html)

    # 2. ساخت دوربین عمومی
    print("Generating General Camera...")
    general_html = get_camera_html_content("general")
    with open(GENERAL_CAM_FILE, "w", encoding="utf-8") as f:
        f.write(general_html)

if __name__ == "__main__":
    download_assets()
    create_dashboard()
    create_camera_files()
