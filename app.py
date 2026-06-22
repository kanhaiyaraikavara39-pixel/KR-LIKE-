import os
import json
import base64
import aiohttp
import asyncio
from datetime import date, datetime, timedelta
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

# ============ CONFIGURATION ============
LIKE_API_URL = "https://kanhaiya-raikwar.vercel.app/"
INFO_API_URL = "https://s-kanhaiya-ff-info.vercel.app/player-info"
TOKEN_API_URL = "https://jwt-id-token.vercel.app/api/token"

# 🔄 GITHUB TOKEN UPDATE API
GITHUB_UPDATE_API = "https://github-token-aoto-update-tvnu.vercel.app/api/update?key=KaNhAiYa"

ENCODED_KEY = "WkVYWFk="
API_KEY = base64.b64decode(ENCODED_KEY).decode()

# 🔐 एडमिन लॉगिन क्रेडेंशियल्स
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Kanhaiya@789"

# 💰 UPI कॉन्फ़िगरेशन
UPI_ID = "9230844760@fam"

DATA_FILES = {
    'stats': '/tmp/daily_stats.json',
    'users': '/tmp/user_limits.json',
    'config': '/tmp/bot_config.json',
    'subs': '/tmp/subscriptions.json'
}

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
subscriptions = {"pending": [], "active": []}
daily_limit = 2

def load_data():
    global daily_stats, user_limits, bot_status, daily_limit, subscriptions
    try:
        with open(DATA_FILES['stats'], 'r') as f: daily_stats = json.load(f)
    except: daily_stats = {}
    try:
        with open(DATA_FILES['users'], 'r') as f: user_limits = json.load(f)
    except: user_limits = {}
    try:
        with open(DATA_FILES['subs'], 'r') as f: subscriptions = json.load(f)
    except: subscriptions = {"pending": [], "active": []}
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
        with open(DATA_FILES['subs'], 'w') as f: json.dump(subscriptions, f, indent=2)
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

def admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Admin Credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ============ 🔄 BACKGROUND TASK: GITHUB TOKEN AUTO UPDATE (8 HOURS) ============
async def github_token_auto_updater():
    # पहला अपडेट सर्वर चालू होते ही तुरंत होगा
    await asyncio.sleep(5) 
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(GITHUB_UPDATE_API, timeout=15) as resp:
                    await resp.text()
        except:
            pass
        # 8 घंटे का इंतज़ार (8 * 3600 सेकंड)
        await asyncio.sleep(8 * 3600)

# ============ ⏰ BACKGROUND AUTO-LIKE TASK (CRON) ============
async def daily_auto_like_cron():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now > target_time:
            target_time += timedelta(days=1)
        
        sleep_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(sleep_seconds)
        
        load_data()
        today = date.today()
        still_active = []
        
        for sub in subscriptions.get("active", []):
            exp_date = datetime.strptime(sub["expiry"], "%Y-%m-%Y").date() if "-" in sub["expiry"] else today
            if today <= exp_date:
                uid = sub["uid"]
                for _ in range(10):
                    try:
                        url = f"{LIKE_API_URL}like?uid={uid}&region=IND&key={API_KEY}"
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=10) as resp:
                                await resp.json()
                    except:
                        pass
                    await asyncio.sleep(1)
                still_active.append(sub)
        
        subscriptions["active"] = still_active
        save_all()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(daily_auto_like_cron())
    asyncio.create_task(github_token_auto_updater())

# ============ HTML + CSS + JS (CORE UI) ============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ S.KANHAIYA COLORFUL SYSTEM v2.0 ⚡</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #02040a;
            --card-bg: rgba(10, 15, 30, 0.75);
            --primary: #00ffaa;
            --primary-glow: rgba(0, 255, 170, 0.4);
            --secondary: #00e5ff;
            --secondary-glow: rgba(0, 229, 255, 0.4);
            --accent: #ff0077;
            --accent-glow: rgba(255, 0, 119, 0.4);
            --text-main: #f0f5ff;
            --terminal-border: #223355;
            --alert-red: #ff3355;
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
            overflow-x: hidden;
        }}
        
        #matrixCanvas {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.4; /* एनीमेशन को और अच्छे से दिखाने के लिए विजिबिलिटी बढ़ा दी */
        }}
        
        .container {{
            background: var(--card-bg);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 0 40px rgba(0, 229, 255, 0.2), inset 0 0 20px rgba(255, 0, 119, 0.1);
            width: 100%;
            max-width: 500px;
            border: 2px solid transparent;
            background-image: linear-gradient(var(--card-bg), var(--card-bg)), linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
            background-origin: border-box;
            background-clip: padding-box, border-box;
            box-sizing: border-box;
            position: relative;
            backdrop-filter: blur(10px);
        }}
        
        .brand-header {{
            text-align: center;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 5px;
            margin-bottom: 5px;
            background: linear-gradient(90deg, #ff0077, #00e5ff, #00ffaa, #ffaa00, #ff0077);
            background-size: 400% 100%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: flowColors 6s linear infinite;
            text-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        }}

        @keyframes flowColors {{
            0% {{ background-position: 0% 50%; }}
            100% {{ background-position: 100% 50%; }}
        }}

        .top-action-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .menu-trigger-btn {{
            background: transparent;
            color: var(--secondary);
            border: 1px solid var(--secondary);
            padding: 6px 12px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            width: auto;
            flex: none;
        }}
        .menu-trigger-btn:hover {{
            background: rgba(0, 229, 255, 0.2);
            box-shadow: 0 0 10px var(--secondary);
        }}

        /* 🔄 छोटा टोकन अपडेट बटन */
        .token-update-btn {{
            background: transparent;
            color: #ffaa00;
            border: 1px solid #ffaa00;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            width: auto;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .token-update-btn:hover {{
            background: rgba(255, 170, 0, 0.2);
            box-shadow: 0 0 10px #ffaa00;
        }}

        .links-menu-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.85);
            z-index: 999;
            backdrop-filter: blur(5px);
        }}
        .links-menu {{
            position: fixed;
            top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #090d16;
            border: 2px solid var(--accent);
            border-radius: 6px;
            width: 90%; max-width: 400px; max-height: 75vh;
            overflow-y: auto; padding: 20px;
            box-shadow: 0 0 30px var(--accent-glow);
            z-index: 1000; box-sizing: border-box;
        }}
        .menu-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px; padding-bottom: 10px;
            border-bottom: 1px solid var(--accent);
        }}
        .menu-header h2 {{ margin: 0; font-size: 16px; color: var(--accent); letter-spacing: 1px; }}
        .close-menu-btn {{ background: none; border: none; color: var(--text-main); font-size: 20px; cursor: pointer; padding: 0; width: auto; }}
        .close-menu-btn:hover {{ color: var(--alert-red); }}
        
        .menu-grid {{ display: grid; grid-template-columns: 1fr; gap: 10px; }}
        .menu-link-item {{
            background: #0d1527; color: var(--text-main); padding: 12px; border-radius: 4px;
            text-decoration: none; font-size: 13px; font-weight: bold;
            display: flex; align-items: center; justify-content: space-between;
            border: 1px solid var(--terminal-border); transition: 0.2s;
        }}
        .menu-link-item:hover {{
            background: rgba(255, 0, 119, 0.15); color: var(--accent);
            transform: translateX(4px); border-color: var(--accent);
        }}

        h1 {{
            text-align: center;
            color: var(--secondary);
            font-size: 20px;
            margin: 5px 0;
            letter-spacing: 2px;
            text-shadow: 0 0 8px var(--secondary-glow);
        }}
        .subtitle {{
            text-align: center;
            color: #64748b;
            font-size: 11px;
            margin-bottom: 25px;
            text-transform: uppercase;
        }}
        
        .stats-box {{
            background: rgba(13, 22, 43, 0.9);
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            border: 1px solid var(--terminal-border);
            border-left: 4px solid var(--primary);
        }}
        
        .input-group {{ margin-bottom: 18px; }}
        .input-group label {{
            display: block; margin-bottom: 8px; font-size: 12px;
            color: var(--secondary); text-transform: uppercase; font-weight: bold;
        }}
        .input-group input, .input-group select {{
            width: 100%; padding: 12px; border-radius: 4px;
            border: 1px solid var(--terminal-border); background: #040812;
            color: #ffffff; box-sizing: border-box; font-size: 14px;
            font-family: 'Courier New', Courier, monospace;
        }}
        .input-group input:focus, .input-group select:focus {{
            border-color: var(--secondary); outline: none; box-shadow: 0 0 8px var(--secondary-glow);
        }}
        
        .btn-container {{ display: flex; gap: 12px; margin-top: 10px; }}
        button {{
            flex: 1; padding: 14px; color: #000000; border: none; border-radius: 4px;
            font-size: 13px; font-weight: 900; font-family: 'Courier New', Courier, monospace;
            cursor: pointer; transition: 0.2s; display: flex; align-items: center;
            justify-content: center; gap: 8px; text-transform: uppercase;
        }}
        .btn-like {{ background: var(--primary); box-shadow: 0 0 10px var(--primary-glow); }}
        .btn-like:hover {{ background: #00dd99; box-shadow: 0 0 15px var(--primary); }}
        .btn-info {{ background: var(--secondary); box-shadow: 0 0 10px var(--secondary-glow); }}
        .btn-info:hover {{ background: #00bcd4; box-shadow: 0 0 15px var(--secondary); }}
        .btn-token {{ background: var(--accent); box-shadow: 0 0 10px var(--accent-glow); color: #ffffff; }}
        .btn-token:hover {{ background: #e00066; box-shadow: 0 0 15px var(--accent); }}
        .btn-auto-plan {{ background: linear-gradient(135deg, #ffaa00, #ff4400); color: white; margin-top: 15px; box-shadow: 0 0 12px rgba(255,85,0,0.4); }}
        .btn-auto-plan:hover {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(255,85,0,0.6); }}
        
        .panel-divider {{ margin: 30px 0 20px 0; border: none; border-top: 2px dashed var(--terminal-border); text-align: center; }}
        
        #result, #tokenResult, #autoResult {{ margin-top: 20px; display: none; font-size: 13px; line-height: 1.6; }}
        .success-res {{ background: #022c16; border: 1px solid var(--primary); padding: 15px; border-radius: 4px; color: var(--primary); }}
        .error-res {{ background: #2d0606; border: 1px solid var(--alert-red); padding: 15px; border-radius: 4px; color: var(--alert-red); }}
        
        /* 🎁 SUBSCRIPTION MODAL POPUP */
        .sub-modal {{
            display: none; position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9); z-index: 1001; backdrop-filter: blur(8px);
            justify-content: center; align-items: center; padding: 10px; box-sizing: border-box;
        }}
        .sub-modal-content {{
            background: #090f1c; border: 2px solid #ffaa00; border-radius: 8px;
            width: 100%; max-width: 440px; padding: 20px;
            box-shadow: 0 0 30px rgba(255,170,0,0.3); box-sizing: border-box; position: relative;
        }}
        .plan-cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 15px 0; }}
        .plan-card {{ border: 1px solid var(--terminal-border); background: #040812; padding: 12px; border-radius: 6px; text-align: center; cursor: pointer; transition: 0.2s; }}
        .plan-card.selected {{ border-color: #ffaa00; background: rgba(255,170,0,0.1); box-shadow: 0 0 10px rgba(255,170,0,0.2); }}
        .qr-area {{ text-align: center; margin: 15px 0; display: none; }}
        .qr-area img {{ border: 4px solid white; border-radius: 4px; background: white; }}

        .info-card {{ background: #040812; border: 1px solid var(--terminal-border); border-radius: 4px; padding: 15px; }}
        .section-title {{
            color: var(--secondary); font-size: 13px; font-weight: bold; text-transform: uppercase;
            letter-spacing: 1px; margin: 15px 0 8px 0; padding-bottom: 4px;
            border-bottom: 1px dashed var(--terminal-border); display: flex; align-items: center; gap: 6px;
        }}
        .info-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(0, 255, 170, 0.05); }}
        .info-label {{ color: #64748b; font-size: 12px; }}
        .info-value {{ color: var(--text-main); font-weight: bold; font-size: 12.5px; }}
        
        .val-highlight {{ color: #ffaa00; }}
        .val-success {{ color: var(--primary); }}
        .val-heart {{ color: var(--accent); }}
        .info-sig {{ background: rgba(0, 255, 170, 0.02); padding: 10px; border-radius: 4px; margin-top: 5px; border-left: 3px solid var(--secondary); font-style: italic; color: #94a3b8; font-size: 12px; word-break: break-all; }}
        .raw-data-box {{ background: #010204; border: 1px solid var(--terminal-border); border-radius: 4px; padding: 12px; margin-top: 15px; max-height: 200px; overflow-y: auto; }}
        .raw-data-box pre {{ margin: 0; white-space: pre-wrap; word-wrap: break-word; font-family: 'Courier New', Courier, monospace; font-size: 11px; color: var(--secondary); }}
        .loader {{ display: none; text-align: center; margin-top: 15px; color: var(--secondary); }}
    </style>
</head>
<body>

<canvas id="matrixCanvas"></canvas>

<div class="links-menu-overlay" id="menuOverlay" onclick="toggleMenu(false)">
    <div class="links-menu" onclick="event.stopPropagation()">
        <div class="menu-header">
            <h2><i class="fa-solid fa-code-branch"></i> TERMINAL NAVIGATION</h2>
            <button class="close-menu-btn" onclick="toggleMenu(false)"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div class="menu-grid">
            {menu_buttons_html}
        </div>
    </div>
</div>

<div class="sub-modal" id="subModal">
    <div class="sub-modal-content">
        <button class="close-menu-btn" style="position:absolute; top:12px; right:15px;" onclick="toggleSubModal(false)"><i class="fa-solid fa-xmark"></i></button>
        <div class="brand-header" style="font-size: 20px; color: #ffaa00;">AUTO LIKE SYSTEM</div>
        <p style="font-size:11px; text-align:center; margin:0 0 10px 0; color:#64748b;">हर सुबह ऑटोमैटिक 100 लाइक्स भेजे जाएंगे</p>
        
        <div class="plan-cards">
            <div class="plan-card" id="plan1" onclick="selectPlan(49, 20)">
                <h4 style="margin:0; color:#ffaa00;">₹ 49 PLAN</h4>
                <p style="margin:5px 0 0 0; font-size:12px;">20 दिन वैलिडिटी</p>
            </div>
            <div class="plan-card" id="plan2" onclick="selectPlan(60, 30)">
                <h4 style="margin:0; color:#ffaa00;">₹ 60 PLAN</h4>
                <p style="margin:5px 0 0 0; font-size:12px;">30 दिन वैलिडिटी</p>
            </div>
        </div>

        <div class="qr-area" id="qrArea">
            <p style="font-size:12px; color:var(--primary); margin-bottom:8px;">स्कैन करके पेमेंट करें:</p>
            <img id="payQr" src="" width="160" height="160">
            <p style="font-size:11px; color:#ffffff; margin:6px 0;">UPI: <code style="color:#00e5ff;">{upi_id}</code></p>
            
            <div class="input-group" style="margin-top:12px; text-align:left;">
                <label>TARGET PLAYER UID</label>
                <input type="text" id="subUid" placeholder="जिस UID पर ऑटो लाइक चाहिए...">
            </div>
            <div class="input-group" style="text-align:left;">
                <label>TRANSACTION ID / UTR</label>
                <input type="text" id="subTxid" placeholder="पेमेंट का Transaction ID डालें...">
            </div>
            <button type="button" class="btn-like" style="background:#ffaa00; font-size:12px;" onclick="submitSubRequest()">
                <i class="fa-solid fa-paper-plane"></i> SUBMIT TO ADMIN
            </button>
        </div>
        <div id="autoResult"></div>
    </div>
</div>

<div class="container">
    <div class="top-action-bar">
        <button type="button" class="menu-trigger-btn" onclick="toggleMenu(true)">
            <i class="fa-solid fa-bars"></i> LINKS
        </button>
        
        <button type="button" class="token-update-btn" onclick="triggerManualTokenUpdate()">
            <i class="fa-solid fa-arrows-rotate"></i> TOKEN UPDATE
        </button>
    </div>

    <div class="brand-header">S.KANHAIYA</div>

    <h1>FF MULTI-EXTRACTOR</h1>
    <div class="subtitle">Secure Node Control Center</div>

    <div class="stats-box">
        <span>SYSTEM STATUS: <strong style="color: var(--primary);">{bot_status}</strong></span>
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
            <input type="text" name="uid" id="uid" placeholder="Enter target player UID...">
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
    
    <button type="button" class="btn-auto-plan" onclick="toggleSubModal(true)">
        <i class="fa-solid fa-bolt"></i> ACTIVATE AUTO-LIKE BOT (₹49 / ₹60)
    </button>
    
    <div class="loader" id="loader">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x"></i>
        <p style="margin:5px 0 0 0; font-size:12px;" id="loaderText">CONNECTING TO NODES...</p>
    </div>
    <div id="result"></div>

    <div class="panel-divider"></div>

    <div class="brand-header" style="font-size: 18px; color: var(--accent);">GUEST TOKEN CREATOR</div>
    <form id="tokenForm" style="margin-top: 15px;">
        <div class="input-group">
            <label><i class="fa-solid fa-user-secret"></i> GUEST ID / UID</label>
            <input type="text" id="tokenUid" placeholder="Enter guest account UID...">
        </div>
        <div class="input-group">
            <label><i class="fa-solid fa-key"></i> ACCOUNT PASSWORD</label>
            <input type="password" id="tokenPassword" placeholder="Enter guest account password...">
        </div>
        <button type="button" class="btn-token" onclick="generateGuestToken()">
            <i class="fa-solid fa-unlock-keyhole"></i> GENERATE TOKEN PAYLOAD
        </button>
    </form>
    
    <div class="loader" id="tokenLoader" style="color: var(--accent);">
        <i class="fa-solid fa-terminal fa-spin fa-2x"></i>
        <p style="margin:5px 0 0 0; font-size:12px;">DECRYPTING JWT HANDSHAKE...</p>
    </div>
    <div id="tokenResult"></div>
</div>

<script>
    let selectedAmount = 0;
    let selectedDays = 0;

    // ⚡ SUPER ATTRACTIVE NEON RGB MATRIX DIGITAL RAIN ENGINE ⚡
    const canvas = document.getElementById('matrixCanvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {{
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }}
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+-=🔥⚡💎⭐'.split('');
    const fontSize = 15;
    const columns = canvas.width / fontSize;
    const rainDrops = [];
    for (let x = 0; x < columns; x++) {{ rainDrops[x] = Math.random() * -100; }}

    // अट्रैक्टिव नियॉन और आरजीबी कलर पैलेट
    const colors = ['#00ffaa', '#00e5ff', '#ff0077', '#ffaa00', '#00ff66'];

    function drawMatrix() {{
        ctx.fillStyle = 'rgba(2, 4, 10, 0.08)'; // धीरे-धीरे फेड होने वाला शानदार ट्रेल
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.font = 'bold ' + fontSize + 'px monospace';
        
        for (let i = 0; i < rainDrops.length; i++) {{
            const text = matrixChars[Math.floor(Math.random() * matrixChars.length)];
            
            // कलरफुल रैंडम नियॉन लुक सेलेक्शन
            ctx.fillStyle = colors[i % colors.length];
            
            // पहली बूंद को ग्लोइंग वाइट इफ़ेक्ट देना
            if (Math.random() > 0.98) {{
                ctx.fillStyle = '#ffffff';
            }}
            
            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
            
            if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                rainDrops[i] = 0;
            }}
            rainDrops[i]++;
        }}
    }}
    setInterval(drawMatrix, 30);

    // 🔄 मैनुअल टोकन अपडेट फंक्शनलिटी
    async function triggerManualTokenUpdate() {{
        alert("टोकन अपडेट रिक्वेस्ट सेंड कर दी गई है...");
        try {{
            const response = await fetch('/api/manual-token-update', {{ method: 'POST' }});
            const data = await response.json();
            alert("✅ " + data.message);
        }} catch(e) {{
            alert("❌ टोकन अपडेट एपीआई टाइमआउट!");
        }}
    }}

    function toggleMenu(show) {{ document.getElementById('menuOverlay').style.display = show ? 'block' : 'none'; }}
    function toggleSubModal(show) {{
        document.getElementById('subModal').style.display = show ? 'flex' : 'none';
        if(!show) {{ document.getElementById('autoResult').style.display = 'none'; }}
    }}

    function selectPlan(amount, days) {{
        selectedAmount = amount;
        selectedDays = days;
        document.getElementById('plan1').className = amount === 49 ? 'plan-card selected' : 'plan-card';
        document.getElementById('plan2').className = amount === 60 ? 'plan-card selected' : 'plan-card';
        
        const upiStr = "upi://pay?pa={upi_id}&pn=SKANHAIYA&am=" + amount + "&cu=INR&tn=AutoLike_" + days + "Days";
        document.getElementById('payQr').src = "https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=" + encodeURIComponent(upiStr);
        document.getElementById('qrArea').style.display = 'block';
    }}

    async function submitSubRequest() {{
        const uid = document.getElementById('subUid').value;
        const txid = document.getElementById('subTxid').value;
        const resultDiv = document.getElementById('autoResult');

        if(!uid.trim() || !txid.trim()) {{ alert("UID और Transaction ID डालना अनिवार्य है!"); return; }}

        const formData = new FormData();
        formData.append('uid', uid);
        formData.append('txid', txid);
        formData.append('amount', selectedAmount);
        formData.append('days', selectedDays);

        try {{
            const response = await fetch('/api/submit-subscription', {{ method: 'POST', body: formData }});
            const data = await response.json();
            resultDiv.style.display = 'block';
            if(data.status === 'success') {{
                resultDiv.className = 'success-res';
                resultDiv.innerHTML = "✅ " + data.message;
            }} else {{
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = "❌ " + data.message;
            }}
        }} catch(e) {{
            resultDiv.style.display = 'block'; resultDiv.className = 'error-res';
            resultDiv.innerHTML = "❌ सर्वर से कनेक्शन फ़ेल हुआ।";
        }}
    }}

    async function processAction(actionType) {{
        const region = document.getElementById('region').value;
        const uid = document.getElementById('uid').value;
        const loader = document.getElementById('loader');
        const loaderText = document.getElementById('loaderText');
        const resultDiv = document.getElementById('result');

        if (!uid.trim()) {{ alert("ALERT: Target UID required!"); return; }}

        resultDiv.style.display = 'none';
        loader.style.display = 'block';
        loaderText.innerText = actionType === 'like' ? "INJECTING PACKETS: Auto-retrying on sync failure..." : "SYNCING DATA: Pulling live layout registry...";

        const formData = new FormData();
        formData.append('region', region);
        formData.append('uid', uid);
        formData.append('action', actionType);

        try {{
            const response = await fetch('/api/process', {{ method: 'POST', body: formData }});
            const data = await response.json();
            loader.style.display = 'none';
            resultDiv.style.display = 'block';
            
            if (data.status === 'success') {{
                if (actionType === 'like') {{
                    resultDiv.className = 'success-res';
                    resultDiv.innerHTML = "<h3>⚡ EXPLOIT INJECTED!</h3>" +
                        "<b>PLAYER:</b> " + data.player + "<br>" +
                        "<b>UID:</b> <code>" + data.uid + "</code><br>" +
                        "<b>LEVEL:</b> " + data.level + "<br>" +
                        "<b>BOOSTED:</b> +" + data.given + "<br>" +
                        "<b>REGISTRY SYNC:</b> " + data.before + " ➔ " + data.after;
                }} else {{
                    resultDiv.removeAttribute('class');
                    let res = data.info;
                    let rawJsonString = JSON.stringify(data.raw, null, 4);

                    let infoHTML = '<div class="info-card">' +
                        '<div class="section-title"><i class="fa-solid fa-user"></i> BASIC REGISTRY</div>' +
                        '<div class="info-row"><span class="info-label">NICKNAME:</span><span class="info-value val-highlight">' + res.nickname + '</span></div>' +
                        '<div class="info-row"><span class="info-label">UID HASH:</span><span class="info-value">' + res.uid + '</span></div>' +
                        '<div class="info-row"><span class="info-label">ZONE REGION:</span><span class="info-value">' + res.region + '</span></div>' +
                        '<div class="info-row"><span class="info-label">LEVEL TIER:</span><span class="info-value val-success">' + res.level + '</span></div>' +
                        '<div class="info-row"><span class="info-label">EXP VALUE:</span><span class="info-value">' + res.exp + '</span></div>' +
                        '<div class="info-row"><span class="info-label">CORE LIKES:</span><span class="info-value val-heart"><i class="fa-solid fa-heart"></i> ' + res.likes + '</span></div>' +
                        '<div class="info-row"><span class="info-label">AUTH PLATFORM:</span><span class="info-value">' + res.account_type + '</span></div>' +
                        '<div class="info-row"><span class="info-label">CREATED TIMESTAMP:</span><span class="info-value">' + res.create_at + '</span></div>' +
                        
                        '<div class="section-title"><i class="fa-solid fa-crosshairs"></i> SCORE MATRIX</div>' +
                        '<div class="info-row"><span class="info-label">BR RATING POINTS:</span><span class="info-value val-highlight">' + res.br_points + '</span></div>' +
                        '<div class="info-row"><span class="info-label">CS RANK SCORE:</span><span class="info-value val-highlight">' + res.cs_points + '</span></div>' +
                        '<div class="info-row"><span class="info-label">MAX RANK ACHIEVED:</span><span class="info-value">' + res.max_rank + '</span></div>' +
                        '<div class="info-row"><span class="info-label">INTEGRITY RATING:</span><span class="info-value val-success">' + res.credit_score + '</span></div>' +
                        '<div class="info-row"><span class="info-label">LAST RECORDED ONLINE:</span><span class="info-value">' + res.last_login + '</span></div>' +

                        '<div class="section-title"><i class="fa-solid fa-paw"></i> COMPANION ENTITY</div>' +
                        '<div class="info-row"><span class="info-label">PET DESIGNATION:</span><span class="info-value">' + res.pet_id + '</span></div>' +
                        '<div class="info-row"><span class="info-label">PET LEVEL STAGE:</span><span class="info-value">' + res.pet_level + '</span></div>' +
                        
                        '<div class="section-title"><i class="fa-solid fa-signature"></i> SIGNATURE KEY</div>' +
                        '<div class="info-sig">' + res.signature + '</div>' +

                        '<div class="section-title" style="color: #ff0077;"><i class="fa-solid fa-code"></i> RAW DATAFRAME LAYER</div>' +
                        '<div class="raw-data-box"><pre>' + rawJsonString + '</pre></div>' +
                    '</div>';
                    resultDiv.innerHTML = infoHTML;
                }}
            }} else {{
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = "❌ TRANSACTION FAILURE: " + data.message;
            }}
        }} catch (error) {{
            loader.style.display = 'none'; resultDiv.style.display = 'block'; resultDiv.className = 'error-res';
            resultDiv.innerHTML = "❌ SYSTEM FAULT: Master database offline.";
        }}
    }}

    async function generateGuestToken() {{
        const uid = document.getElementById('tokenUid').value;
        const password = document.getElementById('tokenPassword').value;
        const loader = document.getElementById('tokenLoader');
        const resultDiv = document.getElementById('tokenResult');

        if (!uid.trim() || !password.trim()) {{ alert("ALERT: Token Generation requires UID and Password!"); return; }}

        resultDiv.style.display = 'none'; loader.style.display = 'block';

        const formData = new FormData();
        formData.append('uid', uid);
        formData.append('password', password);

        try {{
            const response = await fetch('/api/generate-token', {{ method: 'POST', body: formData }});
            const data = await response.json();
            loader.style.display = 'none'; resultDiv.style.display = 'block';
            
            if (data.status === 'success') {{
                resultDiv.className = 'success-res'; resultDiv.style.borderColor = 'var(--accent)'; resultDiv.style.color = '#ffffff';
                resultDiv.innerHTML = "<h3>✅ TOKEN CODES GENERATED!</h3>" +
                    "<p style='color:var(--accent); font-weight:bold; margin:5px 0;'>JWT PAYLOAD VALUE:</p>" +
                    "<div class='raw-data-box' style='max-height:150px;'><pre style='color:#ffffff;'>" + JSON.stringify(data.payload, null, 4) + "</pre></div>";
            }} else {{
                resultDiv.className = 'error-res'; resultDiv.style.display = 'block';
                resultDiv.innerHTML = "❌ TOKEN GENERATION FAILED: " + data.message;
            }}
        }} catch(e) {{
            loader.style.display = 'none'; resultDiv.style.display = 'block'; resultDiv.className = 'error-res';
            resultDiv.innerHTML = "❌ ENDPOINT TIMEOUT: Token generation failed.";
        }}
    }}
</script>
</body>
</html>
"""

# ============ ADMIN DASHBOARD UI (HTML) ============
ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>⚡ S.KANHAIYA ADMIN TERMINAL ⚡</title>
    <style>
        body {{ font-family: monospace; background: #030712; color: #00ff66; padding: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid #ffaa00; padding-bottom: 10px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: #090f1c; }}
        th, td {{ border: 1px solid #1e293b; padding: 12px; text-align: left; }}
        th {{ background: #1e293b; color: #00e5ff; }}
        .btn {{ padding: 6px 12px; font-weight: bold; cursor: pointer; border: none; border-radius: 4px; font-family: monospace; }}
        .btn-approve {{ background: #00ff66; color: black; }}
        .btn-reject {{ background: #ff3333; color: white; }}
        .section {{ margin-bottom: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>S.KANHAIYA CONTROL OVERRIDE</h1>
        <p>SECURE ADMIN MANAGEMENT INTERFACE</p>
        <a href="/" style="color:#00e5ff; text-decoration:none;">➔ BACK TO HOME SITE</a>
    </div>

    <div class="section">
        <h2>📥 PENDING PAYMENT OVERVIEW ({pending_count})</h2>
        <table>
            <tr>
                <th>TARGET UID</th>
                <th>TRANSACTION / UTR ID</th>
                <th>PLAN SELECTED</th>
                <th>VALID DAYS</th>
                <th>ACTION TRIGGER</th>
            </tr>
            {pending_rows}
        </table>
    </div>

    <div class="section">
        <h2>✅ ACTIVE AUTO-LIKE BOT QUEUE ({active_count})</h2>
        <table>
            <tr>
                <th>UID</th>
                <th>PLAN STATUS</th>
                <th>EXPIRY DATE</th>
            </tr>
            {active_rows}
        </table>
    </div>
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
        menu_buttons_html=buttons_html,
        upi_id=UPI_ID
    )

# 🔄 यूज़र के बटन दबाने पर चलने वाली मैनुअल टोकन अपडेट API
@app.post("/api/manual-token-update")
async def manual_token_update():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_UPDATE_API, timeout=12) as resp:
                if resp.status == 200:
                    return JSONResponse({"status": "success", "message": "गिटहब टोकन सफलतापूर्वक रिफ्रेश कर दिया गया है!"})
    except:
        pass
    return JSONResponse({"status": "error", "message": "टोकन सर्वर से रिस्पॉन्स नहीं मिला, बैकग्राउंड टास्क चालू है।"})

@app.post("/api/submit-subscription")
async def submit_subscription(uid: str = Form(...), txid: str = Form(...), amount: int = Form(...), days: int = Form(...)):
    if not uid.isdigit() or not txid.strip():
        return JSONResponse({"status": "error", "message": "गलत UID या ट्रांजैक्शन आईडी दी गई है!"})
    
    load_data()
    for req in subscriptions["pending"]:
        if req["txid"] == txid:
            return JSONResponse({"status": "error", "message": "यह Transaction ID पहले से ही वेरिफिकेशन के लिए पेंडिंग है!"})
            
    subscriptions["pending"].append({
        "uid": uid,
        "txid": txid,
        "amount": amount,
        "days": days
    })
    save_all()
    return JSONResponse({"status": "success", "message": "आपकी रिक्वेस्ट एडमिन पैनल में भेज दी गई है। वेरिफिकेशन के तुरंत बाद ऑटो-लाइक चालू कर दिया जाएगा!"})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(username: str = Depends(admin_auth)):
    load_data()
    
    p_rows = ""
    for idx, item in enumerate(subscriptions["pending"]):
        p_rows += f"""
        <tr>
            <td>{item['uid']}</td>
            <td><code>{item['txid']}</code></td>
            <td>₹ {item['amount']}</td>
            <td>{item['days']} दिन</td>
            <td>
                <a href="/admin/approve/{idx}"><button class="btn btn-approve">APPROVE</button></a>
                <a href="/admin/reject/{idx}"><button class="btn btn-reject">REJECT</button></a>
            </td>
        </tr>
        """
    if not p_rows:
        p_rows = "<tr><td colspan='5' style='text-align:center;color:#64748b;'>कोई पेंडिंग रिक्वेस्ट नहीं है</td></tr>"

    a_rows = ""
    for item in subscriptions["active"]:
        a_rows += f"<tr><td>{item['uid']}</td><td>₹{item['amount']} Plan ({item['days']} Days)</td><td>{item['expiry']}</td></tr>"
    if not a_rows:
        a_rows = "<tr><td colspan='3' style='text-align:center;color:#64748b;'>कोई भी बोट एक्टिव नहीं है</td></tr>"
        
    return ADMIN_HTML_TEMPLATE.format(
        pending_count=len(subscriptions["pending"]),
        active_count=len(subscriptions["active"]),
        pending_rows=p_rows,
        active_rows=a_rows
    )

@app.get("/admin/approve/{idx}")
async def approve_sub(idx: int, username: str = Depends(admin_auth)):
    load_data()
    if 0 <= idx < len(subscriptions["pending"]):
        req = subscriptions["pending"].pop(idx)
        expiry_date = (date.today() + timedelta(days=int(req["days"]))).strftime("%d-%m-%Y")
        
        subscriptions["active"].append({
            "uid": req["uid"],
            "amount": req["amount"],
            "days": req["days"],
            "expiry": expiry_date
        })
        save_all()
    return HTMLResponse("<script>alert('Request Approved!'); window.location.href='/admin';</script>")

@app.get("/admin/reject/{idx}")
async def reject_sub(idx: int, username: str = Depends(admin_auth)):
    load_data()
    if 0 <= idx < len(subscriptions["pending"]):
        subscriptions["pending"].pop(idx)
        save_all()
    return HTMLResponse("<script>alert('Request Rejected!'); window.location.href='/admin';</script>")

@app.post("/api/process")
async def process(request: Request, region: str = Form(...), uid: str = Form(...), action: str = Form(...)):
    if bot_status == "off":
        return JSONResponse({"status": "error", "message": "वेबसाइट अभी मेंटेनेंस में है।"})
    
    client_ip = request.client.host or "127.0.0.1"
    region = region.lower()
    
    if not uid.isdigit():
        return JSONResponse({"status": "error", "message": "UID केवल अंकों (Numbers) में होनी चाहिए!"})

    if action == "info":
        url = f"{INFO_API_URL}?region={region}&uid={uid}"
        for _ in range(4):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=6) as resp:
                        if resp.status == 200:
                            raw_data = await resp.json()
                            basic = raw_data.get("BasicInfo") or raw_data.get("basicInfo") or {}
                            social = raw_data.get("socialInfo") or raw_data.get("SocialInfo") or {}
                            credit = raw_data.get("creditScoreInfo") or raw_data.get("CreditScoreInfo") or {}
                            pet = raw_data.get("petInfo") or raw_data.get("PetInfo") or {}
                            
                            last_login_ts = basic.get("lastLoginAt") or basic.get("lastLogin") or 0
                            create_at_ts = basic.get("createAt") or basic.get("createTime") or 0
                            
                            try: last_login = datetime.fromtimestamp(int(last_login_ts)).strftime('%d-%m-%Y %H:%M') if last_login_ts else "N/A"
                            except: last_login = "N/A"
                            try: create_at = datetime.fromtimestamp(int(create_at_ts)).strftime('%d-%m-%Y') if create_at_ts else "N/A"
                            except: create_at = "N/A"

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
                                "signature": social.get("signature") or "No Signature Set"
                            }
                            return JSONResponse({"status": "success", "info": clean_profile, "raw": raw_data})
            except: pass
            await asyncio.sleep(0.1)
        return JSONResponse({"status": "error", "message": "प्लेयर इन्फो सर्वर अभी काफी बिजी है, कृपया दोबारा प्रयास करें!"})

    elif action == "like":
        region_upper = region.upper()
        if not can_user_like(client_ip):
            return JSONResponse({"status": "error", "message": "आज की आपकी लाइक लिमिट खत्म हो चुकी है!"})

        url = f"{LIKE_API_URL}like?uid={uid}&region={region_upper}&key={API_KEY}"
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=8) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('status') == 1:
                                update_user_like(client_ip)
                                return JSONResponse({
                                    "status": "success", "player": data.get('PlayerNickname', 'Unknown'),
                                    "uid": data.get('UID', uid), "region": data.get('Region', region_upper),
                                    "level": data.get('Level', 'N/A'), "given": data.get('LikesGivenByAPI', 0),
                                    "before": data.get('LikesbeforeCommand', 0), "after": data.get('LikesafterCommand', 0)
                                })
                            elif data.get('status') == 2:
                                return JSONResponse({"status": "error", "message": "इस UID की आज की API लिमिट खत्म हो गई है।"})
            except: pass
            await asyncio.sleep(0.1)
        return JSONResponse({"status": "error", "message": "लाइक सर्वर ओवरलोड है, कृपया फिर से कोशिश करें!"})

@app.post("/api/generate-token")
async def generate_token(uid: str = Form(...), password: str = Form(...)):
    url = f"{TOKEN_API_URL}?uid={uid}&password={password}"
    for _ in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=8) as resp:
                    if resp.status == 200:
                        return JSONResponse({"status": "success", "payload": await resp.json()})
        except: pass
        await asyncio.sleep(0.1)
    return JSONResponse({"status": "error", "message": "टोकन एपीआई ने रिस्पॉन्स नहीं दिया।"})
