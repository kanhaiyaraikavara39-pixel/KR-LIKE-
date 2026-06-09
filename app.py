import os
import json
import base64
import aiohttp
from datetime import date, datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

# ============ CONFIGURATION ============
LIKE_API_URL = "https://kanhaiya-raikwar.vercel.app/"
INFO_API_URL = "https://s-kanhaiya-ff-info.vercel.app/player-info"
ENCODED_KEY = "WkVYWFk="
API_KEY = base64.b64decode(ENCODED_KEY).decode()

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
        pass

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

# ============ HTML + CSS + JS ============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Free Fire Multi-Tool</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --primary: #f97316;
            --primary-hover: #ea580c;
            --secondary: #06b6d4;
            --secondary-hover: #0891b2;
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
            max-width: 480px;
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
        .btn-container {{
            display: flex;
            gap: 12px;
            margin-top: 10px;
        }}
        button {{
            flex: 1;
            padding: 14px;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .btn-like {{
            background: var(--primary);
        }}
        .btn-like:hover {{
            background: var(--primary-hover);
        }}
        .btn-info {{
            background: var(--secondary);
        }}
        .btn-info:hover {{
            background: var(--secondary-hover);
        }}
        #result {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
            font-size: 14px;
            line-height: 1.6;
            word-wrap: break-word;
        }}
        .success-res {{ background: #065f46; border: 1px solid #059669; }}
        .info-res {{ 
            background: #0f172a; 
            border: 1px solid #2563eb; 
            padding: 18px;
            border-radius: 12px;
        }}
        .error-res {{ background: #991b1b; border: 1px solid #dc2626; }}
        
        .info-header {{
            color: #67e8f9;
            font-size: 18px;
            font-weight: bold;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 8px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #1e293b;
        }}
        .info-label {{
            color: #94a3b8;
            font-weight: 500;
        }}
        .info-value {{
            color: #f8fafc;
            font-weight: bold;
        }}
        .info-sig {{
            background: rgba(255,255,255,0.05);
            padding: 8px;
            border-radius: 6px;
            margin-top: 10px;
            font-style: italic;
            color: #cbd5e1;
            font-size: 13px;
        }}
        
        .loader {{
            display: none;
            text-align: center;
            margin-top: 15px;
        }}
    </style>
</head>
<body>

<div class="container">
    <h1><i class="fa-solid fa-crosshairs"></i> FF TOOLBOX</h1>
    <div class="subtitle">लाइक्स बढ़ाएं और प्लेयर की जानकारी निकालें</div>

    <div class="stats-box">
        <span>स्टेटस: <strong style="color: #4ade80;">{bot_status}</strong></span>
        <span>आज बचे लाइक्स: <strong>{remaining} / {daily_limit}</strong></span>
    </div>

    <form id="toolForm">
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
            <input type="text" name="uid" id="uid" placeholder="यहाँ गेम UID डालें..." required>
        </div>

        <div class="btn-container">
            <button type="button" class="btn-info" onclick="processAction('info')">
                <i class="fa-solid fa-magnifying-glass"></i> प्लेयर इनफ़ो
            </button>
            <button type="button" class="btn-like" onclick="processAction('like')">
                <i class="fa-solid fa-heart"></i> लाइक भेजें
            </button>
        </div>
    </form>

    <div class="loader" id="loader">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color: var(--primary); margin-bottom: 10px;"></i>
        <p style="margin:0;" id="loaderText">प्रोसेसिंग चालू है, कृपया रुकें...</p>
    </div>

    <div id="result"></div>
</div>

<script>
    async function processAction(actionType) {{
        const region = document.getElementById('region').value;
        const uid = document.getElementById('uid').value;
        const loader = document.getElementById('loader');
        const loaderText = document.getElementById('loaderText');
        const resultDiv = document.getElementById('result');

        if (!uid.trim()) {{
            alert("कृपया पहले UID दर्ज करें!");
            return;
        }}

        resultDiv.style.display = 'none';
        loader.style.display = 'block';
        
        if (actionType === 'like') {{
            loaderText.innerText = "लाइक भेजे जा रहे हैं, पेज रिफ्रेश न करें...";
        }} else {{
            loaderText.innerText = "प्लेयर का डेटा खोजा जा रहा है...";
        }}

        const formData = new FormData();
        formData.append('region', region);
        formData.append('uid', uid);
        formData.append('action', actionType);

        try {{
            const response = await fetch('/api/process', {{
                method: 'POST',
                body: formData
            }});
            const data = await response.json();
            
            loader.style.display = 'none';
            resultDiv.style.display = 'block';
            
            if (data.status === 'success') {{
                if (actionType === 'like') {{
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
                    resultDiv.className = 'info-res';
                    
                    let infoHTML = `
                        <div class="info-header">
                            <i class="fa-solid fa-user-shield"></i> प्लेयर प्रोफाइल कार्ड
                        </div>
                        <div class="info-row">
                            <span class="info-label">निकनेम (Name):</span>
                            <span class="info-value" style="color: #f59e0b;">${{data.info.nickname}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">गेम UID:</span>
                            <span class="info-value">${{data.info.uid}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">क्षेत्र (Region):</span>
                            <span class="info-value">${{data.info.region}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">लेवल (Level):</span>
                            <span class="info-value" style="color: #4ade80;">${{data.info.level}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">कुल लाइक्स (Likes):</span>
                            <span class="info-value" style="color: #ec4899;"><i class="fa-solid fa-heart"></i> ${{data.info.likes}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">क्रेडिट स्कोर:</span>
                            <span class="info-value">${{data.info.credit_score}}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">आखिरी बार ऑनलाइन:</span>
                            <span class="info-value">${{data.info.last_login}}</span>
                        </div>
                        <div class="info-row" style="border:none;">
                            <span class="info-label">सिग्नेचर (Signature):</span>
                        </div>
                        <div class="info-sig">${{data.info.signature}}</div>
                    `;
                    resultDiv.innerHTML = infoHTML;
                }}
            }} else {{
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = `❌ ${{data.message}}`;
            }}
        }} catch (error) {{
            loader.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.className = 'error-res';
            resultDiv.innerHTML = `❌ सर्वर से संपर्क नहीं हो पाया।`;
        }}
    }}
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
    
    return HTML_TEMPLATE.format(
        bot_status=bot_status.upper(),
        remaining=remaining,
        daily_limit=daily_limit
    )

@app.post("/api/process")
async def process(request: Request, region: str = Form(...), uid: str = Form(...), action: str = Form(...)):
    if bot_status == "off":
        return JSONResponse({"status": "error", "message": "वेबसाइट अभी मेंटेनेंस में है।"})
    
    client_ip = request.client.host or "127.0.0.1"
    region = region.lower()
    
    if not uid.isdigit():
        return JSONResponse({"status": "error", "message": "UID केवल अंकों (Numbers) में होनी चाहिए!"})

    # ---- 1. प्लेयर इन्फो एक्शन ----
    if action == "info":
        try:
            url = f"{INFO_API_URL}?region={region}&uid={uid}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    if resp.status == 200:
                        raw_data = await resp.json()
                        
                        # केस-इन्सेन्सिटिव (बड़े-छोटे अक्षर) हैंडलिंग ताकि डेटा मिस न हो
                        basic_info = raw_data.get("BasicInfo") or raw_data.get("basicInfo") or {}
                        social_info = raw_data.get("socialInfo") or raw_data.get("SocialInfo") or {}
                        credit_info = raw_data.get("creditScoreInfo") or raw_data.get("CreditScoreInfo") or {}
                        
                        # नाम और लेवल निकालने के सारे संभावित तरीके (ताकि N/A न आए)
                        nickname = basic_info.get("nickname") or basic_info.get("Nickname") or raw_data.get("nickname") or "Unknown"
                        level = basic_info.get("level") or basic_info.get("Level") or raw_data.get("level") or "N/A"
                        likes = basic_info.get("liked") or basic_info.get("Liked") or basic_info.get("likes") or 0
                        
                        last_login_ts = basic_info.get("lastLoginAt") or basic_info.get("lastLogin") or 0
                        try:
                            last_login_date = datetime.fromtimestamp(int(last_login_ts)).strftime('%d-%m-%Y %H:%M') if last_login_ts else "N/A"
                        except:
                            last_login_date = "N/A"
                            
                        clean_profile = {
                            "nickname": nickname,
                            "uid": basic_info.get("accountId") or uid,
                            "region": basic_info.get("region", region.upper()),
                            "level": level,
                            "likes": likes,
                            "credit_score": credit_info.get("creditScore") or credit_info.get("creditscore") or "N/A",
                            "last_login": last_login_date,
                            "signature": social_info.get("signature") or "No Signature Set"
                        }
                        
                        return JSONResponse({
                            "status": "success",
                            "info": clean_profile
                        })
                    else:
                        return JSONResponse({"status": "error", "message": f"इन्फो एपीआई एरर: HTTP {resp.status}"})
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"इन्फो निकालने में विफल: {str(e)}"})

    # ---- 2. लाइक भेजने का एक्शन ----
    elif action == "like":
        region_upper = region.upper()
        if not can_user_like(client_ip):
            return JSONResponse({"status": "error", "message": "आज की आपकी लाइक लिमिट खत्म हो चुकी है! प्लेयर इन्फो अभी भी चेक कर सकते हैं।"})

        try:
            url = f"{LIKE_API_URL}like?uid={uid}&region={region_upper}&key={API_KEY}"
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
                                "region": data.get('Region', region_upper),
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
                        return JSONResponse({"status": "error", "message": f"लाइक सर्वर एरर कोड: HTTP {resp.status}"})
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"कनेक्शन फ़ेल: {str(e)}"})

    return JSONResponse({"status": "error", "message": "अवैध एक्शन टाइप।"})
