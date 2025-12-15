import os

def create_tool(folder_name, file_name, content):
    """
    این تابع یک پوشه جدید داخل tools می سازد و فایل HTML را درون آن ذخیره می کند.
    """
    # مسیر پایه پوشه ابزارها
    base_path = "tools"
    
    # اگر پوشه tools نبود، بساز
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # ساخت مسیر اختصاصی برای ابزار (مثلا tools/calculator)
    tool_path = os.path.join(base_path, folder_name)
    if not os.path.exists(tool_path):
        os.makedirs(tool_path)
    
    # نوشتن فایل
    full_path = os.path.join(tool_path, file_name)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Created: {full_path}")

# --- محتوای ابزار ماشین حساب ---
calculator_html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ماشین حساب مهندسی</title>
    <style>
        body { font-family: sans-serif; background: #222; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .calculator { background: #333; padding: 20px; border-radius: 15px; box-shadow: 0 0 20px rgba(0,255,0,0.2); }
        input { width: 100%; height: 50px; margin-bottom: 10px; font-size: 24px; text-align: left; padding: 5px; box-sizing: border-box; }
        .buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        button { padding: 20px; font-size: 18px; border: none; border-radius: 5px; cursor: pointer; background: #444; color: white; }
        button:active { background: #666; }
        .equal { background: #00ff00; color: black; font-weight: bold; }
        .clear { background: #ff4444; color: white; }
    </style>
</head>
<body>
    <div class="calculator">
        <h3 style="text-align:center; margin-top:0;">ماشین حساب</h3>
        <input type="text" id="display" readonly>
        <div class="buttons">
            <button class="clear" onclick="clearDisplay()">C</button>
            <button onclick="appendToDisplay('/')">/</button>
            <button onclick="appendToDisplay('*')">×</button>
            <button onclick="backspace()">⌫</button>
            <button onclick="appendToDisplay('7')">7</button>
            <button onclick="appendToDisplay('8')">8</button>
            <button onclick="appendToDisplay('9')">9</button>
            <button onclick="appendToDisplay('-')">-</button>
            <button onclick="appendToDisplay('4')">4</button>
            <button onclick="appendToDisplay('5')">5</button>
            <button onclick="appendToDisplay('6')">6</button>
            <button onclick="appendToDisplay('+')">+</button>
            <button onclick="appendToDisplay('1')">1</button>
            <button onclick="appendToDisplay('2')">2</button>
            <button onclick="appendToDisplay('3')">3</button>
            <button class="equal" onclick="calculateResult()">=</button>
            <button onclick="appendToDisplay('0')" style="grid-column: span 2;">0</button>
            <button onclick="appendToDisplay('.')">.</button>
        </div>
    </div>
    <script>
        function appendToDisplay(value) { document.getElementById('display').value += value; }
        function clearDisplay() { document.getElementById('display').value = ''; }
        function backspace() { let d = document.getElementById('display'); d.value = d.value.slice(0, -1); }
        function calculateResult() { try { document.getElementById('display').value = eval(document.getElementById('display').value); } catch { alert('خطا'); } }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # دستور ساخت: پوشه calculator، فایل index.html، با محتوای بالا
    create_tool("calculator", "index.html", calculator_html)
    print("🎉 Build Complete: Calculator tool created inside tools/ folder.")
