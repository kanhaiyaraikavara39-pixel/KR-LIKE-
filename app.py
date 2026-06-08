from flask import Flask, request, render_template_string, jsonify, send_from_path
import asyncio
import os
import io
from pyrogram import Client

app = Flask(__name__)

# ==================== TELEGRAM CONFIG ====================
API_ID = 36111584
API_HASH = '6f0e6729043de10d48250cc2bc613a6f'
STRING_SESSION = "BQInBOAAOgLtSj7-SKUGoo8aRfWEKh6FhHxMUgQonz6Ub6rQlPY1gul0xKn1uW8O1lw6dcs5sD1ASz0-uvFw_SgTzeNU4Qkedeyewv09fn0As4Gk5q2BWF9sKqoJFK-qB1_QZ5qmn-BOKtXo-j2P-TtiX4h4UjkcU7otYsm7reqzUmpcpasMWOzegDVEikyyobuPRLqCHQe0erFCs354ojUXz7JpZOcPUmUViScbjw3kj0qSbrTQRPv7WjYNll1KLWkmqkoTIkX8lqbUfPey1pkiDJjQiDWo3itR2Pb5uEg5LvmUvbGQfkANwv7w0DEqasddjKulYFoduLiHhoT6M8Sl0iXwOwAAAAGHwtM4AA"

INFO_BOT_USERNAME = "FreeFireInfoBot" 

# फोटो को सर्वर पर स्टोर करने की जगह
CACHE_DIR = "/tmp/avatar_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# ==================== HTML INTERFACE WITH ANIMATION ====================
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
        
        /* 🌀 लोडिंग एनीमेशन स्टाइल */
        .loading-box { display: none; margin-top: 20px; padding: 20px; }
        .spinner { width: 50px; height: 50px; border: 5px solid #3d307a; border-top: 5px solid #00ffcc; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 15px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #00ffcc; font-size: 14px; font-weight: 500; letter-spacing: 0.5px; }

        /* 📊 रिजल्ट कार्ड स्टाइल */
        .result-box { display: none; margin-top: 20px; padding: 15px; border-radius: 10px; background: rgba(0, 255, 204, 0.05); border: 1px solid #3d307a; text-align: left; }
        .player-photo { width: 100%; max-height: 400px; object-fit: contain; border-radius: 8px; border: 2px solid #00ffcc; margin-bottom: 15px; display: none; box-shadow: 0 0 15px rgba(0,255,204,0.2); }
        .info-text { white-space: pre-line; line-height: 1.6; font-size: 15px; color: #e0e0e0; background: #0f0c20; padding: 12px; border-radius: 6px; border-left: 4px solid #ff007f; }
        .error-box { display: none; margin-top: 20px; padding: 15px; border-radius: 10px; background: rgba(255, 0, 127, 0.1); border: 1px solid #ff007f; color: #ff007f; font-size: 14px; text-align: left; }
        
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 10px; letter-spacing: 1px; }
    </style>
</head>
<body>

    <div class="container">
        <h1>👑 S.KANHAIYA SERVICES</h1>
        <p class="subtitle">लाइव गेम प्रोफाइल एवं आउटफिट चेकर पैनल</p>
        
        <form id="checkerForm">
            <div class="form-group">
                <label>खिलाड़ी की यूआईडी (Player UID):</label>
                <input type="number" id="gameUid" placeholder="यहाँ गेम यूआईडी दर्ज करें" required>
            </div>
            <button type="submit">🔍 प्रोफाइल और आउटफिट निकालें</button>
        </form>

        <div id="loadingBox" class="loading-box">
            <div class="spinner"></div>
            <div class="loading-text">⚡ किंग S.KANHAIYA का बोट जानकारी और आउटफिट इमेज निकाल रहा है... कृपया रुकें...</div>
        </div>

        <div id="resultBox" class="result-box">
            <img id="playerImg" class="player-photo" src="" alt="Player Outfit">
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
            const playerImg = document.getElementById('playerImg');
            const playerDetails = document.getElementById('playerDetails');

            // स्क्रीन रीसेट और लोडिंग चालू करना
            loadingBox.style.display = 'block';
            resultBox.style.display = 'none';
            errorBox.style.display = 'none';
            playerImg.style.display = 'none';

            try {
                const response = await fetch('/api/fetch-profile?uid=' + uid);
                const data = await response.json();
                
                loadingBox.style.display = 'none'; // लोडिंग बंद

                if (data.success) {
                    resultBox.style.display = 'block';
                    playerDetails.innerText = data.bot_msg; // बोट का पूरा सैट किया हुआ मैसेज

                    // अगर बोट ने आउटफिट की फोटो भेजी है, तो उसे लोड करना
                    if (data.has_photo) {
                        playerImg.src = "/api/get-photo?file_id=" + data.file_id;
                        playerImg.style.display = 'block';
                    }
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

# ==================== PYROGRAM BACKGROUND LOGIC ============
async def get_bot_profile_data(uid):
    tg_client = Client("kr_web_client", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, in_memory=True)
    try:
        await tg_client.start()
        
        try: await tg_client.read_chat_history(INFO_BOT_USERNAME)
        except: pass

        # बोट को सीधा /get UID कमांड मारना
        await tg_client.send_message(INFO_BOT_USERNAME, f"/get {uid}")
        
        # बोट को इमेज और डेटा जनरेट करने के लिए 8 सेकंड का टाइम देना
        await asyncio.sleep(8)
        
        bot_response_text = ""
        has_photo = False
        file_id = ""
        
        # बोट चैट का लेटेस्ट मैसेज देखना
        async for message in tg_client.get_chat_history(INFO_BOT_USERNAME, limit=2):
            if message.from_user and message.from_user.username == INFO_BOT_USERNAME:
                # अगर बोट ने आउटफिट की फोटो भेजी है
                if message.photo:
                    has_photo = True
                    file_id = message.photo.file_id
                    bot_response_text = message.caption if message.caption else "इमेज प्राप्त हुई भाई!"
                    break
                # अगर बोट ने सिर्फ टेक्स्ट भेजा है
                elif message.text:
                    bot_response_text = message.text
                    break
                    
        await tg_client.stop()
        
        if bot_response_text:
            return {
                "success": True, 
                "bot_msg": bot_response_text, 
                "has_photo": has_photo, 
                "file_id": file_id
            }
        else:
            return {"success": False, "message": "बॉट की तरफ से रिप्लाई नहीं आया या टाइमआउट हुआ।"}
            
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
    result = loop.run_until_complete(get_bot_profile_data(uid))
    loop.close()
    return jsonify(result)

# टेलीग्राम सर्वर से इमेज डाउनलोड करके वेब स्क्रीन पर सर्व करने का रूट
@app.route('/api/get-photo')
def get_photo():
    file_id = request.args.get('file_id')
    if not file_id:
        return "Missing file_id", 400
        
    async def download_tg_photo():
        tg_client = Client("kr_web_client", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, in_memory=True)
        try:
            await tg_client.start()
            # फोटो को डायरेक्ट मेमोरी (Bytes) में डाउनलोड करना ताकि वेर्सेल पर परमानेंट स्टोर न करना पड़े
            photo_bytes = await tg_client.download_media(file_id, in_memory=True)
            await tg_client.stop()
            return photo_bytes.getbuffer().tobytes()
        except Exception as e:
            try: await tg_client.stop()
            except: pass
            return None

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    img_data = loop.run_until_complete(download_tg_photo())
    loop.close()
    
    if img_data:
        return app.response_class(img_data, mimetype='image/jpeg')
    return "Image not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
