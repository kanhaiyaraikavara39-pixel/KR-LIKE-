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

# 🔗 आपकी सभी सेट की हुई लिंक्स
MENU_LINKS = [
    {"title": "📢 Telegram group", "url": "https://t.me/+L4r9VbNDxJo4ZDJll"},
    {"title": "💬 TELEGRAM BOT", "url": "https://t.me/Kanhaiya789_bot"},
    {"title": "📸 Instagram Profile", "url": "https://www.instagram.com/s.kanhaiya.7m"},
    {"title": "📺 YouTube Channel", "url": "https://youtube.com/@s.kanhaiya.7m?si=5dsvMXdeT8SzX58Q"},
    {"title": "💎 Buy Diamonds", "url": "https://example.com/shop"},
    {"title": "🔥 Free Fire Official", "url": "https://ff.garena.com/"},
    {"title": "🛠️ OB53 PROXY SERVER", "url": "https://astutebetaserverff.com/"}
]

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

# ============ HTML + CSS + JS (HACKER STYLE) ============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ KR TERMINAL v1.0 ⚡</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #05080e;
            --card-bg: #0a0f1d;
            --primary: #00ff66;
            --primary-hover: #00cc52;
            --secondary: #00e5ff;
            --secondary-hover: #00b3cc;
            --text-main: #cddecb;
            --terminal-border: #1a2f4c;
            --alert-red: #ff3333;
        }}
        
        body {{
            font-family: 'Courier New', Courier, monospace;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            position: relative;
            background-image: linear-gradient(rgba(0, 255, 102, 0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 255, 102, 0.03) 1px, transparent 1px);
            background-size: 20px 20px;
        }}
        
        .container {{
            background: var(--card-bg);
            padding: 25px;
            border-radius: 4px;
            box-shadow: 0 0 30px rgba(0, 255, 102, 0.15);
            width: 100%;
            max-width: 500px;
            border: 2px solid var(--primary);
            box-sizing: border-box;
            position: relative;
        }}
        
        /* 💎 VIP ASCII HEADER */
        .ascii-header {{
            text-align: center;
            color: var(--primary);
            font-size: 10px;
            white-space: pre;
            line-height: 1.2;
            margin-bottom: 15px;
            text-shadow: 0 0 8px var(--primary);
            font-weight: bold;
        }}

        .menu-trigger-btn {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: transparent;
            color: var(--secondary);
            border: 1px solid var(--secondary);
            padding: 6px 12px;
            border-radius: 2px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            width: auto;
        }}
        .menu-trigger-btn:hover {{
            background: rgba(0, 229, 255, 0.2);
            box-shadow: 0 0 10px var(--secondary);
        }}

        .links-menu-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            z-index: 999;
            backdrop-filter: blur(5px);
        }}
        .links-menu {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #070c14;
            border: 2px solid var(--secondary);
            border-radius: 4px;
            width: 90%;
            max-width: 400px;
            max-height: 75vh;
            overflow-y: auto;
            padding: 20px;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.3);
            z-index: 1000;
            box-sizing: border-box;
        }}
        .menu-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--secondary);
        }}
        .menu-header h2 {{
            margin: 0;
            font-size: 16px;
            color: var(--secondary);
            letter-spacing: 1px;
        }}
        .close-menu-btn {{
            background: none;
            border: none;
            color: var(--text-main);
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            width: auto;
        }}
        .close-menu-btn:hover {{ color: var(--alert-red); }}
        
        .menu-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
        }}
        .menu-link-item {{
            background: #0d1527;
            color: var(--text-main);
            padding: 12px;
            border-radius: 2px;
            text-decoration: none;
            font-size: 13px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid var(--terminal-border);
            transition: 0.2s;
        }}
        .menu-link-item:hover {{
            background: rgba(0, 229, 255, 0.1);
            color: var(--secondary);
            transform: translateX(4px);
            border-color: var(--secondary);
        }}

        h1 {{
            text-align: center;
            color: var(--primary);
            font-size: 22px;
            margin: 5px 0;
            letter-spacing: 2px;
            text-shadow: 0 0 5px var(--primary);
        }}
        .subtitle {{
            text-align: center;
            color: #6482a6;
            font-size: 12px;
            margin-bottom: 25px;
            text-transform: uppercase;
        }}
        
        .stats-box {{
            background: #02050a;
            padding: 12px;
            border-radius: 2px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            border: 1px solid var(--terminal-border);
            border-left: 4px solid var(--primary);
        }}
        
        .input-group {{
            margin-bottom: 18px;
        }}
        .input-group label {{
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            color: var(--primary);
            text-transform: uppercase;
        }}
        .input-group input, .input-group select {{
            width: 100%;
            padding: 12px;
            border-radius: 2px;
            border: 1px solid var(--terminal-border);
            background: #02050a;
            color: var(--primary);
            box-sizing: border-box;
            font-size: 15px;
            font-family: 'Courier New', Courier, monospace;
        }}
        .input-group input:focus, .input-group select:focus {{
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 8px rgba(0, 255, 102, 0.4);
        }}
        
        .btn-container {{
            display: flex;
            gap: 12px;
            margin-top: 10px;
        }}
        button {{
            flex: 1;
            padding: 14px;
            color: #000;
            border: none;
            border-radius: 2px;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            cursor: pointer;
            transition: 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            text-transform: uppercase;
        }}
        .btn-like {{ background: var(--primary); box-shadow: 0 0 10px rgba(0, 255, 102, 0.3); }}
        .btn-like:hover {{ background: var(--primary-hover); box-shadow: 0 0 15px var(--primary); }}
        .btn-info {{ background: var(--secondary); box-shadow: 0 0 10px rgba(0, 229, 255, 0.3); }}
        .btn-info:hover {{ background: var(--secondary-hover); box-shadow: 0 0 15px var(--secondary); }}
        
        #result {{
            margin-top: 20px;
            display: none;
            font-size: 13px;
            line-height: 1.6;
        }}
        .success-res {{ background: #041a10; border: 1px solid var(--primary); padding: 15px; border-radius: 2px; color: var(--primary); }}
        .error-res {{ background: #1a0505; border: 1px solid var(--alert-red); padding: 15px; border-radius: 2px; color: var(--alert-red); }}
        
        /* प्रोफाइल कार्ड डिजाइन */
        .info-card {{
            background: #02050a;
            border: 1px solid var(--terminal-border);
            border-radius: 2px;
            padding: 15px;
        }}
        .section-title {{
            color: var(--secondary);
            font-size: 13px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 15px 0 8px 0;
            padding-bottom: 4px;
            border-bottom: 1px dashed var(--terminal-border);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .section-title:first-of-type {{ margin-top: 0; }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(0, 255, 102, 0.05);
        }}
        .info-label {{ color: #6482a6; font-size: 12px; }}
        .info-value {{ color: var(--text-main); font-weight: bold; font-size: 12.5px; }}
        
        .val-highlight {{ color: #ffaa00; }}
        .val-success {{ color: var(--primary); }}
        .val-heart {{ color: #ff0077; }}
        
        .info-sig {{
            background: rgba(0, 255, 102, 0.02);
            padding: 10px;
            border-radius: 2px;
            margin-top: 5px;
            border-left: 3px solid var(--secondary);
            font-style: italic;
            color: #a4b8c9;
            font-size: 12px;
            word-break: break-all;
        }}

        .raw-data-box {{
            background: #010204;
            border: 1px solid var(--terminal-border);
            border-radius: 2px;
            padding: 12px;
            margin-top: 15px;
            max-height: 250px;
            overflow-y: auto;
        }}
        .raw-data-box pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', Courier, monospace;
            font-size: 11px;
            color: var(--secondary);
        }}

        .loader {{ display: none; text-align: center; margin-top: 15px; color: var(--primary); }}
    </style>
</head>
<body>

<div class="links-menu-overlay" id="menuOverlay" onclick="toggleMenu(false)">
    <div class="links-menu" onclick="event.stopPropagation()">
        <div class="menu-header">
            <h2><i class="fa-solid fa-code-branch"></i> TERMINAL NAV</h2>
            <button class="close-menu-btn" onclick="toggleMenu(false)"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="menu-grid">
            {menu_buttons_html}
        </div>
    </div>
</div>

<div class="container">
    <button type="button" class="menu-trigger-btn" onclick="toggleMenu(true)">
        <i class="fa-solid fa-terminal"></i> MENU
    </button>

<div class="ascii-header">
███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██╗  ██╗ █████╗ ██╗██╗   ██╗ █████╗ 
██╔════╝    ██║ ██╔╝██╔══██╗████╗  ██║██║  ██║██╔══██╗██║╚██╗ ██╔╝██╔══██╗
███████╗    █████╔╝ ███████║██╔██╗ ██║███████║███████║██║ ╚████╔╝ ███████║
╚════██║    ██╔═██╗ ██╔══██║██║╚██╗██║██╔══██║██╔══██║██║  ╚██╔╝  ██╔══██║
███████║    ██║  ██╗██║  ██║██║ ╚████║██║  ██║██║  ██║██║   ██║   ██║  ██║
╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝
[ SYSTEM v1.0 ]</div>


    <h1>FF MULTI-EXTRACTOR</h1>
    <div class="subtitle">Secure Request Terminal</div>

    <div class="stats-box">
        <span>STATUS: <strong style="color: var(--primary);">{bot_status}</strong></span>
        <span>LIMIT: <strong>{remaining} / {daily_limit}</strong></span>
    </div>

    <form id="toolForm">
        <div class="input-group">
            <label><i class="fa-solid fa-network-wired"></i> SELECT REGION</label>
            <select name="region" id="region">
                <option value="IND">India (IND)</option>
                <option value="BD">Bangladesh (BD)</option>
                <option value="PK">Pakistan (PK)</option>
                <option value="USA">USA</option>
                <option value="BR">Brazil</option>
            </select>
        </div>

        <div class="input-group">
            <label><i class="fa-solid fa-fingerprint"></i> TARGET PLAYER UID</label>
            <input type="text" name="uid" id="uid" placeholder="Enter target UID..." required>
        </div>

        <div class="btn-container">
            <button type="button" class="btn-info" onclick="processAction('info')">
                <i class="fa-solid fa-shield-halved"></i> FETCH INFO
            </button>
            <button type="button" class="btn-like" onclick="processAction('like')">
                <i class="fa-solid fa-heart-pulse"></i> INJECT LIKE
            </button>
        </div>
    </form>

    <div class="loader" id="loader">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="margin-bottom: 10px;"></i>
        <p style="margin:0; font-size:12px;" id="loaderText">CONNECTING TO SERVER...</p>
    </div>

    <div id="result"></div>
</div>

<script>
    function toggleMenu(show) {{
        document.getElementById('menuOverlay').style.display = show ? 'block' : 'none';
    }}

    async function processAction(actionType) {{
        const region = document.getElementById('region').value;
        const uid = document.getElementById('uid').value;
        const loader = document.getElementById('loader');
        const loaderText = document.getElementById('loaderText');
        const resultDiv = document.getElementById('result');

        if (!uid.trim()) {{
            alert("ALERT: Target UID required!");
            return;
        }}

        resultDiv.style.display = 'none';
        loader.style.display = 'block';
        
        if (actionType === 'like') {{
            loaderText.innerText = "INJECTING EXPLOIT: Sending likes to node...";
        }} else {{
            loaderText.innerText = "DECRYPTING NODE: Extracting profile layout...";
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
                    resultDiv.innerHTML = "<h3>⚡ PACKET INJECTED SUCCESSFULLY!</h3>" +
                        "<b>TARGET ALIAS:</b> " + data.player + "<br>" +
                        "<b>UID Hash:</b> <code>" + data.uid + "</code><br>" +
                        "<b>NODE LEVEL:</b> " + data.level + "<br>" +
                        "<b>LOAD SENT:</b> +" + data.given + "<br>" +
                        "<b>DATABASE SYNC:</b> " + data.before + " ➔ " + data.after;
                }} else {{
                    resultDiv.removeAttribute('class');
                    
                    let res = data.info;
                    let rawJsonString = JSON.stringify(data.raw, null, 4);

                    let infoHTML = '<div class="info-card">' +
                        '<div class="section-title"><i class="fa-solid fa-terminal"></i> CORE REGISTRY DATA</div>' +
                        '<div class="info-row"><span class="info-label">ALIAS (Name):</span><span class="info-value val-highlight">' + res.nickname + '</span></div>' +
                        '<div class="info-row"><span class="info-label">ACCOUNT ID:</span><span class="info-value">' + res.uid + '</span></div>' +
                        '<div class="info-row"><span class="info-label">ZONE:</span><span class="info-value">' + res.region + '</span></div>' +
                        '<div class="info-row"><span class="info-label">TIER LEVEL:</span><span class="info-value val-success">' + res.level + '</span></div>' +
                        '<div class="info-row"><span class="info-label">EXP COUNTER:</span><span class="info-value">' + res.exp + '</span></div>' +
                        '<div class="info-row"><span class="info-label">VALOR LIKES:</span><span class="info-value val-heart"><i class="fa-solid fa-heart"></i> ' + res.likes + '</span></div>' +
                        '<div class="info-row"><span class="info-label">AUTH METHOD:</span><span class="info-value">' + res.account_type + '</span></div>' +
                        '<div class="info-row"><span class="info-label">STAMP TIMESTAMP:</span><span class="info-value">' + res.create_at + '</span></div>' +
                        
                        '<div class="section-title"><i class="fa-solid fa-trophy"></i> RANK LOG DATA</div>' +
                        '<div class="info-row"><span class="info-label">BR RATING POINTS:</span><span class="info-value val-highlight">' + res.br_points + '</span></div>' +
                        '<div class="info-row"><span class="info-label">CS SCORE POINTS:</span><span class="info-value val-highlight">' + res.cs_points + '</span></div>' +
                        '<div class="info-row"><span class="info-label">PEAK RANK RECORD:</span><span class="info-value">' + res.max_rank + '</span></div>' +
                        '<div class="info-row"><span class="info-label">INTEGRITY MATRIX:</span><span class="info-value val-success">' + res.credit_score + '</span></div>' +
                        '<div class="info-row"><span class="info-label">LAST ONLINE PING:</span><span class="info-value">' + res.last_login + '</span></div>' +

                        '<div class="section-title"><i class="fa-solid fa-paw"></i> COMPANION ID</div>' +
                        '<div class="info-row"><span class="info-label">PET HASH ID:</span><span class="info-value">' + res.pet_id + '</span></div>' +
                        '<div class="info-row"><span class="info-label">PET STAGE LVL:</span><span class="info-value">' + res.pet_level + '</span></div>' +
                        
                        '<div class="section-title"><i class="fa-solid fa-signature"></i> SIGNATURE MATRIX</div>' +
                        '<div class="info-sig">' + res.signature + '</div>' +

                        '<div class="section-title" style="color: #a78bfa;"><i class="fa-solid fa-code"></i> RAW DATAFRAME PAYLOAD</div>' +
                        '<div class="raw-data-box">' +
                            '<pre>' + rawJsonString + '</pre>' +
                        '</div>' +
                    '</div>';
                    
                    resultDiv.innerHTML = infoHTML;
                }}
            }} else {{
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = "❌ FAULT ERROR: " + data.message;
            }}
        }} catch (error) {{
            loader.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.className = 'error-res';
            resultDiv.innerHTML = "❌ CONNECTION FAILURE: Server node unreachable.";
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
    
    buttons_html = ""
    for item in MENU_LINKS:
        buttons_html += f'<a href="{item["url"]}" target="_blank" class="menu-link-item">{item["title"]} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 11px;"></i></a>\n'
    
    return HTML_TEMPLATE.format(
        bot_status=bot_status.upper(),
        remaining=remaining,
        daily_limit=daily_limit,
        menu_buttons_html=buttons_html
    )

@app.post("/api/process")
async def process(request: Request, region: str = Form(...), uid: str = Form(...), action: str = Form(...)):
    if bot_status == "off":
        return JSONResponse({"status": "error", "message": "वेबसाइट अभी मेंटेनेंस में है।"})
    
    client_ip = request.client.host or "127.0.0.1"
    region = region.lower()
    
    if not uid.isdigit():
        return JSONResponse({"status": "error", "message": "UID केवल अंकों (Numbers) में होनी चाहिए!"})

    # ---- प्लेयर इन्फो एक्शन ----
    if action == "info":
        try:
            url = f"{INFO_API_URL}?region={region}&uid={uid}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                    if resp.status == 200:
                        raw_data = await resp.json()
                        
                        basic = raw_data.get("BasicInfo") or raw_data.get("basicInfo") or {}
                        social = raw_data.get("socialInfo") or raw_data.get("SocialInfo") or {}
                        credit = raw_data.get("creditScoreInfo") or raw_data.get("CreditScoreInfo") or {}
                        pet = raw_data.get("petInfo") or raw_data.get("PetInfo") or {}
                        
                        last_login_ts = basic.get("lastLoginAt") or basic.get("lastLogin") or 0
                        create_at_ts = basic.get("createAt") or basic.get("createTime") or 0
                        
                        try:
                            last_login = datetime.fromtimestamp(int(last_login_ts)).strftime('%d-%m-%Y %H:%M') if last_login_ts else "N/A"
                        except: last_login = "N/A"
                            
                        try:
                            create_at = datetime.fromtimestamp(int(create_at_ts)).strftime('%d-%m-%Y') if create_at_ts else "N/A"
                        except: create_at = "N/A"

                        gender_raw = social.get("gender", "N/A")
                        gender = "Female ♀️" if "FEMALE" in gender_raw.upper() else "Male ♂️" if "MALE" in gender_raw.upper() else "N/A"
                        prefer_mode = social.get("modePrefer", "N/A").replace("ModePrefer_", "")

                        clean_profile = {
                            "nickname": basic.get("nickname") or basic.get("Nickname") or "Unknown",
                            "uid": basic.get("accountId") or uid,
                            "region": basic.get("region", region.upper()),
                            "level": basic.get("level", "N/A"),
                            "exp": basic.get("exp", "N/A"),
                            "likes": basic.get("liked") or basic.get("Liked") or 0,
                            "account_type": "Google/FB" if basic.get("accountType") == 1 else "Guest/Other",
                            "create_at": create_at,
                            "br_points": basic.get("rankingPoints", "N/A"),
                            "cs_points": basic.get("csRank", "N/A"),
                            "max_rank": basic.get("maxRank", "N/A"),
                            "credit_score": credit.get("creditScore", "N/A"),
                            "last_login": last_login,
                            "pet_id": pet.get("id", "No Pet"),
                            "pet_level": pet.get("level", "N/A"),
                            "prefer_mode": prefer_mode,
                            "gender": gender,
                            "signature": social.get("signature") or "No Signature Set"
                        }
                        
                        return JSONResponse({
                            "status": "success", 
                            "info": clean_profile,
                            "raw": raw_data
                        })
                    else:
                        return JSONResponse({"status": "error", "message": f"इन्फो एपीआई एरर: HTTP {resp.status}"})
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"इन्फो निकालने में विफल: {str(e)}"})

    # ---- लाइक भेजने का एक्शन ----
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
