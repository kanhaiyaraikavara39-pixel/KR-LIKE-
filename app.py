import os
import json
import base64
import aiohttp
import asyncio
from datetime import date, datetime, timedelta
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# 🚀 VERCEL TOP-LEVEL OBJECT
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

# 🐙 GITHUB DATABASE CONFIGURATION (यहाँ अपनी डिटेल्स डालें)
GITHUB_USER = "kanhaiyaraikavara39-pixel"      
GITHUB_REPO = "KR-LIKE"            
GITHUB_TOKEN = "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"        
GITHUB_FILE_PATH = "database.json"

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

# ============ 🐙 GITHUB STORAGE ENGINE ============

async def fetch_from_github():
    global daily_stats, user_limits, bot_status, daily_limit, subscriptions
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    res_json = await resp.json()
                    content_b64 = res_json.get("content", "")
                    if content_b64:
                        dec_data = json.loads(base64.b64decode(content_b64).decode('utf-8'))
                        daily_stats = dec_data.get("daily_stats", {})
                        user_limits = dec_data.get("user_limits", {})
                        subscriptions = dec_data.get("subscriptions", {"pending": [], "active": []})
                        bot_status = dec_data.get("bot_status", "on")
                        daily_limit = dec_data.get("daily_limit", 2)
                        return res_json.get("sha")
    except Exception as e:
        print(f"Error fetching from GitHub: {e}")
    return None

async def save_to_github():
    sha = await fetch_from_github()
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    master_data = {
        "daily_stats": daily_stats,
        "user_limits": user_limits,
        "subscriptions": subscriptions,
        "bot_status": bot_status,
        "daily_limit": daily_limit
    }
    compact_json = json.dumps(master_data, indent=2)
    enc_content = base64.b64encode(compact_json.encode('utf-8')).decode('utf-8')
    payload = {"message": "⚡ System Sync: Database auto-updated", "content": enc_content}
    if sha: payload["sha"] = sha
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=payload, timeout=10) as resp:
                await resp.json()
    except Exception as e:
        print(f"Error saving to GitHub: {e}")

def today_str(): return str(date.today())

async def can_user_like(ip_address):
    await fetch_from_github()
    t = today_str()
    if ip_address not in user_limits or user_limits[ip_address]['date'] != t:
        user_limits[ip_address] = {'date': t, 'count': 0}
        return True
    return user_limits[ip_address]['count'] < daily_limit

async def update_user_like(ip_address):
    t = today_str()
    if ip_address not in user_limits or user_limits[ip_address]['date'] != t:
        user_limits[ip_address] = {'date': t, 'count': 0}
    user_limits[ip_address]['count'] += 1
    if t not in daily_stats: daily_stats[t] = {'total': 0, 'ips': {}}  
    daily_stats[t]['total'] += 1  
    if ip_address not in daily_stats[t]['ips']: daily_stats[t]['ips'][ip_address] = 0  
    daily_stats[t]['ips'][ip_address] += 1  
    await save_to_github()

def admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Admin", headers={"WWW-Authenticate": "Basic"})
    return credentials.username

# ============ BACKGROUND TASKS ============
async def github_token_auto_updater():
    await asyncio.sleep(5) 
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(GITHUB_UPDATE_API, timeout=15) as resp: await resp.text()
        except: pass
        await asyncio.sleep(8 * 3600)

async def daily_auto_like_cron():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now > target_time: target_time += timedelta(days=1)
        await asyncio.sleep((target_time - now).total_seconds())
        await fetch_from_github()
        today = date.today()
        still_active = []
        for sub in subscriptions.get("active", []):
            exp_date = datetime.strptime(sub["expiry"], "%d-%m-%Y").date() if "-" in sub["expiry"] else today
            if today <= exp_date:
                uid = sub["uid"]
                for _ in range(10):
                    try:
                        url = f"{LIKE_API_URL}like?uid={uid}&region=IND&key={API_KEY}"
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url, timeout=10) as resp: await resp.json()
                    except: pass
                    await asyncio.sleep(1)
                still_active.append(sub)
        subscriptions["active"] = still_active
        await save_to_github()

@app.on_event("startup")
async def startup_event():
    await fetch_from_github()
    asyncio.create_task(daily_auto_like_cron())
    asyncio.create_task(github_token_auto_updater())

# ============ HTML UI INTERFACE ============
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
            font-family: 'Courier New', Courier, monospace; background-color: var(--bg-color); color: var(--text-main);
            margin: 0; padding: 10px; display: flex; justify-content: center; align-items: center; min-height: 100vh; position: relative; overflow-x: hidden;
        }}
        #matrixCanvas {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; opacity: 0.4; }}
        .container {{
            background: var(--card-bg); padding: 25px; border-radius: 12px;
            box-shadow: 0 0 40px rgba(0, 229, 255, 0.2), inset 0 0 20px rgba(255, 0, 119, 0.1);
            width: 100%; max-width: 500px; border: 2px solid transparent;
            background-image: linear-gradient(var(--card-bg), var(--card-bg)), linear-gradient(135deg, var(--primary), var(--secondary), var(--accent));
            background-origin: border-box; background-clip: padding-box, border-box; box-sizing: border-box; position: relative; backdrop-filter: blur(10px);
        }}
        .brand-header {{
            text-align: center; font-size: 32px; font-weight: 900; letter-spacing: 5px; margin-bottom: 5px;
            background: linear-gradient(90deg, #ff0077, #00e5ff, #00ffaa, #ffaa00, #ff0077); background-size: 400% 100%;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: flowColors 6s linear infinite; text-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        }}
        @keyframes flowColors {{ 0% {{ background-position: 0% 50%; }} 100% {{ background-position: 100% 50%; }} }}
        .top-action-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .menu-trigger-btn {{ background: transparent; color: var(--secondary); border: 1px solid var(--secondary); padding: 6px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 12px; }}
        .token-update-btn {{ background: transparent; color: #ffaa00; border: 1px solid #ffaa00; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; display: flex; align-items: center; gap: 5px; }}
        .links-menu-overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 999; backdrop-filter: blur(5px); }}
        .links-menu {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #090d16; border: 2px solid var(--accent); border-radius: 6px; width: 90%; max-width: 400px; padding: 20px; box-sizing: border-box; }}
        .menu-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid var(--accent); padding-bottom: 10px; }}
        .close-menu-btn {{ background: none; border: none; color: var(--text-main); font-size: 20px; cursor: pointer; }}
        .menu-link-item {{ background: #0d1527; color: var(--text-main); padding: 12px; border-radius: 4px; text-decoration: none; font-size: 13px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border: 1px solid var(--terminal-border); }}
        h1 {{ text-align: center; color: var(--secondary); font-size: 20px; margin: 5px 0; letter-spacing: 2px; }}
        .subtitle {{ text-align: center; color: #64748b; font-size: 11px; margin-bottom: 25px; }}
        .stats-box {{ background: rgba(13, 22, 43, 0.9); padding: 12px; border-radius: 4px; margin-bottom: 20px; display: flex; justify-content: space-between; font-size: 13px; border-left: 4px solid var(--primary); }}
        .input-group {{ margin-bottom: 18px; }}
        .input-group label {{ display: block; margin-bottom: 8px; font-size: 12px; color: var(--secondary); font-weight: bold; }}
        .input-group input, .input-group select {{ width: 100%; padding: 12px; border-radius: 4px; border: 1px solid var(--terminal-border); background: #040812; color: #fff; font-family: monospace; }}
        .btn-container {{ display: flex; gap: 12px; }}
        button {{ flex: 1; padding: 14px; color: #000; border: none; border-radius: 4px; font-weight: 900; cursor: pointer; text-transform: uppercase; display: flex; align-items: center; justify-content: center; gap: 8px; }}
        .btn-like {{ background: var(--primary); }}
        .btn-info {{ background: var(--secondary); }}
        .btn-token {{ background: var(--accent); color: white; }}
        .btn-auto-plan {{ background: linear-gradient(135deg, #ffaa00, #ff4400); color: white; margin-top: 15px; width: 100%; }}
        #result, #tokenResult, #autoResult {{ margin-top: 20px; display: none; }}
        .success-res {{ background: #022c16; border: 1px solid var(--primary); padding: 15px; border-radius: 4px; color: var(--primary); }}
        .error-res {{ background: #2d0606; border: 1px solid var(--alert-red); padding: 15px; border-radius: 4px; color: var(--alert-red); }}
        
        /* 🎨 PLAYER INFO & RAW DATA LAYOUT */
        .info-card {{ background: #050b18; border: 2px solid var(--secondary); border-radius: 8px; padding: 16px; box-shadow: 0 0 15px rgba(0, 229, 255, 0.2); margin-bottom: 15px; }}
        .info-header-title {{ text-align: center; color: var(--primary); font-size: 15px; font-weight: bold; border-bottom: 2px dashed var(--terminal-border); padding-bottom: 8px; margin-bottom: 12px; letter-spacing: 1px; }}
        .info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; }}
        .info-label {{ color: #8492a6; font-weight: bold; }}
        .info-value {{ color: #ffffff; font-weight: bold; }}
        .val-highlight {{ color: #ffaa00; }}
        .val-success {{ color: var(--primary); }}
        .val-heart {{ color: var(--accent); }}
        .info-sig-box {{ background: rgba(0, 255, 170, 0.05); padding: 12px; border-radius: 6px; border-left: 4px solid var(--accent); margin-top: 12px; font-style: italic; font-size: 12px; color: #cbd5e1; }}
        
        /* 💾 API RAW DATABASE BOX */
        .raw-data-box {{ background: #010204; border: 1px solid var(--terminal-border); border-radius: 6px; padding: 12px; max-height: 250px; overflow-y: auto; text-align: left; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }}
        .raw-data-box pre {{ margin: 0; white-space: pre-wrap; font-size: 11px; color: #00ff66; font-family: monospace; }}
        
        .sub-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 1001; backdrop-filter: blur(8px); justify-content: center; align-items: center; padding: 10px; box-sizing: border-box; }}
        .sub-modal-content {{ background: #090f1c; border: 2px solid #ffaa00; border-radius: 8px; width: 100%; max-width: 440px; padding: 20px; box-sizing: border-box; position: relative; }}
        .plan-cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 15px 0; }}
        .plan-card {{ border: 1px solid var(--terminal-border); background: #040812; padding: 12px; border-radius: 6px; text-align: center; cursor: pointer; }}
        .plan-card.selected {{ border-color: #ffaa00; background: rgba(255,170,0,0.1); }}
        .qr-area {{ text-align: center; margin: 15px 0; display: none; }}
        .qr-area img {{ border: 4px solid white; border-radius: 4px; }}
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
        <div class="menu-grid">{menu_buttons_html}</div>
    </div>
</div>

<div class="sub-modal" id="subModal">
    <div class="sub-modal-content">
        <button class="close-menu-btn" style="position:absolute; top:12px; right:15px;" onclick="toggleSubModal(false)"><i class="fa-solid fa-xmark"></i></button>
        <div class="brand-header" style="font-size: 20px; color: #ffaa00;">AUTO LIKE SYSTEM</div>
        <div class="plan-cards">
            <div class="plan-card" id="plan1" onclick="selectPlan(49, 20)">
                <h4 style="margin:0; color:#ffaa00;">₹ 49 PLAN</h4>
                <p style="margin:5px 0 0 0; font-size:12px;">20 दिन वैलिडिटी</p>
            </div>
            <div class="plan-card" id="plan2" onclick="selectPlan(79, 30)">
                <h4 style="margin:0; color:#ffaa00;">₹ 79 PLAN</h4>
                <p style="margin:5px 0 0 0; font-size:12px;">30 दिन वैलिडिटी</p>
            </div>
        </div>
        <div class="qr-area" id="qrArea">
            <img id="payQr" src="" width="160" height="160">
            <p style="font-size:11px; color:#ffffff; margin:6px 0;">UPI: <code style="color:#00e5ff;">{upi_id}</code></p>
            <div class="input-group" style="margin-top:12px; text-align:left;"><label>TARGET PLAYER UID</label><input type="text" id="subUid" placeholder="Enter UID..."></div>
            <div class="input-group" style="text-align:left;"><label>TRANSACTION ID / UTR</label><input type="text" id="subTxid" placeholder="Enter TXID..."></div>
            <button type="button" class="btn-like" style="background:#ffaa00; font-size:12px;" onclick="submitSubRequest()"><i class="fa-solid fa-paper-plane"></i> SUBMIT TO ADMIN</button>
        </div>
        <div id="autoResult"></div>
    </div>
</div>

<div class="container">
    <div class="top-action-bar">
        <button type="button" class="menu-trigger-btn" onclick="toggleMenu(true)"><i class="fa-solid fa-bars"></i> LINKS</button>
        <button type="button" class="token-update-btn" onclick="triggerManualTokenUpdate()"><i class="fa-solid fa-arrows-rotate"></i> TOKEN UPDATE</button>
    </div>

    <div class="brand-header">S.KANHAIYA</div>
    <h1>FF MULTI-EXTRACTOR</h1>
    <div class="subtitle">Secure GitHub Cloud Center</div>

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
            </select>
        </div>
        <div class="input-group">
            <label><i class="fa-solid fa-fingerprint"></i> TARGET PLAYER UID</label>
            <input type="text" name="uid" id="uid" placeholder="Enter target player UID...">
        </div>
        <div class="btn-container">
            <button type="button" class="btn-info" onclick="processAction('info')"><i class="fa-solid fa-shield-halved"></i> FETCH INFO</button>
            <button type="button" class="btn-like" onclick="processAction('like')"><i class="fa-solid fa-heart-pulse"></i> INJECT LIKE</button>
        </div>
    </form>
    
    <button type="button" class="btn-auto-plan" onclick="toggleSubModal(true)"><i class="fa-solid fa-bolt"></i> ACTIVATE AUTO-LIKE BOT</button>
    
    <div class="loader" id="loader">
        <i class="fa-solid fa-circle-notch fa-spin fa-2x"></i>
        <p style="margin:5px 0 0 0; font-size:12px;">EXTRACTING DATABASE NODES...</p>
    </div>
    <div id="result"></div>

    <div style="height:2px; background:var(--terminal-border); margin:30px 0;"></div>
    <div class="brand-header" style="font-size: 18px; color: var(--accent);">GUEST TOKEN CREATOR</div>
    <form id="tokenForm" style="margin-top: 15px;">
        <div class="input-group"><label><i class="fa-solid fa-user-secret"></i> GUEST ID</label><input type="text" id="tokenUid" placeholder="Enter guest UID..."></div>
        <div class="input-group"><label><i class="fa-solid fa-key"></i> PASSWORD</label><input type="password" id="tokenPassword" placeholder="Enter password..."></div>
        <button type="button" class="btn-token" onclick="generateGuestToken()"><i class="fa-solid fa-unlock-keyhole"></i> GENERATE TOKEN</button>
    </form>
    <div id="tokenResult"></div>
</div>

<script>
    let selectedAmount = 0, selectedDays = 0;
    const canvas = document.getElementById('matrixCanvas'); const ctx = canvas.getContext('2d');
    function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
    resizeCanvas(); window.addEventListener('resize', resizeCanvas);
    const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+-='.split(''); const fontSize = 15; const columns = canvas.width / fontSize;
    const rainDrops = []; for (let x = 0; x < columns; x++) {{ rainDrops[x] = Math.random() * -100; }}
    const colors = ['#00ffaa', '#00e5ff', '#ff0077'];
    function drawMatrix() {{
        ctx.fillStyle = 'rgba(2, 4, 10, 0.08)'; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.font = fontSize + 'px monospace';
        for (let i = 0; i < rainDrops.length; i++) {{
            const text = matrixChars[Math.floor(Math.random() * matrixChars.length)]; ctx.fillStyle = colors[i % colors.length];
            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
            if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) rainDrops[i] = 0; rainDrops[i]++;
        }}
    }}
    setInterval(drawMatrix, 30);

    function toggleMenu(show) {{ document.getElementById('menuOverlay').style.display = show ? 'block' : 'none'; }}
    function toggleSubModal(show) {{ document.getElementById('subModal').style.display = show ? 'flex' : 'none'; }}
    async function triggerManualTokenUpdate() {{ alert("रिक्वेस्ट भेज दी गई है..."); const r = await fetch('/api/manual-token-update', {{ method: 'POST' }}); const d = await r.json(); alert(d.message); }}

    function selectPlan(amount, days) {{
        selectedAmount = amount; selectedDays = days;
        document.getElementById('plan1').className = amount === 49 ? 'plan-card selected' : 'plan-card';
        document.getElementById('plan2').className = amount === 79 ? 'plan-card selected' : 'plan-card';
        const upiStr = "upi://pay?pa={upi_id}&pn=SKANHAIYA&am=" + amount + "&cu=INR&tn=AutoLike_" + days + "Days";
        document.getElementById('payQr').src = "https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=" + encodeURIComponent(upiStr);
        document.getElementById('qrArea').style.display = 'block';
    }}

    async function submitSubRequest() {{
        const uid = document.getElementById('subUid').value; const txid = document.getElementById('subTxid').value;
        if(!uid.trim() || !txid.trim()) {{ alert("डिटेल्स भरें!"); return; }}
        const f = new FormData(); f.append('uid', uid); f.append('txid', txid); f.append('amount', selectedAmount); f.append('days', selectedDays);
        const r = await fetch('/api/submit-subscription', {{ method: 'POST', body: f }}); const d = await r.json();
        const res = document.getElementById('autoResult'); res.style.display = 'block'; res.className = d.status === 'success' ? 'success-res' : 'error-res'; res.innerHTML = d.message;
    }}

    async function processAction(actionType) {{
        const region = document.getElementById('region').value; const uid = document.getElementById('uid').value;
        const loader = document.getElementById('loader'); const resultDiv = document.getElementById('result');
        if (!uid.trim()) {{ alert("UID डालना ज़रूरी है!"); return; }}
        resultDiv.style.display = 'none'; loader.style.display = 'block';
        const formData = new FormData(); formData.append('region', region); formData.append('uid', uid); formData.append('action', actionType);
        try {{
            const response = await fetch('/api/process', {{ method: 'POST', body: formData }});
            const data = await response.json(); loader.style.display = 'none'; resultDiv.style.display = 'block';
            if (data.status === 'success') {{
                if (actionType === 'like') {{
                    resultDiv.className = 'success-res';
                    resultDiv.innerHTML = "<h3>⚡ EXPLOIT INJECTED!</h3><b>PLAYER:</b> " + data.player + "<br><b>UID:</b> <code>" + data.uid + "</code><br><b>BOOSTED:</b> +" + data.given;
                }} else {{
                    resultDiv.removeAttribute('class');
                    resultDiv.innerHTML = data.html; // बैकएंड से रेंडर होकर आ रहा पूरा स्ट्रक्चर यहाँ इंजेक्ट होगा
                }}
            }} else {{ resultDiv.className = 'error-res'; resultDiv.innerHTML = "❌ " + data.message; }}
        }} catch (e) {{ loader.style.display = 'none'; resultDiv.style.display = 'block'; resultDiv.className = 'error-res'; resultDiv.innerHTML = "❌ SYSTEM TIMEOUT."; }}
    }}

    async function generateGuestToken() {{
        const uid = document.getElementById('tokenUid').value; const password = document.getElementById('tokenPassword').value;
        const res = document.getElementById('tokenResult'); if (!uid.trim() || !password.trim()) return;
        const f = new FormData(); f.append('uid', uid); f.append('password', password);
        const response = await fetch('/api/generate-token', {{ method: 'POST', body: f }}); const d = await response.json();
        res.style.display = 'block'; res.className = d.status === 'success' ? 'success-res' : 'error-res';
        if(d.status === 'success') res.innerHTML = "<h3>✅ GENERATED!</h3><div class='raw-data-box'><pre>" + JSON.stringify(d.payload, null, 4) + "</pre></div>";
        else res.innerHTML = "❌ " + d.message;
    }}
</script>
</body>
</html>
"""

ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head><meta charset="UTF-8"><title>⚡ ADMIN OVERRIDE ⚡</title><style>body{{font-family:monospace;background:#030712;color:#00ff66;padding:20px;}}table{{width:100%;border-collapse:collapse;margin-top:15px;background:#090f1c;}}th,td{{border:1px solid #1e293b;padding:12px;}}th{{background:#1e293b;color:#00e5ff;}}.btn{{padding:6px 12px;font-weight:bold;cursor:pointer;border:none;border-radius:4px;}}.btn-approve{{background:#00ff66;color:black;}}.btn-reject{{background:#ff3333;color:white;}}</style></head>
<body>
    <div style="text-align:center; border-bottom:2px solid #ffaa00; padding-bottom:10px;"><h1>S.KANHAIYA CONTROL PANEL</h1><a href="/" style="color:#00e5ff; text-decoration:none;">➔ BACK TO HOME</a></div>
    <h2>📥 PENDING ({pending_count})</h2>
    <table><tr><th>UID</th><th>TRANSACTION ID</th><th>PLAN</th><th>VALIDITY</th><th>ACTION</th></tr>{pending_rows}</table>
    <h2>✅ ACTIVE ({active_count})</h2>
    <table><tr><th>UID</th><th>PLAN TYPE</th><th>EXPIRY DATE</th></tr>{active_rows}</table>
</body>
</html>
"""

# ============ API ROUTES ============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    await fetch_from_github()
    client_ip = request.client.host or "127.0.0.1"
    t = today_str()
    used = user_limits.get(client_ip, {}).get('count', 0) if client_ip in user_limits and user_limits[client_ip]['date'] == t else 0
    remaining = daily_limit - used
    buttons_html = "".join([f'<a href="{i["url"]}" target="_blank" class="menu-link-item">{i["title"]} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:11px;"></i></a>' for i in MENU_LINKS])
    return HTML_TEMPLATE.format(bot_status=bot_status.upper(), remaining=remaining, daily_limit=daily_limit, menu_buttons_html=buttons_html, upi_id=UPI_ID)

@app.post("/api/manual-token-update")
async def manual_token_update():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_UPDATE_API, timeout=12) as resp:
                if resp.status == 200: return JSONResponse({"status": "success", "message": "टोकन सफलतापूर्वक रीफ्रेश हुआ!"})
    except: pass
    return JSONResponse({"status": "error", "message": "टाइमआउट!"})

@app.post("/api/submit-subscription")
async def submit_subscription(uid: str = Form(...), txid: str = Form(...), amount: int = Form(...), days: int = Form(...)):
    if not uid.isdigit() or not txid.strip(): return JSONResponse({"status": "error", "message": "गलत डिटेल्स!"})
    await fetch_from_github()
    for req in subscriptions["pending"]:
        if req["txid"] == txid: return JSONResponse({"status": "error", "message": "पहले से पेंडिंग है!"})
    subscriptions["pending"].append({"uid": uid, "txid": txid, "amount": amount, "days": days})
    await save_to_github()
    return JSONResponse({"status": "success", "message": "रिव्यू के लिए एडमिन पैनल में भेज दिया गया है!"})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(username: str = Depends(admin_auth)):
    await fetch_from_github()
    p_rows = "".join([f"<tr><td>{i['uid']}</td><td><code>{i['txid']}</code></td><td>₹{i['amount']}</td><td>{i['days']} दिन</td><td><a href='/admin/approve/{idx}'><button class='btn btn-approve'>APPROVE</button></a> <a href='/admin/reject/{idx}'><button class='btn btn-reject'>REJECT</button></a></td></tr>" for idx, i in enumerate(subscriptions["pending"])])
    if not p_rows: p_rows = "<tr><td colspan='5' style='text-align:center;'>कोई डेटा नहीं है</td></tr>"
    a_rows = "".join([f"<tr><td>{i['uid']}</td><td>₹{i['amount']} Plan ({i['days']} Days)</td><td>{i['expiry']}</td></tr>" for i in subscriptions["active"]])
    if not a_rows: a_rows = "<tr><td colspan='3' style='text-align:center;'>कोई एक्टिव बोट नहीं है</td></tr>"
    return ADMIN_HTML_TEMPLATE.format(pending_count=len(subscriptions["pending"]), active_count=len(subscriptions["active"]), pending_rows=p_rows, active_rows=a_rows)

@app.get("/admin/approve/{idx}")
async def approve_sub(idx: int, username: str = Depends(admin_auth)):
    await fetch_from_github()
    if 0 <= idx < len(subscriptions["pending"]):
        req = subscriptions["pending"].pop(idx)
        expiry_date = (date.today() + timedelta(days=int(req["days"]))).strftime("%d-%m-%Y")
        subscriptions["active"].append({"uid": req["uid"], "amount": req["amount"], "days": req["days"], "expiry": expiry_date})
        await save_to_github()
    return HTMLResponse("<script>alert('Approved!'); window.location.href='/admin';</script>")

@app.get("/admin/reject/{idx}")
async def reject_sub(idx: int, username: str = Depends(admin_auth)):
    await fetch_from_github()
    if 0 <= idx < len(subscriptions["pending"]): subscriptions["pending"].pop(idx); await save_to_github()
    return HTMLResponse("<script>alert('Rejected!'); window.location.href='/admin';</script>")

@app.post("/api/process")
async def process(request: Request, region: str = Form(...), uid: str = Form(...), action: str = Form(...)):
    if bot_status == "off": return JSONResponse({"status": "error", "message": "वेबसाइट मेंटेनेंस में है।"})
    client_ip = request.client.host or "127.0.0.1"
    region = region.lower()
    if not uid.isdigit(): return JSONResponse({"status": "error", "message": "गलत UID फॉर्मेट!"})

    if action == "info":
        url = f"{INFO_API_URL}?region={region}&uid={uid}"
        for _ in range(4):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=7) as resp:
                        if resp.status == 200:
                            raw = await resp.json()
                            
                            # 🧩 SAFE PARSING OF COMPLEX API RESPONSE STRUCT
                            basic = raw.get("BasicInfo") or raw.get("basicInfo") or {}
                            social = raw.get("socialInfo") or raw.get("SocialInfo") or {}
                            profile = raw.get("profileInfo") or raw.get("ProfileInfo") or {}

                            nickname = basic.get("nickname", "Unknown")
                            level = basic.get("level", "N/A")
                            likes = basic.get("liked", 0)
                            region_name = basic.get("region", region.upper())
                            signature = social.get("signature", "No Signature Inside")
                            req_likes = basic.get("likesRequired", "N/A")
                            avatar = profile.get("avatarId") or basic.get("avatarId", "Default")
                            banner = profile.get("bannerId") or basic.get("bannerId", "Default")

                            # 🎨 RAW JSON FORMATTING FOR RE-VISUALIZATION
                            raw_json_string = json.dumps(raw, indent=4, ensure_ascii=False)

                            # 🎨 HIGH-QUALITY V1 TERMINAL STYLE + RAW JSON RESPONSE AT THE BOTTOM
                            html_ui = f"""
                            <div class="info-card">
                                <div class="info-header-title"><i class="fa-solid fa-terminal"></i> PLAYER CORE REGISTRY</div>
                                <div class="info-row"><span class="info-label">TARGET UID:</span><span class="info-value val-highlight">{uid}</span></div>
                                <div class="info-row"><span class="info-label">NICKNAME:</span><span class="info-value val-success">{nickname}</span></div>
                                <div class="info-row"><span class="info-label">LEVEL TIER:</span><span class="info-value val-highlight">Lv {level}</span></div>
                                <div class="info-row"><span class="info-label">TOTAL LIKES:</span><span class="info-value val-heart"><i class="fa-solid fa-heart"></i> {likes}</span></div>
                                <div class="info-row"><span class="info-label">REQUIRED LIKES:</span><span class="info-value">{req_likes}</span></div>
                                <div class="info-row"><span class="info-label">REGION NODE:</span><span class="info-value">{region_name}</span></div>
                                <div class="info-row"><span class="info-label">AVATAR ASSET:</span><span class="info-value">{avatar}</span></div>
                                <div class="info-row"><span class="info-label">BANNER ASSET:</span><span class="info-value">{banner}</span></div>
                                <div class="info-header-title" style="margin-top:10px; font-size:12px; color:var(--accent);">SIGNATURE DATA</div>
                                <div class="info-sig-box">{signature}</div>
                            </div>
                            
                            <div class="brand-header" style="font-size: 14px; text-align: left; margin: 15px 0 5px 2px; color: #00ff66;">📦 API RAW DATABASE RESPONSE:</div>
                            <div class="raw-data-box">
                                <pre>{raw_json_string}</pre>
                            </div>
                            """
                            return JSONResponse({"status": "success", "html": html_ui})
            except: pass
            await asyncio.sleep(0.1)
        return JSONResponse({"status": "error", "message": "प्लेयर इन्फो API से डेटा नहीं मिला।"})

    elif action == "like":
        if not await can_user_like(client_ip): return JSONResponse({"status": "error", "message": "आपकी आज की लाइक लिमिट पूरी हो चुकी है!"})
        url = f"{LIKE_API_URL}like?uid={uid}&region={region.upper()}&key={API_KEY}"
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=8) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('status') == 1:
                                await update_user_like(client_ip)
                                return JSONResponse({"status": "success", "player": data.get('PlayerNickname', 'Unknown'), "uid": data.get('UID', uid), "given": data.get('LikesGivenByAPI', 0)})
                            elif data.get('status') == 2:
                                return JSONResponse({"status": "error", "message": "इस UID की आज की लिमिट खत्म हो गई है।"})
            except: pass
            await asyncio.sleep(0.1)
        return JSONResponse({"status": "error", "message": "लाइक एपीआई डाउन है!"})

@app.post("/api/generate-token")
async def generate_token(uid: str = Form(...), password: str = Form(...)):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TOKEN_API_URL}?uid={uid}&password={password}", timeout=8) as resp:
                if resp.status == 200: return JSONResponse({"status": "success", "payload": await resp.json()})
    except: pass
    return JSONResponse({"status": "error", "message": "टोकन सर्वर डाउन है!"})
