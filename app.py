# app.py - Vercel compatible version
from flask import Flask, request, jsonify, render_template_string
import requests
import json
import asyncio
import aiohttp
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

async def call_like_api(region, uid):
    try:
        url = f"{API_URL}like?uid={uid}&region={region}&key={API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
    except Exception as e:
        return {"error": str(e)}

async def call_info_api(region, uid):
    try:
        url = f"{INFO_API_URL}?region={region.lower()}&uid={uid}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=12)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"HTTP {resp.status}"}
    except Exception as e:
        return {"error": str(e)}

def run_async(coro):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Simple HTML Template - Clean and minimal
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
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #00ff00;
            font-size: 24px;
            text-shadow: 0 0 10px #00ff00;
        }
        .header p {
            color: #00cc66;
            font-size: 12px;
        }
        .box {
            background: #111;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 25px;
        }
        .select-box {
            margin-bottom: 20px;
        }
        .select-box select {
            background: #1a1a1a;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 10px 15px;
            font-family: monospace;
            font-size: 14px;
            border-radius: 5px;
            width: 100%;
            max-width: 200px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group input {
            width: 100%;
            padding: 12px 15px;
            font-size: 16px;
            font-family: monospace;
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 8px;
            color: #00ff00;
            text-align: center;
        }
        .input-group input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(0,255,0,0.3);
        }
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 30px;
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-info {
            background: #00ff00;
            color: #000;
        }
        .btn-like {
            background: #ff3366;
            color: #fff;
        }
        .btn:hover {
            transform: scale(1.02);
            opacity: 0.9;
        }
        .loader {
            display: none;
            text-align: center;
            margin: 15px 0;
            color: #00ff00;
            font-size: 12px;
        }
        .loader.active {
            display: block;
        }
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #00ff00;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .result {
            margin-top: 20px;
        }
        .info-card, .like-card {
            background: rgba(0,255,0,0.05);
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .info-card h3, .like-card h3 {
            color: #00ff00;
            font-size: 14px;
            margin-bottom: 12px;
            text-align: center;
        }
        .row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px dotted rgba(0,255,0,0.2);
            font-size: 12px;
        }
        .label {
            color: #ffcc00;
        }
        .value {
            color: #00ffaa;
            text-align: right;
        }
        .alert {
            padding: 10px;
            margin: 10px 0;
            background: rgba(0,255,0,0.1);
            border-left: 3px solid #00ff00;
            color: #00ff00;
            font-size: 12px;
            text-align: center;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
            padding: 10px;
            background: rgba(0,255,0,0.05);
            border: 1px solid #00ff00;
            border-radius: 8px;
            font-size: 11px;
            color: #00cc66;
        }
        .status-bar span {
            color: #00ff00;
        }
        @media (max-width: 600px) {
            .btn { padding: 10px 20px; font-size: 14px; }
            .row { font-size: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>S.KANHAIYA INFO PANEL</h1>
            <p>FREE FIRE PLAYER INTEL SYSTEM</p>
        </div>
        
        <div class="box">
            <div class="status-bar">
                <div>🟢 SYSTEM: <span>ONLINE</span></div>
                <div>🤖 BOT: <span>ACTIVE</span></div>
                <div>❤️ LIKES LEFT: <span id="likesRemaining">2</span>/2</div>
            </div>
            
            <div class="select-box">
                <select id="region">
                    <option value="IND">🇮🇳 INDIA</option>
                    <option value="USA">🇺🇸 USA</option>
                    <option value="ID">🇮🇩 INDONESIA</option>
                    <option value="BR">🇧🇷 BRAZIL</option>
                    <option value="VN">🇻🇳 VIETNAM</option>
                    <option value="ME">🇦🇪 MIDDLE EAST</option>
                </select>
            </div>
            
            <div class="input-group">
                <input type="text" id="uid" placeholder="ENTER PLAYER UID" value="7989681100">
            </div>
            
            <div class="button-group">
                <button class="btn btn-info" onclick="getInfo()">📡 GET INFO</button>
                <button class="btn btn-like" onclick="sendLike()">❤️ SEND LIKE</button>
            </div>
            
            <div class="loader" id="loader">
                <span class="spinner"></span> PROCESSING...
            </div>
            
            <div class="result" id="result"></div>
        </div>
    </div>

    <script>
        let currentData = null;
        
        function showLoader() {
            document.getElementById('loader').classList.add('active');
        }
        
        function hideLoader() {
            document.getElementById('loader').classList.remove('active');
        }
        
        function showAlert(msg) {
            const resultDiv = document.getElementById('result');
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            alertDiv.textContent = msg;
            resultDiv.insertBefore(alertDiv, resultDiv.firstChild);
            setTimeout(() => alertDiv.remove(), 3000);
        }
        
        async function getInfo() {
            const region = document.getElementById('region').value;
            const uid = document.getElementById('uid').value.trim();
            
            if(!uid) {
                showAlert('⚠️ ENTER UID FIRST!');
                return;
            }
            
            showLoader();
            
            try {
                const response = await fetch(`/api/player?region=${region}&uid=${uid}`);
                const data = await response.json();
                hideLoader();
                
                if(data.success && data.player) {
                    currentData = data.player;
                    displayInfo(data.player);
                    showAlert('✅ PLAYER DATA FOUND!');
                } else {
                    showAlert('❌ PLAYER NOT FOUND!');
                    document.getElementById('result').innerHTML = '';
                }
            } catch(e) {
                hideLoader();
                showAlert('❌ NETWORK ERROR!');
            }
        }
        
        function displayInfo(player) {
            const basic = player.basicInfo || {};
            const clan = player.clanBasicInfo || {};
            const pet = player.petInfo || {};
            const social = player.socialInfo || {};
            const credit = player.creditScoreInfo || {};
            
            const createdAt = basic.createAt ? new Date(basic.createAt * 1000).toLocaleString() : 'N/A';
            const lastLogin = basic.lastLoginAt ? new Date(basic.lastLoginAt * 1000).toLocaleString() : 'N/A';
            
            const html = `
                <div class="info-card">
                    <h3>📡 PLAYER INTEL</h3>
                    <div class="row"><span class="label">🎮 NICKNAME</span><span class="value">${escapeHtml(basic.nickname) || 'N/A'}</span></div>
                    <div class="row"><span class="label">🆔 UID</span><span class="value">${basic.accountId || 'N/A'}</span></div>
                    <div class="row"><span class="label">🌍 REGION</span><span class="value">${basic.region || 'N/A'}</span></div>
                    <div class="row"><span class="label">⭐ LEVEL</span><span class="value">${basic.level || 0}</span></div>
                    <div class="row"><span class="label">❤️ LIKES</span><span class="value" id="likesCount">${basic.liked || 0}</span></div>
                    <div class="row"><span class="label">🏆 BR RANK</span><span class="value">${basic.rank || 0}</span></div>
                    <div class="row"><span class="label">🎯 CS RANK</span><span class="value">${basic.csRank || 0}</span></div>
                    <div class="row"><span class="label">💎 CREDIT</span><span class="value">${credit.creditScore || 100}</span></div>
                    <div class="row"><span class="label">🏢 CLAN</span><span class="value">${escapeHtml(clan.clanName) || 'No Clan'}</span></div>
                    <div class="row"><span class="label">🐾 PET LEVEL</span><span class="value">${pet.level || 0}</span></div>
                    <div class="row"><span class="label">📅 CREATED</span><span class="value">${createdAt}</span></div>
                    <div class="row"><span class="label">🕐 LAST LOGIN</span><span class="value">${lastLogin}</span></div>
                    <div class="row"><span class="label">✍️ SIGNATURE</span><span class="value">${escapeHtml(social.signature) || 'N/A'}</span></div>
                </div>
            `;
            
            document.getElementById('result').innerHTML = html;
        }
        
        async function sendLike() {
            const region = document.getElementById('region').value;
            const uid = document.getElementById('uid').value.trim();
            const remainingSpan = document.getElementById('likesRemaining');
            let remaining = parseInt(remainingSpan.innerText);
            
            if(remaining <= 0) {
                showAlert('❌ NO LIKES LEFT TODAY!');
                return;
            }
            
            if(!uid) {
                showAlert('⚠️ ENTER UID FIRST!');
                return;
            }
            
            showLoader();
            
            try {
                const response = await fetch(`/api/like?region=${region}&uid=${uid}`);
                const data = await response.json();
                hideLoader();
                
                if(data.success && data.status === 1) {
                    const likesSpan = document.getElementById('likesCount');
                    if(likesSpan) {
                        likesSpan.innerText = parseInt(likesSpan.innerText) + data.LikesGivenByAPI;
                    }
                    remainingSpan.innerText = remaining - 1;
                    
                    const likeHtml = `
                        <div class="like-card">
                            <h3>✅ LIKE SENT!</h3>
                            <div class="row"><span class="label">👤 PLAYER</span><span class="value">${escapeHtml(data.PlayerNickname) || uid}</span></div>
                            <div class="row"><span class="label">📊 LIKES</span><span class="value">${data.LikesbeforeCommand} → ${data.LikesafterCommand} (+${data.LikesGivenByAPI})</span></div>
                        </div>
                    `;
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.insertAdjacentHTML('afterbegin', likeHtml);
                    showAlert(`❤️ +${data.LikesGivenByAPI} LIKE SENT!`);
                } else {
                    showAlert('❌ FAILED TO SEND LIKE!');
                }
            } catch(e) {
                hideLoader();
                showAlert('❌ NETWORK ERROR!');
            }
        }
        
        function escapeHtml(str) {
            if(!str) return str;
            return String(str).replace(/[&<>]/g, function(m) {
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
        result = run_async(call_info_api(region, uid))
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
        result = run_async(call_like_api(region, uid))
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

# For Vercel
def handler(request, context=None):
    return app(request)

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)