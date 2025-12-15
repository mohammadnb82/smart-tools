import os
import subprocess
import shutil

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def create_professional_site():
    print("🚀 Starting Deployment...")
    
    # HTML Content
    html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><title>Video Tools</title></head>
<body style="background:#111;color:white;text-align:center;padding:50px;">
<h1>سایت ویدیو حرفه‌ای</h1><p>این سایت توسط ربات ساخته شده است.</p>
</body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Deploy to stable-site
    token = os.environ.get("PERSONAL_TOKEN")
    repo = "stable-site"
    user = os.environ.get("GITHUB_REPOSITORY").split("/")[0]
    
    if token:
        print(f"🔄 Deploying to {repo}...")
        run_command(f'git config --global user.email "{user}@bot.com"')
        run_command(f'git config --global user.name "{user}"')
        run_command(f"git clone https://oauth2:{token}@github.com/{user}/{repo}.git")
        
        if os.path.exists(repo):
            shutil.copy("index.html", f"{repo}/index.html")
            os.chdir(repo)
            run_command("git add .")
            run_command('git commit -m "Update site"')
            run_command("git push")
            print("✅ SUCCESS!")
        else:
            print("❌ Repo not found")
    else:
        print("⚠️ Token missing")

if __name__ == "__main__":
    create_professional_site()
