from flask import Flask, request, render_template_string, jsonify
import asyncio
import re
from pyrogram import Client

app = Flask(__name__)

# ==================== TELEGRAM CONFIG ====================
API_ID = 36111584
API_HASH = '6f0e6729043de10d48250cc2bc613a6f'
STRING_SESSION = "BQInBOAAOgLtSj7-SKUGoo8aRfWEKh6FhHxMUgQonz6Ub6rQlPY1gul0xKn1uW8O1lw6dcs5sD1ASz0-uvFw_SgTzeNU4Qkedeyewv09fn0As4Gk5q2BWF9sKqoJFK-qB1_QZ5qmn-BOKtXo-j2P-TtiX4h4UjkcU7otYsm7reqzUmpcpasMWOzegDVEikyyobuPRLqCHQe0erFCs354ojUXz7JpZOcPUmUViScbjw3kj0qSbrTQRPv7WjYNll1KLWkmqkoTIkX8lqbUfPey1pkiDJjQiDWo3itR2Pb5uEg5LvmUvbGQfkANwv7w0DEqasddjKulYFoduLiHhoT6M8Sl0iXwOwAAAAGHwtM4AA"

INFO_BOT_USERNAME = "FreeFireInfoBot" 

# ==================== HTML INTERFACE ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 S.KANHAIYA VIP TRACKER</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f0c20; color: #fff; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; justify-content: center; }
        .container { width: 100%; max-width: 500px; background: #1a1635; padding: 25px; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); border: 1px solid #3d307a; margin-bottom: 20px; }
        h1 { text-align: center; color: #00ffcc; margin-bottom: 10px; font-size: 24px; text-shadow: 0 0 10px rgba(0,255,204,0.3); }
        p.subtitle { text-align: center; color: #aaa; font-size: 14px; margin-bottom: 25px; }
        .section-title { font-size: 18px; color: #ff007f; margin-bottom: 15px; border-bottom: 1px solid #3d307a; padding-bottom: 5px; text-align: center;}
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #ccc; font-size: 14px; }
        input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #3d307a; background: #0f0c20; color: #fff; font-size: 16px; outline: none; text-align: center; }
        input:focus { border-color: #00ffcc; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 5px; }
        .btn-free { background: linear-gradient(45deg, #00ffcc, #0099ff); color: #0f0c20; }
        .btn-free:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(0,255,204,0.4); }
        .response-box { margin-top: 15px; padding: 15px; border-radius: 8px; font-size: 14px; display: none; line-height: 1.6; white-space: pre-line; text-align: left; }
        .success { background: rgba(0, 255, 204, 0.1); border: 1px solid #00ffcc; color: #00ffcc; }
        .error { background: rgba(255, 0, 127, 0.1); border: 1px solid #ff007f; color: #ff007f; }
        
        /* Loading Animation CSS */
        .loader-container { display: none; flex-direction: column; align-items: center; margin-top: 15px; }
        .loader { border: 4px solid #0f0c20; border-top: 4px solid #00ffcc; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #00ffcc; font-size: 14px; text-shadow: 0 0 5px rgba(0,255,204,0.2); }
        
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 10px; letter-spacing: 1px; }
    </style>
</head>
<body>

    <div class="container">
        <h1>👑 S.KANHAIYA SERVICES</h1>
        <p class="subtitle">इंस्टेंट प्लेयर इनफार्मेशन ट्रैकर</p>
        
        <div class="section-title">🔍 ENTER GAME UID</div>
        <form id="verifyForm">
            <div class="form-group">
                <input type="number" id="gameUid" placeholder="यहाँ प्लेयर यूआईडी दर्ज करें" required>
            </div>
            <button type="submit" class="btn-free">बोट से डेटा निकालें</button>
        </form>

        <div id="loaderSection" class="loader-container">
            <div class="loader"></div>
            <div class="loading-text">🔄 टेलीग्राम बोट से जानकारी निकाली जा रही है... कृपया प्रतीक्षा करें...</div>
        </div>

        <div id="verifyResponse" class="response-box"></div>
    </div>

    <div class="footer">⚡️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴋ.ʀ sᴇʀᴠɪ́ᴄᴇ</div>

    <script>
        document.getElementById('verifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const uid = document.getElementById('gameUid').value;
            const resBox = document.getElementById('verifyResponse');
            const loader = document.getElementById('loaderSection');
            
            // UI रीसेट करें और एनिमेशन दिखाएं
            resBox.style.display = 'none';
            loader.style.display = 'flex';

            try {
                const response = await fetch('/api/tg-verify?uid=' + uid);
                const data = await response.json();
                
                // एनिमेशन छुपाएं
                loader.style.display = 'none';
                resBox.style.display = 'block';
                
                if (data.success) {
                    resBox.className = 'response-box success';
                    resBox.innerText = "📋 प्लेयर प्रोफाइल डेटा मिल गया भाई!\\n\\n" + data.bot_msg + "\\n\\n🎯 निकाला गया स्तर (Level): " + data.level;
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = "❌ त्रुटि: " + data.message;
                }
            } catch (err) {
                loader.style.display = 'none';
                resBox.style.display = 'block';
                resBox.className = 'response-box error';
                resBox.innerText = '❌ सर्वर से रिस्पांस प्राप्त करने में समस्या आई।';
            }
        });
    </script>
</body>
</html>
"""

# ==================== PYROGRAM BACKGROUND LOGIC ============
async def ask_info_bot(uid):
    tg_client = Client("kr_web_client", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, in_memory=True)
    try:
        await tg_client.start()
        
        try:
            await tg_client.read_chat_history(INFO_BOT_USERNAME)
        except:
            pass

        await tg_client.send_message(INFO_BOT_USERNAME, f"/get {uid}")
        
        # बोट रिप्लाई के लिए थोड़ा इंतजार
        await asyncio.sleep(7)
        
        bot_response_text = ""
        
        async for message in tg_client.get_chat_history(INFO_BOT_USERNAME, limit=3):
            if message.from_user and message.from_user.username == INFO_BOT_USERNAME:
                if message.caption:
                    bot_response_text = message.caption
                    break
                elif message.text:
                    bot_response_text = message.text
                    break
                
        await tg_client.stop()
        
        if bot_response_text:
            # 🎯 सुधरा हुआ नियम: 'Prime Level' को छोड़कर सिर्फ असली लेवल (जैसे Level: 55 या स्तर: 60) को ही पकड़ेगा
            # यह 'prime' शब्द के ठीक बाद वाले नंबर्स को नजरअंदाज करेगा
            cleaned_text = re.sub(r'(?i)prime\s*(?:level|lv)?\s*[:\s]*\d+', '', bot_response_text)
            
            level_match = re.search(r'(?:Level|level|स्तर|Lv|LV)\s*[:\s]*\s*(\d+)', cleaned_text)
            
            if level_match:
                level = int(level_match.group(1))
            else:
                all_nums = re.findall(r'\b\d+\b', cleaned_text)
                level = "नहीं मिला"
                for n in all_nums:
                    val = int(n)
                    if 1 <= val <= 100:
                        level = val
                        break
                        
            return {"success": True, "bot_msg": bot_response_text, "level": level}
        else:
            return {"success": False, "message": "बॉट की तरफ से कोई रिप्लाई नहीं आया या टाइमआउट हो गया।"}
            
    except Exception as e:
        try: await tg_client.stop()
        except: pass
        return {"success": False, "message": str(e)}

# ==================== FLASK ROUTES ====================
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tg-verify')
def tg_verify():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"success": False, "message": "UID आवश्यक है"}), 400
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(ask_info_bot(uid))
    loop.close()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
