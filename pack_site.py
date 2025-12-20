import os
import base64

# نام فایلی که خروجی می‌دهد
OUTPUT_FILENAME = "installer.py"

# لیست پوشه‌ها و فایل‌هایی که نباید کپی شوند (مثل فایل‌های سیستمی گیت)
IGNORE_DIRS = {'.git', '.github', '__pycache__', 'venv', 'node_modules', '.upm'}
IGNORE_FILES = {OUTPUT_FILENAME, os.path.basename(__file__), '.DS_Store', 'replit.nix', '.replit'}

def create_installer():
    print("--- STARTING PACKING PROCESS ---")
    
    # شروع ساخت محتوای فایل اینستالر
    installer_content = [
        "# --- AUTO GENERATED INSTALLER ---",
        "import os",
        "import base64",
        "import sys",
        "",
        "print('--- STARTING INSTALLATION ---')",
        "",
        "files_data = {"
    ]

    file_count = 0
    
    # پیمایش تمام پوشه‌ها و زیرپوشه‌ها (Recursive)
    for root, dirs, files in os.walk("."):
        # حذف پوشه‌های ممنوعه تا وارد آنها نشود
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
            
            # مسیر کامل فایل در سیستم
            full_path = os.path.join(root, file)
            # مسیر نسبی برای ساختار سایت (بدون ./)
            rel_path = os.path.relpath(full_path, ".")
            
            # تبدیل اسلش‌های ویندوز به لینوکس (برای سازگاری)
            rel_path = rel_path.replace("\\", "/")
            
            try:
                with open(full_path, "rb") as f:
                    raw_data = f.read()
                    b64_data = base64.b64encode(raw_data).decode('utf-8')
                    
                # اضافه کردن به لیست داده‌ها
                installer_content.append(f'    "{rel_path}": "{b64_data}",')
                print(f"[PACKED] {rel_path}")
                file_count += 1
            except Exception as e:
                print(f"[ERROR] Could not pack {rel_path}: {e}")

    # بستن دیکشنری و اضافه کردن کد بازسازی
    installer_content.append("}")
    installer_content.append("")
    installer_content.append("def install():")
    installer_content.append("    print(f'Extracting {len(files_data)} files...')")
    installer_content.append("    for file_path, encoded_data in files_data.items():")
    installer_content.append("        try:")
    installer_content.append("            # Create directory structure")
    installer_content.append("            dir_name = os.path.dirname(file_path)")
    installer_content.append("            if dir_name:")
    installer_content.append("                os.makedirs(dir_name, exist_ok=True)")
    installer_content.append("")
    installer_content.append("            # Write binary data")
    installer_content.append("            with open(file_path, 'wb') as f:")
    installer_content.append("                f.write(base64.b64decode(encoded_data))")
    installer_content.append("            print(f'[OK] Created: {file_path}')")
    installer_content.append("        except Exception as e:")
    installer_content.append("            print(f'[FAIL] Error creating {file_path}: {e}')")
    installer_content.append("    print('\\n--- INSTALLATION COMPLETE ---')")
    installer_content.append("")
    installer_content.append("if __name__ == '__main__':")
    installer_content.append("    install()")

    # ذخیره فایل نهایی
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(installer_content))
    
    print(f"\nSUCCESS! Packed {file_count} files into '{OUTPUT_FILENAME}'.")

if __name__ == "__main__":
    create_installer()
