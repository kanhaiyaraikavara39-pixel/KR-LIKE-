# app.py - Vercel compatible (serverless)
from flask import Flask, request, jsonify, render_template_string
import requests
import json
import base64
from datetime import datetime, date

app = Flask(__name__)

API_URL = "https://kanhaiya-raikwar.vercel.app/"
INFO_API_URL = "https://s-kanhaiya-ff-info.vercel.app/player-info"
ENCODED_KEY = "WkVYWFk="
API_KEY = base64.b64decode(ENCODED_KEY).decode()

daily_limit = 2
user_limits = {}

def today_str():
    return str(date.today())

def can_user_like(uid):
    t = today_str()
    if uid not in user_limits or user_limits[uid]['date'] != t:
        user_limits[uid] = {'date': t, 'count': 0}
        return True
    return user_limits[uid]['count'] < daily_limit

def update_user_like(uid):
    t = today_str()
    if uid not in user_limits or user_limits[uid]['date'] != t:
        user_limits[uid] = {'date': t, 'count': 0}
    user_limits[uid]['count'] += 1

# Synchronous functions (no asyncio for Vercel)
def call_like_api(region, uid):
    try:
        url = f"{API_URL}like?uid={uid}&region={region}&key={API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def call_info_api(region, uid):
    try:
        url = f"{INFO_API_URL}?region={region.lower()}&uid={uid}"
        response = requests.get(url, timeout=12)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Simple HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S.KANHAIYA INFO PANEL</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 15px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #00ff00;
            font-size: 22px;
            text-shadow: 0 0 10px #00ff00;
        }
        .header p {
            color: #00cc66;
            font-size: 11px;
        }
        .box {
            background: #111;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
            padding: 8px;
            background: rgba(0,255,0,0.05);
            border: 1px solid #00ff00;
            border-radius: 8px;
            font-size: 10px;
            color: #00cc66;
        }
        .status-bar span {
            color: #00ff00;
        }
        select, input {
            background: #1a1a1a;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 10px;
            font-family: monospace;
            font-size: 14px;
            border-radius: 5px;
            width: 100%;
            margin-bottom: 12px;
        }
        input {
            text-align: center;
        }
        .button-group {
            display: flex;
            gap: 12px;
            justify-content: center;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 10px 25px;
            font-family: monospace;
            font-size: 14px;
            font-weight: bold;
            border: none;
            border-radius: 50px;
            cursor: pointer;
        }
        .btn-info {
            background: #00ff00;
            color: #000;
        }
        .btn-like {
            background: #ff3366;
            color: #fff;
        }
        .loader {
            display: none;
            text-align: center;
            margin: 10px 0;
            color: #00ff00;
            font-size: 11px;
        }
        .loader.show {
            display: block;
        }
        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #00ff00;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            margin-right: 6px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .result {
            margin-top: 15px;
        }
        .info-card, .like-card {
            background: rgba(0,255,0,0.05);
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .info-card h3, .like-card h3 {
            color: #00ff00;
            font-size: 13px;
            margin-bottom: 10px;
            text-align: center;
        }
        .row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px dotted rgba(0,255,0,0.2);
            font-size: 11px;
        }
        .label {
            color: #ffcc00;
        }
        .value {
            color: #00ffaa;
            text-align: right;
        }
        .alert {
            padding: 8px;
            margin: 8px 0;
            background: rgba(0,255,0,0.1);
            border-left: 3px solid #00ff00;
            color: #00ff00;
            font-size: 11px;
            text-align: center;
        }
        button:active {
            transform: scale(0.98);
        }
        @media (max-width: 500px) {
            .btn { padding: 8px 18px; font-size: 12px; }
            .row { font-size: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>S.KANHAIYA PANEL</h1>
            <p>FREE FIRE PLAYER INTEL</p>
        </div>
        
        <div class="box">
            <div class="status-bar">
                <div>🟢 SYSTEM: <span>ONLINE</span></div>
                <div>❤️ LIKES: <span id="likesRemaining">2</span>/2</div>
                <div>🔐 S.KANHAIYA</div>
            </div>
            
            <select id="region">
                <option value="IND">🇮🇳 INDIA</option>
                <option value="USA">🇺🇸 USA</option>
                <option value="ID">🇮🇩 INDONESIA</option>
                <option value="BR">🇧🇷 BRAZIL</option>
                <option value="VN">🇻🇳 VIETNAM</option>
                <option value="ME">🇦🇪 MIDDLE EAST</option>
            </select>
            
            <input type="text" id="uid" placeholder="Enter Player UID" value="7989681100">
            
            <div class="button-group">
                <button class="btn btn-info" onclick="getInfo()">📡 GET INFO</button>
                <button class="btn btn-like" onclick="sendLike()">❤️ LIKE</button>
            </div>
            
            <div id="loader" class="loader">
                <span class="spinner"></span> PROCESSING...
            </div>
            
            <div id="result"></div>
        </div>
    </div>

    <script>
        function showLoader() {
            document.getElementById('loader').classList.add('show');
        }
        function hideLoader() {
            document.getElementById('loader').classList.remove('show');
        }
        function showAlert(msg) {
            const resultDiv = document.getElementById('result');
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            alertDiv.innerText = msg;
            resultDiv.insertBefore(alertDiv, resultDiv.firstChild);
            setTimeout(() => alertDiv.remove(), 2500);
        }
        
        async function getInfo() {
            const region = document.getElementById('region').value;
            const uid = document.getElementById('uid').value.trim();
            if(!uid) { showAlert('⚠️ Enter UID!'); return; }
            
            showLoader();
            try {
                const resp = await fetch(`/api/player?region=${region}&uid=${uid}`);
                const data = await resp.json();
                hideLoader();
                
                if(data.success && data.player) {
                    displayInfo(data.player);
                    showAlert('✅ Data Found!');
                } else {
                    showAlert('❌ Player Not Found!');
                    document.getElementById('result').innerHTML = '';
                }
            } catch(e) {
                hideLoader();
                showAlert('❌ Network Error!');
            }
        }
        
        function displayInfo(p) {
            const b = p.basicInfo || {};
            const c = p.clanBasicInfo || {};
            const pet = p.petInfo || {};
            const soc = p.socialInfo || {};
            const cred = p.creditScoreInfo || {};
            
            const created = b.createAt ? new Date(b.createAt * 1000).toLocaleString() : 'N/A';
            const last = b.lastLoginAt ? new Date(b.lastLoginAt * 1000).toLocaleString() : 'N/A';
            
            const html = `
                <div class="info-card">
                    <h3>📡 PLAYER DATA</h3>
                    <div class="row"><span class="label">🎮 NAME</span><span class="value">${escapeHtml(b.nickname) || 'N/A'}</span></div>
                    <div class="row"><span class="label">🆔 UID</span><span class="value">${b.accountId || 'N/A'}</span></div>
                    <div class="row"><span class="label">⭐ LEVEL</span><span class="value">${b.level || 0}</span></div>
                    <div class="row"><span class="label">❤️ LIKES</span><span class="value" id="likesCount">${b.liked || 0}</span></div>
                    <div class="row"><span class="label">🏆 BR RANK</span><span class="value">${b.rank || 0}</span></div>
                    <div class="row"><span class="label">🎯 CS RANK</span><span class="value">${b.csRank || 0}</span></div>
                    <div class="row"><span class="label">💎 CREDIT</span><span class="value">${cred.creditScore || 100}</span></div>
                    <div class="row"><span class="label">🏢 CLAN</span><span class="value">${escapeHtml(c.clanName) || 'None'}</span></div>
                    <div class="row"><span class="label">🐾 PET</span><span class="value">Level ${pet.level || 0}</span></div>
                    <div class="row"><span class="label">📅 CREATED</span><span class="value">${created}</span></div>
                    <div class="row"><span class="label">🕐 LAST</span><span class="value">${last}</span></div>
                    <div class="row"><span class="label">✍️ SIGN</span><span class="value">${escapeHtml(soc.signature) || '-'}</span></div>
                </div>
            `;
            document.getElementById('result').innerHTML = html;
        }
        
        async function sendLike() {
            const region = document.getElementById('region').value;
            const uid = document.getElementById('uid').value.trim();
            const remainSpan = document.getElementById('likesRemaining');
            let remain = parseInt(remainSpan.innerText);
            
            if(remain <= 0) { showAlert('❌ No likes left today!'); return; }
            if(!uid) { showAlert('⚠️ Enter UID!'); return; }
            
            showLoader();
            try {
                const resp = await fetch(`/api/like?region=${region}&uid=${uid}`);
                const data = await resp.json();
                hideLoader();
                
                if(data.success && data.status === 1) {
                    const likesSpan = document.getElementById('likesCount');
                    if(likesSpan) likesSpan.innerText = parseInt(likesSpan.innerText) + data.LikesGivenByAPI;
                    remainSpan.innerText = remain - 1;
                    
                    const likeHtml = `
                        <div class="like-card">
                            <h3>✅ LIKE SENT!</h3>
                            <div class="row"><span class="label">👤 PLAYER</span><span class="value">${escapeHtml(data.PlayerNickname) || uid}</span></div>
                            <div class="row"><span class="label">❤️ LIKES</span><span class="value">${data.LikesbeforeCommand} → ${data.LikesafterCommand} (+${data.LikesGivenByAPI})</span></div>
                        </div>
                    `;
                    document.getElementById('result').insertAdjacentHTML('afterbegin', likeHtml);
                    showAlert(`❤️ +${data.LikesGivenByAPI} Like Sent!`);
                } else {
                    showAlert('❌ Like Failed!');
                }
            } catch(e) {
                hideLoader();
                showAlert('❌ Network Error!');
            }
        }
        
        function escapeHtml(s) {
            if(!s) return s;
            return String(s).replace(/[&<>]/g, function(m) {
                if(m === '&') return '&amp;';
                if(m === '<') return '&lt;';
                if(m === '>') return '&gt;';
                return m;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/player')
def get_player_info():
    region = request.args.get('region', 'IND')
    uid = request.args.get('uid', '')
    if not uid:
        return jsonify({"success": False, "error": "UID required"}), 400
    
    try:
        result = call_info_api(region, uid)
        if result and "error" not in result:
            return jsonify({"success": True, "player": result})
        return jsonify({"success": False, "error": result.get("error", "API failed")}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/like')
def send_like():
    region = request.args.get('region', 'IND')
    uid = request.args.get('uid', '')
    if not uid:
        return jsonify({"success": False, "error": "UID required"}), 400
    
    try:
        result = call_like_api(region, uid)
        if result and "error" not in result:
            status = result.get('status')
            if status == 1:
                return jsonify({
                    "success": True,
                    "status": status,
                    "PlayerNickname": result.get('PlayerNickname', 'Unknown'),
                    "LikesbeforeCommand": result.get('LikesbeforeCommand', 0),
                    "LikesafterCommand": result.get('LikesafterCommand', 0),
                    "LikesGivenByAPI": result.get('LikesGivenByAPI', 0)
                })
            return jsonify({"success": False, "error": "Like failed", "status": status}), 400
        return jsonify({"success": False, "error": result.get("error", "API failed")}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# This is for Vercel serverless function
app.debug = False

# For Vercel
def handler(event, context):
    return app(event, context)

# Local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)