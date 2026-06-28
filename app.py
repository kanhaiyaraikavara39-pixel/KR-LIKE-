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

# 🐙 GITHUB DATABASE CONFIGURATION
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

# ============ 🎨 UPGRADED HACKER-STYLE HTML UI ============
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ KANHAIYA TERMINAL v3.0 ⚡</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        /* ===== CYBERPUNK ROOT ===== */
        :root {
            --bg-deep: #07090e;
            --bg-card: rgba(12, 18, 34, 0.82);
            --border-glow: #00ffaa;
            --text-main: #e2e8f0;
            --text-dim: #7a8aa4;
            --cyan: #00f0ff;
            --green: #00ff88;
            --pink: #ff2d75;
            --gold: #ffb800;
            --glow: 0 0 40px rgba(0, 255, 170, 0.08);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: var(--bg-deep);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            background-image: radial-gradient(circle at 20% 30%, rgba(0, 255, 170, 0.02) 0%, transparent 60%),
                              radial-gradient(circle at 80% 70%, rgba(255, 0, 113, 0.02) 0%, transparent 60%);
            position: relative;
        }
        #matrixCanvas {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: 0;
            opacity: 0.10;
            pointer-events: none;
        }
        .container {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 520px;
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 28px 22px;
            border-radius: 20px;
            border: 1px solid rgba(0, 255, 170, 0.12);
            box-shadow: var(--glow), inset 0 0 60px rgba(0, 255, 170, 0.02);
            transition: 0.3s;
        }
        .container:hover {
            border-color: rgba(0, 255, 170, 0.25);
            box-shadow: 0 0 60px rgba(0, 255, 170, 0.05), inset 0 0 60px rgba(0, 255, 170, 0.03);
        }

        /* ===== TOP BAR ===== */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(0, 255, 170, 0.08);
        }
        .top-bar .brand {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            background: linear-gradient(135deg, var(--cyan), var(--green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .top-bar .badge {
            font-size: 9px;
            padding: 4px 12px;
            border-radius: 30px;
            background: rgba(0, 255, 170, 0.08);
            border: 1px solid rgba(0, 255, 170, 0.20);
            color: var(--green);
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .badge i { margin-right: 4px; }

        /* ===== GLITCH TITLE ===== */
        .glitch {
            text-align: center;
            font-size: 28px;
            font-weight: 900;
            letter-spacing: 6px;
            text-transform: uppercase;
            color: #fff;
            text-shadow: 0 0 20px rgba(0, 255, 170, 0.15);
            margin-bottom: 0px;
            position: relative;
            display: inline-block;
            width: 100%;
        }
        .glitch::before, .glitch::after {
            content: attr(data-text);
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            opacity: 0.6;
            pointer-events: none;
        }
        .glitch::before {
            color: var(--pink);
            transform: translate(-2px, -1px);
            animation: g1 4s infinite;
        }
        .glitch::after {
            color: var(--cyan);
            transform: translate(2px, 1px);
            animation: g2 4s infinite;
        }
        @keyframes g1 {
            0%, 90%, 100% { transform: translate(-2px, -1px); opacity: 0.5; }
            92% { transform: translate(4px, -2px); opacity: 0.1; }
            94% { transform: translate(-4px, 2px); opacity: 0.8; }
        }
        @keyframes g2 {
            0%, 90%, 100% { transform: translate(2px, 1px); opacity: 0.5; }
            92% { transform: translate(-3px, 3px); opacity: 0.2; }
            94% { transform: translate(3px, -2px); opacity: 0.7; }
        }
        .sub-glow {
            text-align: center;
            font-size: 11px;
            color: var(--text-dim);
            letter-spacing: 4px;
            margin-top: -2px;
            margin-bottom: 22px;
            border-bottom: 1px dashed rgba(148, 163, 184, 0.08);
            padding-bottom: 14px;
        }
        .sub-glow i { color: var(--cyan); margin: 0 4px; }

        /* ===== STATS BAR ===== */
        .stats {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 6px;
            background: rgba(0,0,0,0.30);
            border-radius: 14px;
            padding: 12px 6px;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.02);
        }
        .stat {
            text-align: center;
        }
        .stat .lbl {
            font-size: 8px;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 1.5px;
        }
        .stat .val {
            font-size: 18px;
            font-weight: 700;
            color: var(--green);
            text-shadow: 0 0 20px rgba(0, 255, 170, 0.10);
        }
        .stat .val.gold { color: var(--gold); }

        /* ===== FORM ===== */
        .input-group {
            margin-bottom: 16px;
        }
        .input-group label {
            display: block;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--text-dim);
            margin-bottom: 5px;
        }
        .input-group label i { margin-right: 6px; color: var(--cyan); }
        .input-group select, .input-group input {
            width: 100%;
            padding: 12px 14px;
            background: rgba(0,0,0,0.40);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            color: #fff;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            transition: 0.25s;
            outline: none;
        }
        .input-group select:focus, .input-group input:focus {
            border-color: var(--cyan);
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.05);
            background: rgba(0,0,0,0.55);
        }

        /* ===== BUTTONS ===== */
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 4px;
        }
        .btn {
            flex: 1;
            padding: 13px 8px;
            border: none;
            border-radius: 12px;
            font-family: 'Courier New', monospace;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: 0.25s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #000;
        }
        .btn i { font-size: 14px; }
        .btn-like { background: var(--green); color: #000; box-shadow: 0 0 30px rgba(0, 255, 136, 0.15); }
        .btn-like:hover { transform: scale(1.02); box-shadow: 0 0 50px rgba(0, 255, 136, 0.25); }
        .btn-info { background: var(--cyan); color: #000; box-shadow: 0 0 30px rgba(0, 240, 255, 0.10); }
        .btn-info:hover { transform: scale(1.02); box-shadow: 0 0 50px rgba(0, 240, 255, 0.20); }
        .btn-token { background: var(--pink); color: #fff; box-shadow: 0 0 30px rgba(255, 45, 117, 0.10); }
        .btn-token:hover { transform: scale(1.02); box-shadow: 0 0 50px rgba(255, 45, 117, 0.20); }
        .btn-auto { background: linear-gradient(135deg, var(--gold), #ff6a00); color: #000; width: 100%; margin-top: 16px; padding: 14px; border-radius: 12px; border: none; font-weight: 700; font-size: 13px; cursor: pointer; transition: 0.25s; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .btn-auto:hover { transform: scale(1.02); box-shadow: 0 0 50px rgba(255, 184, 0, 0.20); }

        /* ===== RESULT BOX ===== */
        #result, #tokenResult, #autoResult {
            margin-top: 18px;
            display: none;
        }
        .success-res {
            background: rgba(0, 255, 136, 0.06);
            border: 1px solid var(--green);
            padding: 16px;
            border-radius: 12px;
            color: var(--green);
            font-size: 13px;
        }
        .error-res {
            background: rgba(255, 45, 117, 0.06);
            border: 1px solid var(--pink);
            padding: 16px;
            border-radius: 12px;
            color: var(--pink);
            font-size: 13px;
        }

        /* ===== INFO CARD ===== */
        .info-card {
            background: rgba(0,0,0,0.30);
            border: 1px solid rgba(0, 255, 170, 0.10);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 14px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            font-size: 12px;
        }
        .info-row .lbl { color: var(--text-dim); }
        .info-row .val { color: #fff; font-weight: 600; }
        .val-heart { color: var(--pink); }
        .val-highlight { color: var(--gold); }
        .val-success { color: var(--green); }
        .raw-box {
            background: rgba(0,0,0,0.50);
            border-radius: 10px;
            padding: 12px;
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.03);
        }
        .raw-box pre {
            margin: 0;
            font-size: 10px;
            color: var(--green);
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-all;
        }

        /* ===== MENU / MODAL ===== */
        .menu-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.88);
            backdrop-filter: blur(8px);
            z-index: 999;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .menu-box {
            background: #0c1222;
            border: 1px solid var(--cyan);
            border-radius: 16px;
            padding: 24px;
            max-width: 420px;
            width: 100%;
        }
        .menu-box .head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.10);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }
        .menu-box .head h2 { font-size: 16px; color: var(--cyan); letter-spacing: 2px; }
        .close-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
        .menu-link {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 14px;
            background: rgba(255,255,255,0.02);
            border-radius: 10px;
            margin-bottom: 8px;
            text-decoration: none;
            color: var(--text-main);
            font-size: 13px;
            border: 1px solid transparent;
            transition: 0.2s;
        }
        .menu-link:hover { border-color: rgba(0, 255, 170, 0.15); background: rgba(0, 255, 170, 0.03); }
        .menu-link i { color: var(--text-dim); }

        /* ===== SUB MODAL ===== */
        .sub-modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.92);
            backdrop-filter: blur(10px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .sub-box {
            background: #0c1222;
            border: 1px solid var(--gold);
            border-radius: 16px;
            padding: 24px;
            max-width: 440px;
            width: 100%;
            position: relative;
        }
        .plan-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin: 16px 0;
        }
        .plan-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
            cursor: pointer;
            transition: 0.25s;
        }
        .plan-card:hover { border-color: rgba(255, 184, 0, 0.30); }
        .plan-card.selected { border-color: var(--gold); background: rgba(255, 184, 0, 0.06); }
        .plan-card h4 { color: var(--gold); font-size: 16px; }
        .plan-card p { font-size: 11px; color: var(--text-dim); margin-top: 4px; }
        .qr-area { text-align: center; margin: 14px 0; display: none; }
        .qr-area img { border-radius: 8px; border: 2px solid rgba(255,255,255,0.05); }
        .qr-area code { color: var(--cyan); }
        .loader { display: none; text-align: center; margin-top: 14px; color: var(--cyan); }
        @media (max-width: 480px) {
            .container { padding: 18px 14px; }
            .glitch { font-size: 22px; letter-spacing: 4px; }
            .stats { grid-template-columns: 1fr 1fr 1fr; gap: 4px; }
            .stat .val { font-size: 15px; }
            .btn-group { flex-direction: column; }
            .btn { padding: 14px; }
        }
    </style>
</head>
<body>

<canvas id="matrixCanvas"></canvas>

<!-- ===== MENU OVERLAY ===== -->
<div class="menu-overlay" id="menuOverlay" onclick="toggleMenu(false)">
    <div class="menu-box" onclick="event.stopPropagation()">
        <div class="head">
            <h2><i class="fas fa-code-branch"></i> NAVIGATE</h2>
            <button class="close-btn" onclick="toggleMenu(false)"><i class="fas fa-xmark"></i></button>
        </div>
        {menu_buttons_html}
    </div>
</div>

<!-- ===== SUBSCRIPTION MODAL ===== -->
<div class="sub-modal" id="subModal">
    <div class="sub-box">
        <button class="close-btn" style="position:absolute; top:12px; right:16px;" onclick="toggleSubModal(false)"><i class="fas fa-xmark"></i></button>
        <div class="glitch" data-text="AUTO-BOT" style="font-size:22px; letter-spacing:3px;">AUTO-BOT</div>
        <div class="plan-grid">
            <div class="plan-card" id="plan1" onclick="selectPlan(49,20)"><h4>₹49</h4><p>20 Days</p></div>
            <div class="plan-card" id="plan2" onclick="selectPlan(79,30)"><h4>₹79</h4><p>30 Days</p></div>
        </div>
        <div class="qr-area" id="qrArea">
            <img id="payQr" src="" width="140" height="140">
            <p style="font-size:11px; color:var(--text-dim); margin:6px 0;">UPI: <code style="color:var(--cyan);">{upi_id}</code></p>
            <div class="input-group"><label>TARGET UID</label><input type="text" id="subUid" placeholder="Enter UID..."></div>
            <div class="input-group"><label>TRANSACTION ID</label><input type="text" id="subTxid" placeholder="Enter TXID..."></div>
            <button class="btn-like" style="width:100%; padding:14px; margin-top:4px;" onclick="submitSubRequest()"><i class="fas fa-paper-plane"></i> SUBMIT</button>
        </div>
        <div id="autoResult"></div>
    </div>
</div>

<!-- ===== MAIN CONTAINER ===== -->
<div class="container">
    <div class="top-bar">
        <span class="brand"><i class="fas fa-terminal"></i> S.KANHAIYA</span>
        <span class="badge"><i class="fas fa-circle" style="color:var(--green);"></i> {bot_status}</span>
    </div>

    <div class="glitch" data-text="FF EXTRACTOR">FF EXTRACTOR</div>
    <div class="sub-glow"><i class="fas fa-shield-halved"></i> CLOUD ENGINE v3.0 <i class="fas fa-shield-halved"></i></div>

    <div class="stats">
        <div class="stat"><div class="lbl">STATUS</div><div class="val">{bot_status}</div></div>
        <div class="stat"><div class="lbl">TODAY</div><div class="val">{remaining}</div></div>
        <div class="stat"><div class="lbl">LIMIT</div><div class="val gold">{daily_limit}</div></div>
    </div>

    <form id="toolForm">
        <div class="input-group">
            <label><i class="fas fa-globe"></i> REGION</label>
            <select name="region" id="region">
                <option value="IND">🇮🇳 India</option>
                <option value="BD">🇧🇩 Bangladesh</option>
                <option value="PK">🇵🇰 Pakistan</option>
            </select>
        </div>
        <div class="input-group">
            <label><i class="fas fa-fingerprint"></i> TARGET UID</label>
            <input type="text" name="uid" id="uid" placeholder="Enter player UID...">
        </div>
        <div class="btn-group">
            <button type="button" class="btn btn-info" onclick="processAction('info')"><i class="fas fa-shield-halved"></i> INFO</button>
            <button type="button" class="btn btn-like" onclick="processAction('like')"><i class="fas fa-heart"></i> LIKE</button>
        </div>
    </form>

    <button type="button" class="btn-auto" onclick="toggleSubModal(true)"><i class="fas fa-bolt"></i> ACTIVATE AUTO-BOT</button>

    <div class="loader" id="loader"><i class="fas fa-circle-notch fa-spin fa-2x"></i><p style="margin-top:6px;font-size:11px;">PROCESSING...</p></div>
    <div id="result"></div>

    <div style="height:1px; background:rgba(255,255,255,0.04); margin:32px 0 22px;"></div>

    <div class="glitch" data-text="TOKEN GEN" style="font-size:16px; letter-spacing:3px;">TOKEN GEN</div>
    <form id="tokenForm" style="margin-top:14px;">
        <div class="input-group"><label><i class="fas fa-user-secret"></i> GUEST ID</label><input type="text" id="tokenUid" placeholder="Enter guest UID..."></div>
        <div class="input-group"><label><i class="fas fa-key"></i> PASSWORD</label><input type="password" id="tokenPassword" placeholder="Enter password..."></div>
        <button type="button" class="btn btn-token" style="width:100%;" onclick="generateGuestToken()"><i class="fas fa-unlock-keyhole"></i> GENERATE</button>
    </form>
    <div id="tokenResult"></div>
</div>

<script>
    // ===== MATRIX RAIN =====
    const canvas = document.getElementById('matrixCanvas');
    const ctx = canvas.getContext('2d');
    function resizeCanvas() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    resizeCanvas(); window.addEventListener('resize', resizeCanvas);
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+-='.split('');
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = [];
    for (let i = 0; i < columns; i++) drops[i] = Math.random() * -100;
    const colors = ['#00ffaa', '#00f0ff', '#ff2d75'];
    function drawMatrix() {
        ctx.fillStyle = 'rgba(7, 9, 14, 0.06)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.font = fontSize + 'px monospace';
        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        }
    }
    setInterval(drawMatrix, 35);

    // ===== UI HELPERS =====
    function toggleMenu(show) { document.getElementById('menuOverlay').style.display = show ? 'flex' : 'none'; }
    function toggleSubModal(show) { document.getElementById('subModal').style.display = show ? 'flex' : 'none'; }

    let selectedAmount = 0, selectedDays = 0;
    function selectPlan(amount, days) {
        selectedAmount = amount; selectedDays = days;
        document.getElementById('plan1').className = amount === 49 ? 'plan-card selected' : 'plan-card';
        document.getElementById('plan2').className = amount === 79 ? 'plan-card selected' : 'plan-card';
        const upi = "upi://pay?pa={upi_id}&pn=SKANHAIYA&am=" + amount + "&cu=INR&tn=AutoLike_" + days + "Days";
        document.getElementById('payQr').src = "https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=" + encodeURIComponent(upi);
        document.getElementById('qrArea').style.display = 'block';
    }

    async function submitSubRequest() {
        const uid = document.getElementById('subUid').value;
        const txid = document.getElementById('subTxid').value;
        if (!uid.trim() || !txid.trim()) { alert("Please fill all fields!"); return; }
        const fd = new FormData();
        fd.append('uid', uid); fd.append('txid', txid); fd.append('amount', selectedAmount); fd.append('days', selectedDays);
        const res = await fetch('/api/submit-subscription', { method: 'POST', body: fd });
        const data = await res.json();
        const box = document.getElementById('autoResult');
        box.style.display = 'block';
        box.className = data.status === 'success' ? 'success-res' : 'error-res';
        box.innerHTML = data.message;
    }

    async function processAction(actionType) {
        const region = document.getElementById('region').value;
        const uid = document.getElementById('uid').value;
        if (!uid.trim()) { alert("Enter UID first!"); return; }
        const loader = document.getElementById('loader');
        const resultDiv = document.getElementById('result');
        resultDiv.style.display = 'none';
        loader.style.display = 'block';
        const fd = new FormData();
        fd.append('region', region); fd.append('uid', uid); fd.append('action', actionType);
        try {
            const response = await fetch('/api/process', { method: 'POST', body: fd });
            const data = await response.json();
            loader.style.display = 'none';
            resultDiv.style.display = 'block';
            if (data.status === 'success') {
                if (actionType === 'like') {
                    resultDiv.className = 'success-res';
                    resultDiv.innerHTML = `<i class="fas fa-bolt"></i> <strong>INJECTED!</strong><br>Player: ${data.player}<br>UID: <code>${data.uid}</code><br>Boost: +${data.given}`;
                } else {
                    resultDiv.removeAttribute('class');
                    resultDiv.innerHTML = data.html;
                }
            } else {
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = `<i class="fas fa-skull"></i> ${data.message}`;
            }
        } catch (e) {
            loader.style.display = 'none';
            resultDiv.style.display = 'block';
            resultDiv.className = 'error-res';
            resultDiv.innerHTML = '<i class="fas fa-skull"></i> SYSTEM TIMEOUT';
        }
    }

    async function generateGuestToken() {
        const uid = document.getElementById('tokenUid').value;
        const pass = document.getElementById('tokenPassword').value;
        const res = document.getElementById('tokenResult');
        if (!uid.trim() || !pass.trim()) { alert("Fill both fields!"); return; }
        const fd = new FormData();
        fd.append('uid', uid); fd.append('password', pass);
        const response = await fetch('/api/generate-token', { method: 'POST', body: fd });
        const data = await response.json();
        res.style.display = 'block';
        res.className = data.status === 'success' ? 'success-res' : 'error-res';
        if (data.status === 'success') {
            res.innerHTML = `<i class="fas fa-check-circle"></i> <strong>TOKEN GENERATED</strong><div class="raw-box"><pre>${JSON.stringify(data.payload, null, 4)}</pre></div>`;
        } else {
            res.innerHTML = `<i class="fas fa-skull"></i> ${data.message}`;
        }
    }

    // ===== MANUAL TOKEN UPDATE =====
    async function triggerManualTokenUpdate() {
        const r = await fetch('/api/manual-token-update', { method: 'POST' });
        const d = await r.json();
        alert(d.message);
    }
</script>
</body>
</html>
"""

# ============ ADMIN HTML (SAME AS BEFORE) ============
ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head><meta charset="UTF-8"><title>⚡ ADMIN PANEL ⚡</title><style>
body{font-family:monospace;background:#07090e;color:#00ff66;padding:20px;}
table{width:100%;border-collapse:collapse;margin-top:15px;background:#0c1222;}
th,td{border:1px solid #1e293b;padding:12px;}
th{background:#1e293b;color:#00e5ff;}
.btn{padding:6px 14px;font-weight:bold;cursor:pointer;border:none;border-radius:6px;}
.btn-approve{background:#00ff66;color:black;}
.btn-reject{background:#ff3333;color:white;}
</style></head>
<body>
<div style="text-align:center; border-bottom:2px solid #ffb800; padding-bottom:10px;"><h1>S.KANHAIYA CONTROL</h1><a href="/" style="color:#00e5ff; text-decoration:none;">➔ BACK</a></div>
<h2>📥 PENDING ({pending_count})</h2>
<table><tr><th>UID</th><th>TXID</th><th>PLAN</th><th>VALIDITY</th><th>ACTION</th></tr>{pending_rows}</table>
<h2>✅ ACTIVE ({active_count})</h2>
<table><tr><th>UID</th><th>PLAN</th><th>EXPIRY</th></tr>{active_rows}</table>
</body>
</html>
"""

# ============ API ROUTES (UNCHANGED) ============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    await fetch_from_github()
    client_ip = request.client.host or "127.0.0.1"
    t = today_str()
    used = user_limits.get(client_ip, {}).get('count', 0) if client_ip in user_limits and user_limits[client_ip]['date'] == t else 0
    remaining = daily_limit - used
    buttons_html = "".join([f'<a href="{i["url"]}" target="_blank" class="menu-link">{i["title"]} <i class="fas fa-arrow-up-right-from-square" style="font-size:10px;"></i></a>' for i in MENU_LINKS])
    return HTML_TEMPLATE.format(bot_status=bot_status.upper(), remaining=remaining, daily_limit=daily_limit, menu_buttons_html=buttons_html, upi_id=UPI_ID)

@app.post("/api/manual-token-update")
async def manual_token_update():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_UPDATE_API, timeout=12) as resp:
                if resp.status == 200: return JSONResponse({"status": "success", "message": "Token refreshed successfully!"})
    except: pass
    return JSONResponse({"status": "error", "message": "Timeout!"})

@app.post("/api/submit-subscription")
async def submit_subscription(uid: str = Form(...), txid: str = Form(...), amount: int = Form(...), days: int = Form(...)):
    if not uid.isdigit() or not txid.strip(): return JSONResponse({"status": "error", "message": "Invalid details!"})
    await fetch_from_github()
    for req in subscriptions["pending"]:
        if req["txid"] == txid: return JSONResponse({"status": "error", "message": "Already pending!"})
    subscriptions["pending"].append({"uid": uid, "txid": txid, "amount": amount, "days": days})
    await save_to_github()
    return JSONResponse({"status": "success", "message": "Submitted for admin review!"})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(username: str = Depends(admin_auth)):
    await fetch_from_github()
    p_rows = "".join([f"<tr><td>{i['uid']}</td><td><code>{i['txid']}</code></td><td>₹{i['amount']}</td><td>{i['days']} days</td><td><a href='/admin/approve/{idx}'><button class='btn btn-approve'>APPROVE</button></a> <a href='/admin/reject/{idx}'><button class='btn btn-reject'>REJECT</button></a></td></tr>" for idx, i in enumerate(subscriptions["pending"])])
    if not p_rows: p_rows = "<tr><td colspan='5' style='text-align:center;'>No pending requests</td></tr>"
    a_rows = "".join([f"<tr><td>{i['uid']}</td><td>₹{i['amount']} ({i['days']} Days)</td><td>{i['expiry']}</td></tr>" for i in subscriptions["active"]])
    if not a_rows: a_rows = "<tr><td colspan='3' style='text-align:center;'>No active bots</td></tr>"
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
    if bot_status == "off": return JSONResponse({"status": "error", "message": "Website is under maintenance."})
    client_ip = request.client.host or "127.0.0.1"
    region = region.lower()
    if not uid.isdigit(): return JSONResponse({"status": "error", "message": "Invalid UID format!"})

    if action == "info":
        url = f"{INFO_API_URL}?region={region}&uid={uid}"
        for _ in range(4):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=7) as resp:
                        if resp.status == 200:
                            raw = await resp.json()
                            basic = raw.get("BasicInfo") or raw.get("basicInfo") or {}
                            social = raw.get("socialInfo") or raw.get("SocialInfo") or {}
                            profile = raw.get("profileInfo") or raw.get("ProfileInfo") or {}
                            nickname = basic.get("nickname", "Unknown")
                            level = basic.get("level", "N/A")
                            likes = basic.get("liked", 0)
                            region_name = basic.get("region", region.upper())
                            signature = social.get("signature", "No Signature")
                            req_likes = basic.get("likesRequired", "N/A")
                            avatar = profile.get("avatarId") or basic.get("avatarId", "Default")
                            banner = profile.get("bannerId") or basic.get("bannerId", "Default")
                            raw_json_string = json.dumps(raw, indent=4, ensure_ascii=False)
                            html_ui = f"""
                            <div class="info-card">
                                <div class="info-row"><span class="lbl">UID</span><span class="val val-highlight">{uid}</span></div>
                                <div class="info-row"><span class="lbl">NICKNAME</span><span class="val val-success">{nickname}</span></div>
                                <div class="info-row"><span class="lbl">LEVEL</span><span class="val val-highlight">Lv {level}</span></div>
                                <div class="info-row"><span class="lbl">LIKES</span><span class="val val-heart"><i class="fas fa-heart"></i> {likes}</span></div>
                                <div class="info-row"><span class="lbl">REQUIRED</span><span class="val">{req_likes}</span></div>
                                <div class="info-row"><span class="lbl">REGION</span><span class="val">{region_name}</span></div>
                                <div class="info-row"><span class="lbl">AVATAR</span><span class="val">{avatar}</span></div>
                                <div class="info-row"><span class="lbl">BANNER</span><span class="val">{banner}</span></div>
                                <div style="margin-top:8px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.03); font-size:11px; color:var(--text-dim);"><i class="fas fa-quote-left"></i> {signature}</div>
                            </div>
                            <div class="raw-box"><pre>{raw_json_string}</pre></div>
                            """
                            return JSONResponse({"status": "success", "html": html_ui})
            except: pass
            await asyncio.sleep(0.1)
        return JSONResponse({"status": "error", "message": "Player info API timeout."})

    elif action == "like":
        if not await can_user_like(client_ip): return JSONResponse({"status": "error", "message": "Daily like limit reached!"})
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
                                return JSONResponse({"status": "error", "message": "This UID's daily limit is over."})
            except: pass
            await asyncio.sleep(0.1)
        return JSONResponse({"status": "error", "message": "Like API down!"})

@app.post("/api/generate-token")
async def generate_token(uid: str = Form(...), password: str = Form(...)):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{TOKEN_API_URL}?uid={uid}&password={password}", timeout=8) as resp:
                if resp.status == 200: return JSONResponse({"status": "success", "payload": await resp.json()})
    except: pass
    return JSONResponse({"status": "error", "message": "Token server down!"})