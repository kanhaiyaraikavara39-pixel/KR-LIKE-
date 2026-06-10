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
    'config': '/tmp/bot_config.json',
    'menu': '/tmp/menu_links.json'  # डाउनलोड लिंक्स के लिए नई फ़ाइल
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
        
    # डिफ़ॉल्ट लिंक्स फ़ाइल बनाना अगर वह मौजूद न हो
    if not os.path.exists(DATA_FILES['menu']):
        default_links = [
            {"title": "File Download 1", "url": "https://example.com/file1"},
            {"title": "File Download 2", "url": "https://example.com/file2"},
            {"title": "File Download 3", "url": "https://example.com/file3"},
            {"title": "File Download 4", "url": "https://example.com/file4"},
            {"title": "File Download 5", "url": "https://example.com/file5"},
            {"title": "File Download 6", "url": "https://example.com/file6"},
            {"title": "File Download 7", "url": "https://example.com/file7"},
            {"title": "File Download 8", "url": "https://example.com/file8"},
            {"title": "File Download 9", "url": "https://example.com/file9"},
            {"title": "File Download 10", "url": "https://example.com/file10"}
        ]
        try:
            with open(DATA_FILES['menu'], 'w') as f:
                json.dump(default_links, f, indent=2)
        except:
            pass

def load_menu_links():
    try:
        with open(DATA_FILES['menu'], 'r') as f:
            return json.load(f)
    except:
        return []

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
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            position: relative;
        }}
        .container {{
            background: var(--card-bg);
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 500px;
            border: 1px solid #334155;
            box-sizing: border-box;
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
        .btn-like {{ background: var(--primary); }}
        .btn-like:hover {{ background: var(--primary-hover); }}
        .btn-info {{ background: var(--secondary); }}
        .btn-info:hover {{ background: var(--secondary-hover); }}
        
        #result {{
            margin-top: 20px;
            display: none;
            font-size: 14px;
            line-height: 1.6;
        }}
        .success-res {{ background: #065f46; border: 1px solid #059669; padding: 15px; border-radius: 8px; }}
        .error-res {{ background: #991b1b; border: 1px solid #dc2626; padding: 15px; border-radius: 8px; }}
        
        /* प्रोफाइल कार्ड डिजाइन */
        .info-card {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 15px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
        }}
        .section-title {{
            color: #67e8f9;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 15px 0 8px 0;
            padding-bottom: 4px;
            border-bottom: 1px dashed #334155;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .section-title:first-of-type {{ margin-top: 0; }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.02);
        }}
        .info-label {{ color: #94a3b8; font-size: 13px; }}
        .info-value {{ color: #f8fafc; font-weight: 600; font-size: 13.5px; }}
        
        .val-highlight {{ color: #f59e0b; font-weight: bold; }}
        .val-success {{ color: #4ade80; }}
        .val-heart {{ color: #ec4899; }}
        
        .info-sig {{
            background: rgba(255,255,255,0.03);
            padding: 10px;
            border-radius: 6px;
            margin-top: 5px;
            border-left: 3px solid var(--secondary);
            font-style: italic;
            color: #cbd5e1;
            font-size: 13px;
            word-break: break-all;
        }}

        /* रॉ डेटा रिस्पॉन्स बॉक्स डिजाइन */
        .raw-data-box {{
            background: #090d16;
            border: 1px solid #1e293b;
            border-radius: 8px;
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
            font-size: 12px;
            color: #38bdf8;
        }}

        .loader {{ display: none; text-align: center; margin-top: 15px; }}

        /* ============ FLOATING MENU STYLES ============ */
        .floating-menu-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, var(--primary), #ec4899);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
            z-index: 1000;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 2px solid rgba(255,255,255,0.2);
        }}
        .floating-menu-btn:hover {{
            transform: scale(1.1) rotate(15deg);
        }}
        .side-menu-panel {{
            position: fixed;
            top: 0;
            right: -320px;
            width: 300px;
            height: 100vh;
            background: #0b1329;
            box-shadow: -5px 0 25px rgba(0,0,0,0.5);
            z-index: 999;
            transition: right 0.4s cubic-bezier(0.075, 0.82, 0.165, 1);
            padding: 20px;
            box-sizing: border-box;
            border-left: 2px solid #1e293b;
            overflow-y: auto;
        }}
        .side-menu-panel.open {{
            right: 0;
        }}
        .menu-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #1e293b;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .menu-header h2 {{
            margin: 0;
            font-size: 18px;
            color: #67e8f9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .close-menu-btn {{
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            flex: none;
            width: auto;
        }}
        .close-menu-btn:hover {{ color: white; }}
        .download-links-container {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .menu-download-btn {{
            width: 100%;
            background: #1e293b;
            border: 1px solid #334155;
            color: #cbd5e1;
            padding: 12px;
            border-radius: 8px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 10px;
            text-decoration: none;
            box-sizing: border-box;
        }}
        .menu-download-btn:hover {{
            background: #27354f;
            border-color: var(--secondary);
            color: white;
            transform: translateX(-4px);
        }}
        .menu-download-btn i {{
            color: var(--secondary);
            font-size: 16px;
        }}
    </style>
</head>
<body>

<div class="floating-menu-btn" onclick="toggleMenu()" title="डाउनलोड मेनू">
    <i class="fa-solid fa-download"></i>
</div>

<div class="side-menu-panel" id="sideMenu">
    <div class="menu-header">
        <h2><i class="fa-solid fa-cloud-arrow-down"></i> डाउनलोड लिंक्स</h2>
        <button class="close-menu-btn" onclick="toggleMenu()"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="download-links-container">
        {menu_buttons_html}
    </div>
</div>

<div class="container">
    <h1><i class="fa-solid fa-crosshairs"></i> S.KANHAIYA_INFO-PANEL</h1>
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
    // मेनू ओपन-क्लोज करने का फंक्शन
    function toggleMenu() {{
        const menu = document.getElementById('sideMenu');
        menu.classList.toggle('open');
    }}

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
            loaderText.innerText = "प्लेयर का पूरा डेटा निकाला जा रहा है...";
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
                        <b>प्लेयर नाम:</b> \${data.player}<br>
                        <b>UID:</b> <code>\${data.uid}</code><br>
                        <b>लेवल:</b> \${data.level}<br>
                        <b>मिले लाइक्स:</b> +\${data.given}<br>
                        <b>टोटल लाइक्स:</b> \${data.before} ➔ \${data.after}
                    `;
                }} else {{
                    resultDiv.removeAttribute('class');
                    
                    let res = data.info;
                    
                    let rawJsonString = JSON.stringify(data.raw, null, 4);

                    let infoHTML = `
                        <div class="info-card">
                            <div class="section-title"><i class="fa-solid fa-user"></i> बेसिक इनफ़ॉर्मेशन</div>
                            <div class="info-row"><span class="info-label">निकनेम (Name):</span><span class="info-value val-highlight">\${res.nickname}</span></div>
                            <div class="info-row"><span class="info-label">गेम UID:</span><span class="info-value">\${res.uid}</span></div>
                            <div class="info-row"><span class="info-label">क्षेत्र (Region):</span><span class="info-value">\${res.region}</span></div>
                            <div class="info-row"><span class="info-label">लेवल (Level):</span><span class="info-value val-success">\${res.level}</span></div>
                            <div class="info-row"><span class="info-label">टोटल एक्सपी (EXP):</span><span class="info-value">\${res.exp}</span></div>
                            <div class="info-row"><span class="info-label">कुल लाइक्स:</span><span class="info-value val-heart"><i class="fa-solid fa-heart"></i> \${res.likes}</span></div>
                            <div class="info-row"><span class="info-label">अकाउंट टाइप:</span><span class="info-value">\${res.account_type}</span></div>
                            <div class="info-row"><span class="info-label">खाता बना (Created At):</span><span class="info-value">\${res.create_at}</span></div>
                            
                            <div class="section-title"><i class="fa-solid fa-trophy"></i> रैंक और स्कोर डेटा</div>
                            <div class="info-row"><span class="info-label">BR रैंक पॉइंट:</span><span class="info-value val-highlight">\${res.br_points}</span></div>
                            <div class="info-row"><span class="info-label">CS रैंक पॉइंट:</span><span class="info-value val-highlight">\${res.cs_points}</span></div>
                            <div class="info-row"><span class="info-label">हाईएस्ट रैंक एवर:</span><span class="info-value">\${res.max_rank}</span></div>
                            <div class="info-row"><span class="info-label">क्रेडिट स्कोर:</span><span class="info-value val-success">\${res.credit_score}</span></div>
                            <div class="info-row"><span class="info-label">आखिरी बार ऑनलाइन:</span><span class="info-value">\${res.last_login}</span></div>

                            <div class="section-title"><i class="fa-solid fa-paw"></i> पेट (Pet) और अन्य</div>
                            <div class="info-row"><span class="info-label">एक्टिव पेट ID:</span><span class="info-value">\${res.pet_id}</span></div>
                            <div class="info-row"><span class="info-label">पेट लेवल:</span><span class="info-value">\${res.pet_level}</span></div>
                            
                            <div class="section-title"><i class="fa-solid fa-signature"></i> सिग्नेचर (Signature)</div>
                            <div class="info-sig">\${res.signature}</div>

                            <div class="section-title" style="color: #a78bfa;"><i class="fa-solid fa-code"></i> RAW API DATA (All Information)</div>
                            <div class="raw-data-box">
                                <pre>\${rawJsonString}</pre>
                            </div>
                        </div>
                    `;
                    resultDiv.innerHTML = infoHTML;
                }}
            }} else {{
                resultDiv.className = 'error-res';
                resultDiv.innerHTML = `❌ \${data.message}`;
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
    
    # JSON फ़ाइल से डायनामिक लिंक्स लोड करना
    links = load_menu_links()
    buttons_html = ""
    for item in links:
        title = item.get("title", "Download Link")
        url = item.get("url", "#")
        buttons_html += f'<a href="{url}" target="_blank" class="menu-download-btn"><i class="fa-solid fa-file-arrow-down"></i> {title}</a>\n'
    
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
                            "max_rank": basic.get("maxRank", "N/A"),"credit_score": credit.get("creditScore", "N/A"),
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
