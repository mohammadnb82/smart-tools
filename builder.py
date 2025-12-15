import os
import subprocess

def force_restore_workflow():
    print("--- 🚨 FORCE RESTORING WORKFLOW ENGINE 🚨 ---")

    # 1. ساخت پوشه دایرکتوری (حتی اگر وجود داشته باشد)
    workflow_dir = ".github/workflows"
    if not os.path.exists(workflow_dir):
        os.makedirs(workflow_dir)
        print(f"Created directory: {workflow_dir}")

    # 2. محتوای فایل YAML (همان موتوری که گم شده بود)
    yaml_content = """name: builder.py

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout 🛎️
        uses: actions/checkout@v3

      - name: Deploy to GitHub Pages 🚀
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          folder: .
          clean: true
"""

    # 3. نوشتن فایل
    file_path = f"{workflow_dir}/main.yml"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print(f"✅ Written workflow file: {file_path}")

    # 4. اصلاح .gitignore (اگر مانع باشد)
    if os.path.exists(".gitignore"):
        with open(".gitignore", "r") as f:
            lines = f.readlines()
        
        # حذف هر خطی که باعث نادیده گرفته شدن .github شود
        new_lines = [line for line in lines if ".github" not in line]
        
        if len(new_lines) != len(lines):
            with open(".gitignore", "w") as f:
                f.writelines(new_lines)
            print("⚠️ Removed .github from .gitignore to allow upload")

    # 5. عملیات گیت با فشار (Force)
    print("--- GIT OPERATIONS ---")
    try:
        # نکته کلیدی: استفاده از -f برای مجبور کردن گیت به قبول فایل
        subprocess.run(["git", "add", "-f", ".github/workflows/main.yml"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        
        subprocess.run(["git", "commit", "-m", "FORCE ADD WORKFLOW FILE"], check=False)
        
        print("Pushing to GitHub...")
        subprocess.run(["git", "push"], check=True)
        print("🎉 SUCCESS! Workflow forced successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Error: {e}")

if __name__ == "__main__":
    force_restore_workflow()
