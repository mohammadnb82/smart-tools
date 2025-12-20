import os
import shutil

# مسیر پوشه هدف
folder_path = "tools/doorbin-tashkhis-harekat"

# 1. پاک‌سازی فایل‌های قبلی
if os.path.exists(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
else:
    os.makedirs(folder_path)

# 2. محتوای HTML/JS اصلاح شده (رفع باگ صدا و دوربین جلو)
html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Motion Detector Final</title>
<style>
:root { --bg: #000; --card: #1c1c1e; --text: #fff; --sub: #8e8e93; --red: #ff453a; --green: #32d74b; --blue: #0a84ff; }
body { background: var(--bg); color: var(--text); font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; box-sizing: border-box; }
.video-box { width: 100%; max-width: 500px; aspect-ratio: 4/3; background: #111; border-radius: 12px; overflow: hidden; position: relative; margin-bottom: 15px; border: 1px solid #333; }
video { width: 100%; height: 100%; object-fit: cover; display: block; transform: scaleX(1); }
/* کلاس برای آینه کردن دوربین جلو */
video.mirrored { transform: scaleX(-1); }
#alarm-flash { position: absolute; inset: 0; background: rgba(255, 69, 58, 0.5); display: none; z-index: 10; }
.controls-card { width: 100%; max-width: 500px; background: var(--card); padding: 20px; border-radius: 16px; display: flex; flex-direction: column; gap: 15px; }
.graph-wrapper { position: relative; height: 45px; background: #2c2c2e; border-radius: 8px; overflow: hidden; margin-bottom: 5px; }
/* حذف ترنزیشن برای واکنش آنی */
.motion-bar { height: 100%; width: 0%; background: var(--green); opacity: 0.9; }
.threshold-line { position: absolute; top: 0; bottom: 0; width: 4px; background: var(--red); z-index: 5; left: 40%; transform: translateX(-50%); box-shadow: 0 0 5px red; }
.stats-row { display: flex; justify-content: space-between; align-items: center; font-weight: 700; font-size: 15px; }
.stat-left { color: var(--red); } .stat-right { color: var(--green); }
.slider-container { display: flex; flex-direction: column; gap: 8px; }
input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
input[type=range]:focus { outline: none; }
input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 6px; background: var(--blue); border-radius: 3px; }
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 24px; width: 24px; border-radius: 50%; background: #fff; margin-top: -9px; box-shadow: 0 2px 5px black; }
.buttons-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
.btn { border: none; padding: 16px; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }
.btn-grey { background: #3a3a3c; color: white; }
.btn-red { background: #3a3a3c; color: #ccc; border: 1px solid #444; }
.btn-red.active { background: var(--red); color: white; border: none; animation: pulseBtn 1s infinite; }
@keyframes pulseBtn { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }
canvas { display: none; }
.back-link { margin-top: auto; color: var(--sub); text-decoration: none; font-size: 13px; padding-bottom: 20px; }
</style>
</head>
<body>
<div class="video-box">
    <video id="webcam" autoplay playsinline muted></video>
    <div id="alarm-flash"></div>
</div>
<canvas id="proc-canvas"></canvas>

<div class="controls-card">
    <div>
        <div class="graph-wrapper">
            <div id="bar-motion" class="motion-bar"></div>
            <div id="line-thresh" class="threshold-line"></div>
        </div>
    </div>
    <div class="stats-row">
        <span class="stat-left">Trigger: <span id="txt-thresh">40</span>%</span>
        <span class="stat-right">Motion: <span id="txt-motion">0</span>%</span>
    </div>
    <div class="slider-container">
        <span style="color:#888; font-size:12px;">Alarm Threshold</span>
        <input type="range" id="input-slider" min="0" max="100" value="40">
    </div>
    <div class="buttons-grid">
        <button class="btn btn-grey" onclick="rotateCamera()">🔄 Flip Cam</button>
        <button id="btn-siren" class="btn btn-red" onclick="toggleSiren()">🔔 Siren ON</button>
    </div>
</div>

<a href="../index_tools.html" class="back-link">← Back to Tools</a>

<script>
// --- CONFIG ---
const CONF = { 
    procWidth: 64,      // رزولوشن پردازش پایین برای سرعت بالا
    procHeight: 48, 
    diffThresh: 20,     // حساسیت پیکسل
    gain: 5             // ضریب تقویت حرکت
};

// --- ELEMENTS ---
const video = document.getElementById('webcam');
const canvas = document.getElementById('proc-canvas');
const ctx = canvas.getContext('2d', { willReadFrequently: true });
const elFlash = document.getElementById('alarm-flash');
const elBar = document.getElementById('bar-motion');
const elLine = document.getElementById('line-thresh');
const txtThresh = document.getElementById('txt-thresh');
const txtMotion = document.getElementById('txt-motion');
const slider = document.getElementById('input-slider');
const btnSiren = document.getElementById('btn-siren');

// --- STATE ---
let stream = null;
let facingMode = 'environment'; // environment = پشت, user = جلو
let lastData = null;
let sirenEnabled = false;
let audioCtx = null;
let loopId = null;

// --- INIT ---
function init() {
    canvas.width = CONF.procWidth;
    canvas.height = CONF.procHeight;
    updateThreshUI(slider.value);
    startCamera();
}

async function startCamera() {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
    }
    
    // توقف لوپ قبلی برای جلوگیری از تداخل
    if (loopId) cancelAnimationFrame(loopId);

    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: facingMode,
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false 
        });
        
        video.srcObject = stream;
        
        // اصلاح آینه‌ای بودن دوربین جلو
        if (facingMode === 'user') {
            video.classList.add('mirrored');
        } else {
            video.classList.remove('mirrored');
        }

        // مطمئن می‌شویم ویدیو واقعا پخش می‌شود
        video.onloadedmetadata = () => {
            video.play();
            lastData = null; // ریست کردن فریم قبلی
            loopId = requestAnimationFrame(processLoop);
        };
        
    } catch (e) {
        console.error(e);
        alert("Camera Error. Please allow camera access.");
    }
}

function rotateCamera() {
    facingMode = (facingMode === 'environment') ? 'user' : 'environment';
    startCamera();
}

function processLoop() {
    // فقط وقتی ویدیو دیتا دارد پردازش کن
    if (video.readyState === 4 && video.videoWidth > 0) {
        try {
            // رسم ویدیو در کانواس کوچک
            ctx.drawImage(video, 0, 0, CONF.procWidth, CONF.procHeight);
            const frame = ctx.getImageData(0, 0, CONF.procWidth, CONF.procHeight);
            const data = frame.data;
            
            if (lastData) {
                let changed = 0;
                const pData = lastData.data;
                const len = data.length;
                
                // مقایسه پیکسل به پیکسل (سریع)
                for (let i = 0; i < len; i += 4) {
                    const diff = Math.abs(data[i] - pData[i]) + 
                                 Math.abs(data[i+1] - pData[i+1]) + 
                                 Math.abs(data[i+2] - pData[i+2]);
                    if (diff > CONF.diffThresh) {
                        changed++;
                    }
                }
                
                // محاسبه درصد حرکت
                let percent = Math.floor((changed / (CONF.procWidth * CONF.procHeight)) * 100 * CONF.gain);
                if (percent > 100) percent = 100;
                
                updateUI(percent);
                checkAlarm(percent);
            }
            lastData = frame;
        } catch (e) {
            console.error(e);
        }
    }
    loopId = requestAnimationFrame(processLoop);
}

// --- UI & LOGIC ---
slider.addEventListener('input', (e) => updateThreshUI(e.target.value));

function updateThreshUI(val) {
    elLine.style.left = val + '%';
    txtThresh.innerText = val;
}

function updateUI(motionVal) {
    elBar.style.width = motionVal + '%';
    txtMotion.innerText = motionVal;
    
    // تغییر رنگ بار بر اساس عبور از آستانه
    const th = parseInt(slider.value);
    if (motionVal >= th) {
        elBar.style.backgroundColor = '#ff453a'; // قرمز
    } else {
        elBar.style.backgroundColor = '#32d74b'; // سبز
    }
}

function checkAlarm(motionVal) {
    const th = parseInt(slider.value);
    if (motionVal >= th && th > 0) {
        if (sirenEnabled) {
            elFlash.style.display = 'block';
            beep();
        }
    } else {
        elFlash.style.display = 'none';
    }
}

// --- AUDIO SYSTEM (Fixed for iOS) ---
function toggleSiren() {
    // 1. ایجاد کانتکست صدا در اولین کلیک (ضروری برای iOS)
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    // 2. اگر کانتکست معلق است، فعالش کن
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }

    sirenEnabled = !sirenEnabled;
    
    if (sirenEnabled) {
        btnSiren.classList.add('active');
        btnSiren.innerText = "🚨 Siren ACTIVE";
        // یک صدای کوتاه تست پخش کن تا مطمئن شویم کار میکند
        beep(0.1, 800, 0.05);
    } else {
        btnSiren.classList.remove('active');
        btnSiren.innerText = "🔔 Siren ON";
        elFlash.style.display = 'none';
    }
}

function beep(duration = 0.1, freq = 800, vol = 0.5) {
    if (!audioCtx || audioCtx.state !== 'running') return;
    
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'square'; // صدای تیزتر برای آلارم
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    osc.frequency.linearRampToValueAtTime(freq + 400, audioCtx.currentTime + duration); // افکت آژیر (تغییر فرکانس)
    
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
}

// شروع برنامه
init();

</script>
</body>
</html>"""

# 3. نوشتن فایل
html_file_path = os.path.join(folder_path, "index_doorbin-tashkhis-harekat.html")

try:
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Success! File created at: {html_file_path}")
except Exception as e:
    print(f"Write Error: {e}")
