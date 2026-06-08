from flask import Flask, request, render_template_string, jsonify
import asyncio
from pyrogram import Client

app = Flask(__name__)

# ==================== TELEGRAM CONFIG ====================
API_ID = 36111584
API_HASH = '6f0e6729043de10d48250cc2bc613a6f'
STRING_SESSION = "BQInBOAAOgLtSj7-SKUGoo8aRfWEKh6FhHxMUgQonz6Ub6rQlPY1gul0xKn1uW8O1lw6dcs5sD1ASz0-uvFw_SgTzeNU4Qkedeyewv09fn0As4Gk5q2BWF9sKqoJFK-qB1_QZ5qmn-BOKtXo-j2P-TtiX4h4UjkcU7otYsm7reqzUmpcpasMWOzegDVEikyyobuPRLqCHQe0erFCs354ojUXz7JpZOcPUmUViScbjw3kj0qSbrTQRPv7WjYNll1KLWkmqkoTIkX8lqbUfPey1pkiDJjQiDWo3itR2Pb5uEg5LvmUvbGQfkANwv7w0DEqasddjKulYFoduLiHhoT6M8Sl0iXwOwAAAAGHwtM4AA"

INFO_BOT_USERNAME = "FFPlayerInfoBot" 

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
        .container { width: 100%; max-width: 500px; background: #1a1635; padding: 25px; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); border: 1px solid #3d307a; margin-bottom: 20px; text-align: center; }
        h1 { color: #00ffcc; margin-bottom: 5px; font-size: 24px; text-shadow: 0 0 10px rgba(0,255,204,0.3); }
        p.subtitle { color: #aaa; font-size: 14px; margin-bottom: 25px; }
        .form-group { margin-bottom: 15px; text-align: left; }
        label { display: block; margin-bottom: 8px; color: #ccc; font-size: 14px; }
        input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #3d307a; background: #0f0c20; color: #fff; font-size: 16px; outline: none; text-align: center; }
        input:focus { border-color: #00ffcc; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; background: linear-gradient(45deg, #00ffcc, #0099ff); color: #0f0c20; margin-top: 5px; }
        button:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(0,255,204,0.4); }
        
        /* 🌀 एनिमेशन बॉक्स */
        .loading-box { display: none; margin-top: 20px; padding: 20px; }
        .spinner { width: 45px; height: 45px; border: 4px solid #3d307a; border-top: 4px solid #00ffcc; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #00ffcc; font-size: 14px; font-weight: 500; }

        /* 📊 रिजल्ट बॉक्स */
        .result-box { display: none; margin-top: 20px; padding: 15px; border-radius: 10px; background: rgba(0, 255, 204, 0.05); border: 1px solid #3d307a; text-align: left; }
        .info-text { white-space: pre-line; line-height: 1.6; font-size: 15px; color: #e0e0e0; background: #0f0c20; padding: 15px; border-radius: 6px; border-left: 4px solid #ff007f; font-family: monospace; }
        .error-box { display: none; margin-top: 20px; padding: 15px; border-radius: 10px; background: rgba(255, 0, 127, 0.1); border: 1px solid #ff007f; color: #ff007f; font-size: 14px; text-align: left; }
        
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 10px; letter-spacing: 1px; }
    </style>
</head>
<body>

    <div class="container">
        <h1>👑 S.KANHAIYA SERVICES</h1>
        <p class="subtitle">लाइव गेम प्रोफाइल इनफार्मेशन चेकर</p>
        
        <form id="checkerForm">
            <div class="form-group">
                <label>खिलाड़ी की यूआईडी (Player UID):</label>
                <input type="number" id="gameUid" placeholder="यहाँ गेम यूआईडी दर्ज करें" required>
            </div>
            <button type="submit">🔍 प्रोफाइल इनफार्मेशन निकालें</button>
        </form>

        <div id="loadingBox" class="loading-box">
            <div class="spinner"></div>
            <div class="loading-text">⚡ किंग S.KANHAIYA का बोट जानकारी निकाल रहा है... कृपया रुकें...</div>
        </div>

        <div id="resultBox" class="result-box">
            <div id="playerDetails" class="info-text"></div>
        </div>

        <div id="errorBox" class="error-box"></div>
    </div>

    <div class="footer">⚡️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴋ.ʀ sᴇʀᴠɪ́ᴄᴇ</div>

    <script>
        document.getElementById('checkerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const uid = document.getElementById('gameUid').value;
            
            const loadingBox = document.getElementById('loadingBox');
            const resultBox = document.getElementById('resultBox');
            const errorBox = document.getElementById('errorBox');
            const playerDetails = document.getElementById('playerDetails');

            loadingBox.style.display = 'block';
            resultBox.style.display = 'none';
            errorBox.style.display = 'none';

            try {
                const response = await fetch('/api/fetch-profile?uid=' + uid);
                const data = await response.json();
                
                loadingBox.style.display = 'none'; 

                if (data.success) {
                    resultBox.style.display = 'block';
                    playerDetails.innerText = data.bot_msg; 
                } else {
                    errorBox.style.display = 'block';
                    errorBox.innerText = "❌ जानकारी नहीं मिल सकी: " + data.message;
                }
            } catch (err) {
                loadingBox.style.display = 'none';
                errorBox.style.display = 'block';
                errorBox.innerText = '❌ सर्वर से कनेक्ट करने में कोई तकनीकी खराबी आई भाई।';
            }
        });
    </script>
</body>
</html>
"""

# ==================== PYROGRAM LOGIC ====================
async def get_bot_text_data(uid):
    tg_client = Client("kr_web_client", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, in_memory=True)
    try:
        await tg_client.start()
        
        try: await tg_client.read_chat_history(INFO_BOT_USERNAME)
        except: pass

        # बोट को कमांड भेजना
        sent_msg = await tg_client.send_message(INFO_BOT_USERNAME, f"/get {uid}")
        
        bot_response_text = ""
        
        # ⏱️ फ़ास्ट चेकिंग लूप (अधिकतम 5 सेकंड इंतज़ार)
        for _ in range(5):
            await asyncio.sleep(1)
            async for message in tg_client.get_chat_history(INFO_BOT_USERNAME, limit=2):
                if message.from_user and message.from_user.username == INFO_BOT_USERNAME and message.id > sent_msg.id:
                    # अगर बोट ने फोटो के साथ टेक्स्ट (Caption) भेजा है
                    if message.photo and message.caption:
                        bot_response_text = message.caption
                    # अगर बोट ने सिर्फ नॉर्मल टेक्स्ट भेजा है
                    elif message.text:
                        bot_response_text = message.text
                    break
            if bot_response_text:
                break
                
        await tg_client.stop()
        
        if bot_response_text:
            return {"success": True, "bot_msg": bot_response_text}
        else:
            return {"success": False, "message": "बॉट ने टाइम पर जवाब नहीं दिया। कृपया दोबारा कोशिश करें भाई।"}
            
    except Exception as e:
        try: await tg_client.stop()
        except: pass
        return {"success": False, "message": str(e)}

# ==================== FLASK ROUTES ====================
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/fetch-profile')
def fetch_profile():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"success": False, "message": "UID ज़रूरी है"}), 400
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_bot_text_data(uid))
    loop.close()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
