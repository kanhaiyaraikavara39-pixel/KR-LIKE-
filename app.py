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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>S.KANHAIYA_INFO_PANEL</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: #000000;
            font-family: 'Share Tech Mono', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        
        /* बैकग्राउंड एनिमेशन */
        #matrixCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.25;
        }
        
        .stars {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            pointer-events: none;
        }
        
        .star {
            position: absolute;
            background: #00ff00;
            border-radius: 50%;
            opacity: 0;
            animation: floatStar 6s infinite ease-in-out;
        }
        
        @keyframes floatStar {
            0% { opacity: 0; transform: translateY(100vh) scale(0); }
            15% { opacity: 0.8; }
            85% { opacity: 0.8; }
            100% { opacity: 0; transform: translateY(-20vh) scale(1.5); }
        }
        
        .scan-line {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom, transparent 50%, rgba(0, 255, 0, 0.04) 50%);
            background-size: 100% 6px;
            pointer-events: none;
            z-index: 1;
            animation: scanMove 8s linear infinite;
        }
        
        @keyframes scanMove {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }
        
        .main-container {
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
            z-index: 2;
        }
        
        .site-title {
            text-align: center;
            margin-bottom: 15px;
        }
        
        .site-title h1 {
            color: #00ff00;
            font-size: 26px;
            letter-spacing: 3px;
            text-shadow: 0 0 15px #00ff00;
            animation: titleGlow 2s ease-in-out infinite;
        }
        
        @keyframes titleGlow {
            0%, 100% { text-shadow: 0 0 5px #00ff00; }
            50% { text-shadow: 0 0 20px #00ff00; }
        }
        
        .site-title p {
            color: #00cc66;
            font-size: 11px;
        }
        
        .terminal-box {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            border: 2px solid #00ff00;
            border-radius: 15px;
            padding: 20px;
        }
        
        .status-bar {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(0, 255, 0, 0.05);
            border: 1px dashed #00ff00;
            border-radius: 8px;
        }
        
        .status-item {
            color: #00cc66;
            font-size: 10px;
        }
        
        .status-item span {
            color: #00ff00;
        }
        
        .button-grid {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin: 15px 0;
        }
        
        .nav-btn {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border: 2px solid #00ff00;
            color: #00ff00;
            font-family: monospace;
            font-size: 12px;
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .nav-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 0 12px #00ff00;
        }
        
        .btn-photo { border-color: #ff00ff; color: #ff00ff; }
        .btn-vmail { border-color: #ffcc00; color: #ffcc00; }
        .btn-inbox { border-color: #00ffcc; color: #00ffcc; }
        .btn-gift { border-color: #ff6600; color: #ff6600; }
        .btn-insta { border-color: #ff00ff; color: #ff00ff; }
        
        .region-selector {
            margin: 12px 0;
        }
        
        .region-selector select {
            background: #0a0a0a;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 6px 15px;
            font-family: monospace;
            font-size: 13px;
            border-radius: 30px;
            width: 100%;
            max-width: 180px;
        }
        
        .uid-section {
            margin: 15px 0;
        }
        
        .uid-label {
            color: #00ff00;
            font-size: 13px;
            margin-bottom: 8px;
        }
        
        .uid-input-group {
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
        }
        
        .uid-input-group input {
            width: 100%;
            max-width: 320px;
            padding: 12px 18px;
            font-size: 16px;
            font-family: monospace;
            background: #0a0a0a;
            border: 2px solid #00ff00;
            border-radius: 50px;
            color: #00ff00;
            text-align: center;
            outline: none;
        }
        
        .uid-input-group input:focus {
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
        }
        
        /* दो बटन साथ-साथ */
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 5px;
        }
        
        .info-btn {
            background: linear-gradient(135deg, #00ff00, #00cc66);
            border: none;
            color: #000;
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 30px;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .like-action-btn {
            background: linear-gradient(135deg, #ff0066, #ff3366);
            border: none;
            color: white;
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 30px;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .info-btn:hover, .like-action-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 0 15px;
        }
        
        /* छोटा लोडर (स्क्रीन ब्लॉक नहीं) */
        .small-loader {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #00ff00;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-left: 8px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            color: #00ff00;
            font-size: 11px;
            margin-top: 8px;
            text-align: center;
        }
        
        .info-container {
            margin-top: 20px;
            border-top: 2px solid #00ff00;
            padding-top: 15px;
        }
        
        .info-title {
            color: #00ff00;
            font-size: 13px;
            text-align: center;
            margin-bottom: 12px;
        }
        
        .data-card {
            background: rgba(0, 255, 0, 0.05);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 15px;
        }
        
        .data-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px dotted rgba(0, 255, 0, 0.2);
        }
        
        .data-label {
            color: #ffcc00;
            font-weight: bold;
            font-size: 11px;
        }
        
        .data-value {
            color: #00ffaa;
            font-size: 11px;
            text-align: right;
        }
        
        .like-result-card {
            background: rgba(255, 51, 102, 0.1);
            border: 1px solid #ff3366;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .like-result-card .result-text {
            color: #ff6699;
            font-size: 12px;
        }
        
        .raw-section {
            margin-top: 15px;
            border-top: 1px dashed #00ff00;
            padding-top: 12px;
        }
        
        .raw-header {
            color: #00ff00;
            cursor: pointer;
            font-size: 11px;
            text-align: center;
        }
        
        .raw-content {
            background: #0a1a0a;
            padding: 12px;
            overflow-x: auto;
            font-size: 10px;
            color: #88ff88;
            white-space: pre-wrap;
            word-break: break-all;
            border-radius: 8px;
            border: 1px solid #00ff00;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }
        
        .raw-content.show {
            display: block;
        }
        
        .raw-buttons {
            text-align: center;
            margin-top: 8px;
        }
        
        .raw-btn {
            background: #000;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 3px 15px;
            margin: 0 3px;
            cursor: pointer;
            font-family: monospace;
            font-size: 10px;
            border-radius: 20px;
        }
        
        .alert {
            padding: 8px;
            margin: 10px 0;
            border-left: 3px solid #00ff00;
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
            font-size: 11px;
            text-align: center;
        }
        
        @media (max-width: 600px) {
            .action-buttons { gap: 10px; }
            .info-btn, .like-action-btn { padding: 8px 20px; font-size: 14px; }
            .nav-btn { font-size: 10px; padding: 6px 12px; }
        }
    </style>
</head>
<body>
    
    <canvas id="matrixCanvas"></canvas>
    <div class="stars" id="stars"></div>
    <div class="scan-line"></div>
    
    <div class="main-container">
        <div class="site-title">
            <h1>S.KANHAIYA_INFO_PANEL</h1>
            <p>⚡ FREE FIRE PLAYER INTEL EXTRACTOR ⚡</p>
        </div>
        
        <div class="terminal-box">
            <div class="status-bar">
                <div class="status-item">>> SYSTEM: <span>ONLINE</span></div>
                <div class="status-item">>> BOT: <span>ACTIVE</span></div>
                <div class="status-item">>> ENCRYPTION: <span>S.KANHAIYA</span></div>
                <div class="status-item">>> LIKES LEFT: <span id="likesRemaining">2</span> / 2</div>
            </div>
            
            <div class="button-grid">
                <button class="nav-btn btn-photo" onclick="showComingSoon('📸 प्लेयर फोटो')">📷 PLAYER PHOTO</button>
                <button class="nav-btn btn-vmail" onclick="showComingSoon('📧 V-MAIL')">📧 V-MAIL</button>
                <button class="nav-btn btn-inbox" onclick="showComingSoon('📥 INBOX')">📥 INBOX</button>
                <button class="nav-btn btn-gift" onclick="showComingSoon('🎁 GIFT CODE')">🎁 GIFT CODE</button>
                <a href="https://www.instagram.com/s.kanhaiya.7m" target="_blank" class="nav-btn btn-insta">📷 INSTAGRAM</a>
            </div>
            
            <div class="region-selector">
                <select id="region">
                    <option value="IND">🇮🇳 INDIA (IND)</option>
                    <option value="USA">🇺🇸 USA</option>
                    <option value="ID">🇮🇩 INDONESIA (ID)</option>
                    <option value="BR">🇧🇷 BRAZIL (BR)</option>
                    <option value="VN">🇻🇳 VIETNAM (VN)</option>
                    <option value="ME">🇦🇪 MIDDLE EAST (ME)</option>
                </select>
            </div>
            
            <div class="uid-section">
                <div class="uid-label">┌─[ENTER TARGET UID]─</div>
                <div class="uid-input-group">
                    <input type="text" id="uid" placeholder="9230844760" value="7989681100" autocomplete="off">
                    
                    <!-- दो बटन साथ-साथ: INFO और LIKE -->
                    <div class="action-buttons">
                        <button class="info-btn" onclick="fetchInfo()">📡 GET INFO</button>
                        <button class="like-action-btn" onclick="sendLike()">❤️ SEND LIKE</button>
                    </div>
                    
                    <!-- छोटा लोडर एनिमेशन (UID बॉक्स के नीचे) -->
                    <div id="smallLoader" style="display:none;" class="loading-text">
                        <span class="small-loader"></span> PROCESSING...
                    </div>
                </div>
            </div>
            
            <div id="result"></div>
        </div>
    </div>

    <script>
        let currentRawData = null;
        let currentRegion = "IND";
        
        function showSmallLoader() {
            document.getElementById('smallLoader').style.display = 'block';
        }
        
        function hideSmallLoader() {
            document.getElementById('smallLoader').style.display = 'none';
        }
        
        async function fetchInfo() {
            const region = document.getElementById('region').value;
            currentRegion = region;
            const uid = document.getElementById('uid').value.trim();
            if(!uid) { showAlert("⚠️ ENTER UID!"); return; }
            
            showSmallLoader();
            try {
                const response = await fetch(`/api/player?region=${region}&uid=${uid}`);
                const data = await response.json();
                hideSmallLoader();
                if(data.success && data.player) {
                    currentRawData = data.player;
                    displayInfoData(data.player);
                    showAlert("✅ DATA DECRYPTED!");
                } else {
                    showAlert("❌ PLAYER NOT FOUND!");
                    document.getElementById('result').innerHTML = '';
                }
            } catch(e) {
                hideSmallLoader();
                showAlert("❌ NETWORK ERROR!");
            }
        }
        
        function displayInfoData(player) {
            const basic = player.basicInfo || {};
            const clan = player.clanBasicInfo || {};
            const pet = player.petInfo || {};
            const social = player.socialInfo || {};
            const credit = player.creditScoreInfo || {};
            
            const createdAt = basic.createAt ? new Date(basic.createAt * 1000).toLocaleString() : 'N/A';
            const lastLogin = basic.lastLoginAt ? new Date(basic.lastLoginAt * 1000).toLocaleString() : 'N/A';
            
            const formattedData = `
                <div class="data-row"><span class="data-label">🎮 NICKNAME</span><span class="data-value">${escapeHtml(basic.nickname) || 'N/A'}</span></div>
                <div class="data-row"><span class="data-label">🆔 UID</span><span class="data-value">${basic.accountId || 'N/A'}</span></div>
                <div class="data-row"><span class="data-label">🌍 REGION</span><span class="data-value">${basic.region || 'N/A'}</span></div>
                <div class="data-row"><span class="data-label">⭐ LEVEL</span><span class="data-value">${basic.level || 0}</span></div>
                <div class="data-row"><span class="data-label">📊 EXP</span><span class="data-value">${(basic.exp || 0).toLocaleString()}</span></div>
                <div class="data-row"><span class="data-label">❤️ LIKES</span><span class="data-value" id="likesCount">${basic.liked || 0}</span></div>
                <div class="data-row"><span class="data-label">🏆 BR RANK</span><span class="data-value">${basic.rank || 0}</span></div>
                <div class="data-row"><span class="data-label">📈 BR POINTS</span><span class="data-value">${basic.rankingPoints || 0}</span></div>
                <div class="data-row"><span class="data-label">🎯 CS RANK</span><span class="data-value">${basic.csRank || 0}</span></div>
                <div class="data-row"><span class="data-label">⚡ CS POINTS</span><span class="data-value">${basic.csRankingPoints || 0}</span></div>
                <div class="data-row"><span class="data-label">💎 CREDIT</span><span class="data-value">${credit.creditScore || 100}</span></div>
                <div class="data-row"><span class="data-label">🏢 CLAN</span><span class="data-value">${escapeHtml(clan.clanName) || 'No Clan'}</span></div>
                <div class="data-row"><span class="data-label">🐾 PET LEVEL</span><span class="data-value">${pet.level || 0}</span></div>
                <div class="data-row"><span class="data-label">📅 CREATED</span><span class="data-value">${createdAt}</span></div>
                <div class="data-row"><span class="data-label">🕐 LAST LOGIN</span><span class="data-value">${lastLogin}</span></div>
                <div class="data-row"><span class="data-label">✍️ SIGNATURE</span><span class="data-value" style="font-size:10px;">${escapeHtml(social.signature) || 'N/A'}</span></div>
            `;
            
            const rawJson = JSON.stringify(currentRawData, null, 2);
            
            const html = `
                <div class="info-container">
                    <div class="info-title">📡 [ TARGET INTEL DECRYPTED ] 📡</div>
                    <div class="data-card">
                        ${formattedData}
                    </div>
                    <div class="raw-section">
                        <div class="raw-header" onclick="toggleRaw()">▼ [ RAW API RESPONSE ] ▼</div>
                        <div id="rawContent" class="raw-content">${escapeHtml(rawJson)}</div>
                        <div class="raw-buttons">
                            <button class="raw-btn" onclick="copyRaw()">📋 COPY</button>
                            <button class="raw-btn" onclick="hideRaw()">🔒 HIDE</button>
                        </div>
                    </div>
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
                showAlert("❌ NO LIKES LEFT TODAY!");
                return;
            }
            
            if(!uid) { showAlert("⚠️ ENTER UID!"); return; }
            
            showSmallLoader();
            try {
                const response = await fetch(`/api/like?region=${region}&uid=${uid}`);
                const data = await response.json();
                hideSmallLoader();
                
                if(data.success && data.status === 1) {
                    // लाइक काउंट अपडेट करें
                    const likesSpan = document.getElementById('likesCount');
                    if(likesSpan) {
                        likesSpan.innerText = parseInt(likesSpan.innerText) + 1;
                    }
                    remainingSpan.innerText = remaining - 1;
                    
                    // लाइक रिजल्ट दिखाएं
                    const resultDiv = document.getElementById('result');
                    const likeResultHtml = `
                        <div class="like-result-card">
                            <div class="result-text">
                                ✅ LIKE SENT SUCCESSFULLY!<br>
                                👤 ${escapeHtml(data.PlayerNickname) || uid}<br>
                                📊 ${data.LikesbeforeCommand} → ${data.LikesafterCommand} (+${data.LikesGivenByAPI})
                            </div>
                        </div>
                    `;
                    if(resultDiv.firstChild) {
                        resultDiv.insertBefore(createElementFromHTML(likeResultHtml), resultDiv.firstChild);
                    } else {
                        resultDiv.innerHTML = likeResultHtml + resultDiv.innerHTML;
                    }
                    showAlert(`❤️ +${data.LikesGivenByAPI} LIKE SENT!`);
                } else {
                    showAlert("❌ FAILED TO SEND LIKE!");
                }
            } catch(e) {
                hideSmallLoader();
                showAlert("❌ NETWORK ERROR!");
            }
        }
        
        function createElementFromHTML(htmlString) {
            const div = document.createElement('div');
            div.innerHTML = htmlString.trim();
            return div.firstChild;
        }
        
        function toggleRaw() {
            const raw = document.getElementById('rawContent');
            raw.classList.toggle('show');
        }
        
        function copyRaw() {
            const rawText = document.getElementById('rawContent').innerText;
            navigator.clipboard.writeText(rawText);
            showAlert("📋 RAW DATA COPIED!");
        }
        
        function hideRaw() {
            document.getElementById('rawContent').classList.remove('show');
        }
        
        function showComingSoon(feature) {
            showAlert(`🚀 ${feature} फीचर जल्द आ रहा है!`);
        }
        
        function showAlert(msg) {
            const resultDiv = document.getElementById('result');
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            alertDiv.innerHTML = msg;
            if(resultDiv.firstChild) {
                resultDiv.insertBefore(alertDiv, resultDiv.firstChild);
            } else {
                resultDiv.appendChild(alertDiv);
            }
            setTimeout(() => alertDiv.remove(), 3000);
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
        
        // मैट्रिक्स रेन
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
        const fontSize = 14;
        let columns = canvas.width / fontSize;
        let drops = [];
        function initDrops() {
            columns = canvas.width / fontSize;
            drops = [];
            for(let i = 0; i < columns; i++) drops[i] = Math.random() * canvas.height / fontSize;
        }
        initDrops();
        
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0,0,0,0.04)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0f0';
            ctx.font = fontSize + 'px monospace';
            for(let i = 0; i < drops.length; i++) {
                ctx.fillText(chars[Math.floor(Math.random()*chars.length)], i*fontSize, drops[i]*fontSize);
                if(drops[i]*fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 50);
        window.addEventListener('resize', () => { resizeCanvas(); initDrops(); });
        
        // स्टार्स
        for(let i = 0; i < 80; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.left = Math.random() * 100 + '%';
            star.style.width = star.style.height = (Math.random() * 3 + 1) + 'px';
            star.style.animationDelay = Math.random() * 8 + 's';
            star.style.animationDuration = (Math.random() * 5 + 4) + 's';
            document.getElementById('stars').appendChild(star);
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)