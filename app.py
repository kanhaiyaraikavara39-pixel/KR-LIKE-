import os
import json
import base64
import aiohttp
from datetime import date
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

# ============ CONFIGURATION ============
API_URL = "https://kanhaiya-raikwar.vercel.app/"
ENCODED_KEY = "WkVYWFk="
API_KEY = base64.b64decode(ENCODED_KEY).decode()

# लोकल स्टोरेज के लिए फाइलें
DATA_FILES = {
    'stats': '/tmp/daily_stats.json',
    'users': '/tmp/user_limits.json',
    'config': '/tmp/bot_config.json'
}

bot_status = "on"
daily_stats = {}
user_limits = {}
daily_limit = 2

def load_data():
    global daily_stats, user_limits, bot_status, daily_limit
    try:
        with open(DATA_FILES['stats'], 'r') as f: daily_stats = json.load(f)
    except: daily_stats = {}
    try:
        with open(DATA_FILES['users'], 'r') as f: user_limits = json.load(f)
    except: user_limits = {}
    try:
        with open(DATA_FILES['config'], 'r') as f:
            cfg = json.load(f)
            bot_status = cfg.get('status', 'on')
            daily_limit = cfg.get('limit', 2)
    except:
        bot_status, daily_limit = 'on', 2

def save_all():
    try:
        with open(DATA_FILES['stats'], 'w') as f: json.dump(daily_stats, f, indent=2)
        with open(DATA_FILES['users'], 'w') as f: json.dump(user_limits, f, indent=2)
        with open(DATA_FILES['config'], 'w') as f: json.dump({'status': bot_status, 'limit': daily_limit}, f, indent=2)
    except:
        pass  # Vercel Serverless में कभी-कभी /tmp के अलावा राइटिंग ब्लॉक होती है

load_data()

def today_str(): 
    return str(date.today())

def can_user_like(ip_address):
    t = today_str()
    if ip_address not in user_limits or user_limits[ip_address]['date'] != t:
        user_limits[ip_address] = {'date': t, 'count': 0}
        return True
    return user_limits[ip_address]['count'] < daily_limit

def update_user_like(ip_address):
    t = today_str()
    if ip_address not in user_limits or user_limits[ip_address]['date'] != t:
        user_limits[ip_address] = {'date': t, 'count': 0}
    user_limits[ip_address]['count'] += 1

    if t not in daily_stats:  
        daily_stats[t] = {'total': 0, 'ips': {}}  
    daily_stats[t]['total'] += 1  
    if ip_address not in daily_stats[t]['ips']:  
        daily_stats[t]['ips'][ip_address] = 0  
    daily_stats[t]['ips'][ip_address] += 1  
    save_all()

# ============ HTML + CSS + JS (सिंगल स्ट्रिंग में इंटरफेस) ============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Fire Like Booster</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --primary: #f97316;
            --primary-hover: #ea580c;
            --text-main: #f8fafc;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            background: var(--card-bg);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 450px;
            border: 1px solid #334155;
        }}
        h1 {{
            text-align: center;
            color: var(--primary);
            font-size: 26px;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .subtitle {{
            text-align: center;
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 25px;
        }}
        .stats-box {{
            background: #0f172a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            border-left: 4px solid var(--primary);
        }}
        .input-group {{
            margin-bottom: 18px;
        }}
        .input-group label {{
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            color: #cbd5e1;
        }}
        .input-group input, .input-group select {{
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #475569;
            background: #0f172a;
            color: white;
            box-sizing: border-box;
            font-size: 16px;
        }}
        .input-group input:focus {{
            border-color: var(--primary);
            outline: none;
        }}
        button {{
            width: 100%;
            padding: 14px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }}
        button:hover {{
            background: var(--primary-hover);
        }}
        #result {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
            font-size: 14px;
            line-height: 1.6;
        }}
        .success-res {{ background: #065f46; border: 1px solid #059669; }}
        .error-res {{ background: #991b1b; border: 1px solid #dc2626; }}
        .loader {{
            display: none;
            text-align: center;
            margin-top: 15px;
        }}
    </style>
</head>
<body>

<div class="container">
    <h1><i class="fa-solid fa-fire text-amber-500"></i> FF LIKE BOOSTER</h1>
    <div class="subtitle">वेबसाइट से सीधे फ्री फायर लाइक्स बढ़ाएं</div>

    <div class="stats-box">
        <span>स्टेटस: <strong style="color: #4ade80;">{bot_status}</strong></span>
        <span>आज बचे लाइक्स: <strong>{remaining} / {daily_limit}</strong></span>
    </div>

    <form id="likeForm">
        <div class="input-group">
            <label><i class="fa-solid fa-globe"></i> क्षेत्र चुनें (Region)</label>
            <select name="region" id="region">
                <option value="IND">India (IND)</option>
                <option value="BD">Bangladesh (BD)</option>
                <option value="PK">Pakistan (PK)</option>
                <option value="USA">USA</option>
                <option value="BR">Brazil</option>
            </select>
        </div>

        <div class="input-group">
            <label><i class="fa-solid fa-id-card"></i> प्लेयर UID</label>
            <input type="text" name="uid" id="uid" placeholder="यहाँ अपनी गेम UID डालें..." required>
        </div>

        <button type="submit" id="submitBtn">लाइक प्रोसेस करें <i class="fa-solid fa-paper-plane"></i></button>
    </form>

    <div class="loader" id="loader">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color: var(--primary); margin-bottom: 10px;"></i>
        <p style="margin:0;">लाइक भेजे जा रहे हैं, पेज को रिफ्रेश न करें...</p>
    </div>

    <div id="result"></div>
</div>

<script>
    document.getElementById('likeForm').addEventListener('submit', async (e) => {{
        e.preventDefault();
        
        const form = e.target;
        const btn = document.getElementById('submitBtn');
        const loader = document.getElementById('loader');
        const resultDiv = document.getElementById('result');
        
        resultDiv.style.display = 'none';
        btn.style.display = 'none';
        loader.style.display = 'block';
        
        const formData = new FormData(form);
        
        try {{
            const response = await fetch('/api/like', {{
                method: 'POST',
                body: formData
            }});
            const data = await response.json();
            
            loader.style.display = 'none';
            btn.style.display = 'block';
            resultDiv.style.display = 'block';
            
            if (data.status === 'success') {{
                resultDiv.className = 'success-res';
                resultDiv.innerHTML = `
                    <h3 style="margin:0 0 10px 0; color: #4ade80;">✅ लाइक सफलतापूर्वक भेजे गए!</h3>
                    <b>प्लेयर नाम:</b> ${{data.player}}<br>
                    <b>UID:</b> <code>${{data.uid}}</code><br>
                    <b>लेवल:</b> ${{data.level}}<br>
                    <b>मिले लाइक्स:</b> +${{data.given}}<br>
                    <b>टोटल लाइक्स:</b> ${{data.before}} ➔ ${{data.after}}
                `;
            }} else {{
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = `❌ ${{data.message}}`;
            }}
        }} catch (error) {{
            loader.style.display = 'none';
            btn.style.display = 'block';
            resultDiv.style.display = 'block';
            resultDiv.className = 'error-res';
            resultDiv.innerHTML = `❌ सर्वर डाउन है या कनेक्शन टूट गया है।`;
        }}
    }});
</script>
</body>
</html>
"""

# ============ ROUTES ============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    client_ip = request.client.host or "127.0.0.1"
    t = today_str()
    used = user_limits.get(client_ip, {}).get('count', 0) if client_ip in user_limits and user_limits[client_ip]['date'] == t else 0
    remaining = daily_limit - used
    
    # HTML को डायनामिक डेटा के साथ रेंडर करना
    return HTML_TEMPLATE.format(
        bot_status=bot_status.upper(),
        remaining=remaining,
        daily_limit=daily_limit
    )

@app.post("/api/like")
async def send_like(request: Request, region: str = Form(...), uid: str = Form(...)):
    if bot_status == "off":
        return JSONResponse({"status": "error", "message": "वेबसाइट अभी मेंटेनेंस में है।"})
    
    client_ip = request.client.host or "127.0.0.1"
    region = region.upper()
    
    if not uid.isdigit():
        return JSONResponse({"status": "error", "message": "UID केवल अंकों (Numbers) में होनी चाहिए!"})
        
    if not can_user_like(client_ip):
        return JSONResponse({"status": "error", "message": "आज की आपकी लिमिट खत्म हो चुकी है! कल आएं।"})

    try:
        url = f"{API_URL}like?uid={uid}&region={region}&key={API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    api_status = data.get('status')
                    
                    if api_status == 1:
                        update_user_like(client_ip)
                        return JSONResponse({
                            "status": "success",
                            "player": data.get('PlayerNickname', 'Unknown'),
                            "uid": data.get('UID', uid),
                            "region": data.get('Region', region),
                            "level": data.get('Level', 'N/A'),
                            "given": data.get('LikesGivenByAPI', 0),
                            "before": data.get('LikesbeforeCommand', 0),
                            "after": data.get('LikesafterCommand', 0)
                        })
                    elif api_status == 2:
                        return JSONResponse({"status": "error", "message": "इस UID की आज की API लिमिट खत्म हो गई है।"})
                    else:
                        return JSONResponse({"status": "error", "message": "मुख्य सर्वर से गलत रिस्पॉन्स मिला।"})
                else:
                    return JSONResponse({"status": "error", "message": f"सर्वर एरर कोड: HTTP {resp.status}"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"कनेक्शन फ़ेल: {str(e)}"})
