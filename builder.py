import os
from bs4 import BeautifulSoup

def update_only_third_button():
    file_path = "index.html"

    # چک کردن وجود فایل
    if not os.path.exists(file_path):
        print("❌ Error: index.html پیدا نشد.")
        return

    # ۱. باز کردن فایل بدون دستکاری ساختار
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # ۲. پیدا کردن تمام تگ‌های لینک (a)
    links = soup.find_all("a")

    # ۳. انتخاب دکمه سوم (ایندکس ۲)
    if len(links) >= 3:
        target_button = links[2] # 0=اول، 1=دوم، 2=سوم

        # الف) تغییر لینک به فایل ماشین حساب
        target_button['href'] = "tools/calculator/index.html"

        # ب) تغییر نام دکمه به "بهترین ماشین حساب"
        # (اگر داخل دکمه تگ h3 بود، متن آن را عوض میکند تا دیزاین بهم نریزد)
        header_tag = target_button.find("h3")
        if header_tag:
            header_tag.string = "بهترین ماشین حساب"
        else:
            # اگر h3 نداشت، کل متن دکمه را عوض میکند
            target_button.string = "بهترین ماشین حساب"
        
        # ج) تغییر آیکون به ماشین حساب (فقط اگر جای آیکون داشته باشد)
        icon_div = target_button.find(class_="icon")
        if icon_div:
            icon_div.string = "🧮"

        print("✅ عملیات موفق: دکمه سوم به ماشین حساب متصل شد.")
    else:
        print("⚠️ هشدار: کمتر از ۳ دکمه در فایل index.html وجود دارد.")
        return

    # ۴. ذخیره فایل با تغییرات جزئی
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == "__main__":
    update_only_third_button()
