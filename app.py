from flask import Flask, request, render_template_string, jsonify
import requests

app = Flask(__name__)

# आपकी असली API का यूआरएल और सीक्रेट की
API_BASE = "https://kanhaiya-raikwar.vercel.app/like"
API_KEY = "ZEXYK"

# सिंगल HTML टेम्पलेट (CSS और जावास्क्रिप्ट के साथ)
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
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 10px; letter-spacing: 1px; }
    </style>
</head>
<body>

    <!-- 1. फ्री लाइक सेक्शन -->
    <div class="container">
        <h1>👑 S.KANHAIYA SERVICES</h1>
        <p class="subtitle">मुफ़्त फ़्री फ़ायर लाइक पैनल</p>
        
        <div class="section-title">🌍 FREE LIKES SENDER</div>
        <form id="freeLikeForm">
            <div class="form-group">
                <label>रीजन (Region) चुनें:</label>
                <select id="freeRegion">
                    <option value="IND">IND (India)</option>
                    <option value="BD">BD (Bangladesh)</option>
                    <option value="PK">PK (Pakistan)</option>
                    <option value="USA">USA</option>
                </select>
            </div>
            <div class="form-group">
                <label>खिलाड़ी की यूआईडी (UID):</label>
                <input type="number" id="freeUid" placeholder="उदा. 9230844760" required>
            </div>
            <button type="submit" class="btn-free">❤️ भेजें मुफ़्त लाइक</button>
        </form>
        <div id="freeResponse" class="response-box"></div>
    </div>

    <!-- 2. प्रीमियम लॉगिन सेक्शन -->
    <div class="container">
        <div class="section-title">🥷 PREMIUM LOGIN (LEVEL 8+ GEST ID)</div>
        <form id="premiumLoginForm">
            <div class="form-group">
                <label>गेस्ट यूआईडी (Guest UID):</label>
                <input type="number" id="loginUid" placeholder="लेवल 8 या उससे ऊपर की आईडी" required>
            </div>
            <div class="form-group">
                <label>पासवर्ड (Password):</label>
                <input type="password" id="loginPass" placeholder="अकाउंट पासवर्ड दर्ज करें" required>
            </div>
            <button type="submit" class="btn-free" style="background: #7f00ff; color: #fff;">🔐 लॉगिन कन्फर्म करें</button>
        </form>
        <div id="loginResponse" class="response-box"></div>

        <div style="margin-top: 25px;">
            <div class="section-title">💎 PREMIUM FEATURES</div>
            <button id="premiumFeatureBtn" class="btn-premium locked-btn" disabled>🔓 अनलिमिटेड लाइक अनलॉक करें (Locked)</button>
        </div>
    </div>

    <div class="footer">⚡️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴋ.ʀ sᴇʀᴠɪᴄᴇ</div>

    <script>
        // फ्री लाइक सेंडर हैंडलर
        document.getElementById('freeLikeForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const region = document.getElementById('freeRegion').value;
            const uid = document.getElementById('freeUid').value;
            const resBox = document.getElementById('freeResponse');
            
            resBox.style.display = 'block';
            resBox.className = 'response-box success';
            resBox.innerText = '🔄 लाइक भेजने की प्रक्रिया जारी है...';

            try {
                // पाइथन बैकएंड को रिक्वेस्ट भेजना
                const response = await fetch(`/send-free-like?uid=${uid}&region=${region}`);
                const data = await response.json();
                
                if (data.status === 1) {
                    resBox.className = 'response-box success';
                    resBox.innerText = `✅ लाइक भेज दिया गया है 😍\\n👤 खिलाड़ी: ${data.PlayerNickname}\\n🆔 UID: ${uid}\\n👍 पहले के लाइक: ${data.LikesbeforeCommand}\\n❤️ अभी के लाइक: ${data.LikesafterCommand}\\n➕ प्लस लाइक: +${data.LikesGivenByAPI}`;
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = `⚠️ लाइक नहीं भेजा जा सका\\n👤 खिलाड़ी: ${data.PlayerNickname || 'Unknown'}\\n❌ स्टेटस: ${data.status || 'Error'}`;
                }
            } catch (err) {
                resBox.className = 'response-box error';
                resBox.innerText = '❌ सर्ver से कनेक्ट करने में समस्या आई।';
            }
        });

        // प्रीमियम लॉगिन हैंडलर (लेवल चेकर)
        document.getElementById('premiumLoginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const uid = document.getElementById('loginUid').value;
            const resBox = document.getElementById('loginResponse');
            const premBtn = document.getElementById('premiumFeatureBtn');

            resBox.style.display = 'block';
            resBox.className = 'response-box success';
            resBox.innerText = '🔄 अकाउंट वेरिफिकेशन चल रहा है... कृपया रुकें...';

            try {
                // पाइथन बैकएंड से लेवल चेक करवाना
                const response = await fetch(`/check-level?uid=${uid}`);
                const data = await response.json();

                if (data.error) {
                    resBox.className = 'response-box error';
                    resBox.innerText = `❌ त्रुटि: ${data.error}`;
                    return;
                }

                const level_int = parseInt(data.Level) || 0;
                const player_name = data.PlayerNickname || 'Guest Player';

                if (level_int >= 8) {
                    resBox.className = 'response-box success';
                    resBox.innerText = `🎉 लॉगिन सफल!\\n👤 खिलाड़ी: ${player_name}\\n⭐ स्तर (Level): ${level_int}\\n🔥 आपका प्रीमियम फीचर अनलॉक हो गया है!`;
                    
                    premBtn.className = 'btn-premium';
                    premBtn.removeAttribute('disabled');
                    premBtn.innerText = '🚀 अनलिमिटेड लाइक पैनल (अनलॉक)';
                    premBtn.onclick = () => { alert('👑 बधाई हो भाई! प्रीमियम सर्विस पूरी तरह चालू हो गई है।'); };
                } else {
                    resBox.className = 'response-box error';
                    resBox.innerText = `❌ लॉगिन फेल!\\n⚠️ आपका स्तर ${level_int} है। प्रीमियम एक्सेस के लिए कम से कम लेवल 8 आवश्यक है!`;
                }
            } catch (err) {
                resBox.className = 'response-box error';
                resBox.innerText = '❌ वेरिफिकेशन के दौरान कोई खराबी आई।';
            }
        });
    </script>
</body>
</html>
"""

# होम रूट - वेबसाइट का मुख्य पेज दिखाना
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# फ्री लाइक प्रोसेस करने का रूट
@app.route('/send-free-like')
def send_free_like():
    uid = request.args.get('uid')
    region = request.args.get('region', 'IND')
    
    try:
        # सीधे आपकी मुख्य लाइक API पर रिक्वेस्ट भेजना
        url = f"{API_BASE}?uid={uid}&region={region}&key={API_KEY}"
        response = requests.get(url, timeout=15)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": 0, "error": str(e)})

# प्रीमियम के लिए लेवल चेक करने का रूट
@app.route('/check-level')
def check_level():
    uid = request.args.get('uid')
    
    try:
        # लेवल चेक करने के लिए डिफ़ॉल्ट IND रीजन से API को कॉल करना
        url = f"{API_BASE}?uid={uid}&region=IND&key={API_KEY}"
        response = requests.get(url, timeout=15)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
