import os
import subprocess
import shutil

def run_command(command):
    """Executes a shell command and prints the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Command: {command}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {command}\n{e.stderr}")
        return None

def create_professional_site():
    print("🚀 Starting God Mode Deployment...")

    # 1. Setup Environment Variables
    token = os.environ.get("PERSONAL_TOKEN")
    repo_name = "stable-site"
    # Get the current user name from the current repo info
    full_repo = os.environ.get("GITHUB_REPOSITORY", "mohammadnb82/smart-tools")
    username = full_repo.split("/")[0]

    # 2. Define the Professional HTML Content (Video Tool)
    html_content = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Editor Pro | ابزار ویرایش ویدیو</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ffmpeg/0.11.6/ffmpeg.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; color: white; }
        .glass { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
        .btn { transition: all 0.3s ease; }
        .btn:hover { transform: translateY(-2px); }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-gray-900 to-black">
    <div class="glass rounded-2xl p-8 w-full max-w-4xl shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-500 to-purple-500"></div>
        
        <div class="text-center mb-8">
            <h1 class="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">ویرایشگر حرفه‌ای ویدیو</h1>
            <p class="text-gray-400 text-lg">قدرتمند، سریع و امن در مرورگر شما</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Upload Zone -->
            <div class="border-2 border-dashed border-gray-600 rounded-xl p-10 text-center hover:border-blue-500 transition cursor-pointer bg-gray-800/50" id="drop-zone">
                <i class="fas fa-cloud-upload-alt text-6xl mb-6 text-blue-500"></i>
                <h3 class="text-xl font-bold mb-2">بارگذاری ویدیو</h3>
                <p class="text-gray-400 text-sm">فایل را اینجا رها کنید یا کلیک کنید</p>
                <input type="file" id="uploader" class="hidden" accept="video/*">
            </div>

            <!-- Controls Panel -->
            <div class="space-y-6 flex flex-col justify-center">
                <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <h3 class="font-bold mb-4 flex items-center gap-2"><i class="fas fa-wrench text-yellow-500"></i> ابزارها</h3>
                    <div class="grid grid-cols-2 gap-3">
                        <button class="btn bg-blue-600 hover:bg-blue-700 px-4 py-3 rounded-lg text-sm font-bold shadow-lg">
                            <i class="fas fa-cut mr-2"></i> برش (Trim)
                        </button>
                        <button class="btn bg-green-600 hover:bg-green-700 px-4 py-3 rounded-lg text-sm font-bold shadow-lg">
                            <i class="fas fa-compress mr-2"></i> فشرده‌سازی
                        </button>
                        <button class="btn bg-purple-600 hover:bg-purple-700 px-4 py-3 rounded-lg text-sm font-bold shadow-lg col-span-2">
                            <i class="fas fa-magic mr-2"></i> استخراج صدا (MP3)
                        </button>
                    </div>
                </div>
                
                <div class="bg-gray-900 p-4 rounded-xl border border-gray-800">
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-2">System Log</h3>
                    <p class="text-xs text-green-400 font-mono" id="log">> سیستم آماده است...</p>
                </div>
            </div>
        </div>

        <div class="mt-8 pt-6 border-t border-gray-700 text-center flex justify-between items-center text-xs text-gray-500">
            <span>نسخه 2.0 (Stable)</span>
            <span>Powered by GitHub Actions & FFmpeg</span>
        </div>
    </div>

    <script>
        const { createFFmpeg, fetchFile } = FFmpeg;
        const ffmpeg = createFFmpeg({ log: true });
        
        document.getElementById('drop-zone').addEventListener('click', () => document.getElementById('uploader').click());
        
        document.getElementById('uploader').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            const log = document.getElementById('log');
            if(file){
                log.innerText = "> در حال بارگذاری هسته پردازشی...";
                if(!ffmpeg.isLoaded()) await ffmpeg.load();
                log.innerText = "> فایل دریافت شد: " + file.name + " | آماده پردازش.";
            }
        });
    </script>
</body>
</html>"""

    # 3. Create index.html in the CURRENT repo (smart-tools)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html generated locally (smart-tools).")

    # 4. DEPLOY TO SECOND REPO (stable-site)
    if not token:
        print("⚠️ SKIP: PERSONAL_TOKEN not found. Cannot deploy to stable-site.")
        return

    print(f"🔄 Preparing to deploy to SECOND repo: {repo_name}...")
    
    # Configure Git
    run_command(f'git config --global user.email "{username}@users.noreply.github.com"')
    run_command(f'git config --global user.name "{username}"')

    # Clone the target repo using the token
    clone_url = f"https://oauth2:{token}@github.com/{username}/{repo_name}.git"
    
    # Clean up if folder exists
    if os.path.exists(repo_name):
        shutil.rmtree(repo_name)
        
    run_command(f"git clone {clone_url}")

    if os.path.exists(repo_name):
        # Copy the new index.html to the cloned repo folder
        shutil.copy("index.html", f"{repo_name}/index.html")
        
        # Go inside, commit and push
        os.chdir(repo_name)
        run_command("git add .")
        run_command('git commit -m "Auto-update: Deployed Video Tool 🚀"')
        push_output = run_command("git push")
        
        if push_output is not None:
             print("✅ SUCCESS: Deployed to stable-site! 🚀")
        else:
             print("⚠️ Push attempt finished (check logs if updated).")
        
        os.chdir("..") # Return to root
    else:
        print(f"❌ ERROR: Could not clone {repo_name}. Does the repo exist?")

if __name__ == "__main__":
    create_professional_sit
