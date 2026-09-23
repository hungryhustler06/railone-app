from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import uuid

# Initialize the application
app = FastAPI(title="RailOne Backend")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic model for the POST request
class PassRequest(BaseModel):
    user_id: int
    ticket_class: str
    source_station: str
    destination_station: str
    pass_duration_days: int
    cost: float

# The POST endpoint to issue a pass
@app.post("/api/v1/passes/issue", status_code=status.HTTP_201_CREATED)
async def issue_season_pass(request: PassRequest):
    try:
        current_balance = 1500.00 # Mocked balance
        if current_balance < request.cost:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance.")
        
        issue_time = datetime.now()
        expiry_time = issue_time + timedelta(days=request.pass_duration_days)
        raw_signature = f"{request.user_id}-{request.ticket_class}-{request.source_station}-{expiry_time.timestamp()}-{uuid.uuid4()}"
        qr_signature_hash = hashlib.sha256(raw_signature.encode()).hexdigest()
        
        return {
            "status": "success",
            "pass_details": {
                "source": request.source_station,
                "destination": request.destination_station,
                "valid_until": expiry_time.isoformat(),
                "qr_signature": qr_signature_hash
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# The GET endpoint to display the pass securely
@app.get("/api/v1/passes/active/{user_id}", status_code=status.HTTP_200_OK)
async def get_active_pass(user_id: int, device_id: str = Query(..., description="Hardware ID for anti-sharing")):
    user_device = "mocked-device-id-123" 
    
    if device_id != user_device:
         raise HTTPException(status_code=403, detail="Pass tied to a different device.")

    active_pass = {
        "ticket_class": "First",
        "source": "MANKHURD",
        "destination": "GHATKOPAR",
        "issue_date": "2026-07-20T08:00:00",
        "expiry_date": "2027-08-20T08:00:00",
        "qr_signature": "mocked_sha256_hash_string"
    }

    if not active_pass:
        raise HTTPException(status_code=404, detail="No active pass found.")

    return {
        "server_time": datetime.now().isoformat(),
        "pass_data": active_pass
    }


@app.get("/home", response_class=HTMLResponse)
async def home_screen():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RailOne Home</title>
        <!-- PWA Links -->
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#ffffff">
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/sw.js')
                .then(() => console.log('Service Worker Registered'));
            }
        </script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #ffffff; color: #1e293b; display: flex; justify-content: center; }
            .app-container { width: 100%; max-width: 414px; position: relative; padding-bottom: 80px; box-shadow: 0 0 20px rgba(0,0,0,0.05); min-height: 100vh; }
            
            /* Header */
            .header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; }
            .lang-icon { color: #2563eb; font-weight: bold; font-size: 20px; }
            .logo { font-size: 24px; font-weight: 800; color: #334155; }
            .bell-icon { position: relative; font-size: 20px; }
            .badge { position: absolute; top: -6px; right: -8px; background: #ef4444; color: white; border-radius: 10px; font-size: 10px; padding: 2px 6px; font-weight: bold; }
            
            /* Typography */
            .greeting { font-size: 14px; padding: 0 20px; font-weight: 600; color: #0f172a; margin-top: 8px; }
            .section-title { font-size: 18px; font-weight: 700; padding: 0 20px; margin: 24px 0 12px; color: #1e3a8a; }

            /* Journey Planner */
            .journey-grid { display: flex; gap: 12px; padding: 0 20px; justify-content: space-between; }
            .j-card { flex: 1; text-align: center; font-size: 13px; color: #64748b; }
            .j-img { height: 80px; width: 100%; border-radius: 12px; margin-bottom: 8px; background-size: cover; background-position: center; border: 1px solid #e2e8f0; }
            .img-res { background-image: url('/static/reserved.png'); }
            .img-unres { background-image: url('/static/unreserved.png'); }
            .img-plat { background-image: url('/static/platform.png'); }
            
            /* More Offerings */
            .offerings-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px 12px; padding: 0 20px; }
            .o-card { display: flex; flex-direction: column; align-items: center; text-align: center; font-size: 11px; font-weight: 500; color: #334155; }
            .o-icon-img { width: 68px; height: 68px; border-radius: 14px; margin-bottom: 8px; object-fit: cover; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            
            /* Ticket Card */
            .ticket-container { padding: 0 20px; }
            .ticket-card { background: linear-gradient(135deg, #7c3aed, #a855f7); border-radius: 16px; padding: 20px; color: white; position: relative; display: flex; flex-direction: column; gap: 16px; box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3); }
            /* Cutouts */
            .ticket-card::before, .ticket-card::after { content: ''; position: absolute; top: -10px; right: 20%; width: 20px; height: 20px; background: white; border-radius: 50%; }
            .ticket-card::after { top: auto; bottom: -10px; }
            
            .t-date { font-size: 13px; opacity: 0.9; }
            .t-stations { font-size: 13px; letter-spacing: 1px; display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 16px; }
            .t-footer { display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 600; }
            .btn-group { display: flex; gap: 8px; }
            .btn { border: 1px solid white; background: transparent; color: white; padding: 6px 14px; border-radius: 20px; font-size: 12px; cursor: pointer; }
            
            /* Bottom Nav */
            .bottom-nav { position: absolute; bottom: 0; width: 100%; background: #0052cc; color: white; display: flex; justify-content: space-around; padding: 12px 0 20px; }
            .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 11px; opacity: 0.6; cursor: pointer; }
            .nav-item.active { opacity: 1; font-weight: 600; }
            .nav-icon { font-size: 22px; margin-bottom: 4px; }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Header -->
            <div class="header">
                <div class="lang-icon">A/अ</div>
                <div class="logo">RailOne</div>
                <div class="bell-icon">🔔<span class="badge">10</span></div>
            </div>
            
            <div class="greeting">Hi, Soham Khedekar!</div>
            
            <!-- Journey Planner -->
            <div class="section-title">Journey Planner</div>
            <div class="journey-grid">
                <div class="j-card"><div class="j-img img-res"></div>Reserved</div>
                <div class="j-card"><div class="j-img img-unres"></div>Unreserved</div>
                <div class="j-card"><div class="j-img img-plat"></div>Platform</div>
            </div>
            
            <!-- More Offerings -->
            <div class="section-title">More Offerings</div>
            <div class="offerings-grid">
                <div class="o-card"><img src="/static/search_trains.png" class="o-icon-img" alt="Search">Search<br>Trains</div>
                <div class="o-card"><img src="/static/pnr_status.png" class="o-icon-img" alt="PNR">PNR<br>Status</div>
                <div class="o-card"><img src="/static/coach_position.png" class="o-icon-img" alt="Coach">Coach<br>Position</div>
                <div class="o-card"><img src="/static/track_your_train.png" class="o-icon-img" alt="Track">Track Your<br>Train</div>
                <div class="o-card"><img src="/static/order_food.png" class="o-icon-img" alt="Food">Order<br>Food</div>
                <div class="o-card"><img src="/static/file_refund.png" class="o-icon-img" alt="Refund">File<br>Refund</div>
                <div class="o-card"><img src="/static/rail_madad.png" class="o-icon-img" alt="Madad">Rail<br>Madad</div>
                <div class="o-card"><img src="/static/go_to_waves.png" class="o-icon-img" alt="Waves">Go To<br>WAVES</div>
            </div>
            
            <!-- Upcoming Journey -->
            <div class="section-title">Upcoming Journey</div>
            <div class="ticket-container">
                <div class="ticket-card">
                    <div class="t-date">Mon, 20 Jul 26</div>
                    <div class="t-stations">
                        <span>MANKHURD</span>
                        <span>GHATKOPAR</span>
                    </div>
                    <div class="t-footer">
                        <span>Unreserved</span>
                        <div class="btn-group">
                            <button class="btn">Book Again</button>
                            <button class="btn" onclick="window.location.href='/ticket-view'">View Details</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Bottom Navigation -->
            <div class="bottom-nav">
                <div class="nav-item active" onclick="window.location.href='/home'"><div class="nav-icon">🏠</div>Home</div>
                <div class="nav-item" onclick="window.location.href='/bookings'"><div class="nav-icon">🎟️</div>My Bookings</div>
                <div class="nav-item"><div class="nav-icon">👤</div>You</div>
                <div class="nav-item"><div class="nav-icon">☰</div>Menu</div>
            </div>
        </div>
    </body>
    </html>
    """
@app.get("/", response_class=HTMLResponse)
async def login_screen():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RailOne - Login</title>
        <!-- PWA Links -->
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#ffffff">
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/sw.js')
                .then(() => console.log('Service Worker Registered'));
            }
        </script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: linear-gradient(to bottom, #f0f9ff 0%, #ffffff 40%); color: #1e293b; display: flex; justify-content: center; min-height: 100vh; }
            .app-container { width: 100%; max-width: 414px; padding: 60px 24px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; text-align: center; }
            
            .logo { font-size: 36px; font-weight: 800; color: #475569; margin-bottom: 50px; display: flex; align-items: center; justify-content: center; gap: 4px; }
            
            h1 { font-size: 22px; color: #334155; margin-bottom: 24px; font-weight: 700; }
            .welcome-text { font-size: 15px; color: #64748b; margin-bottom: 32px; }
            .pin-label { font-size: 14px; color: #475569; margin-bottom: 12px; }
            
            /* PIN Inputs */
            .pin-container { display: flex; gap: 10px; justify-content: center; margin-bottom: 24px; width: 100%; }
            .pin-box { width: 45px; height: 55px; border: 1px solid #bae6fd; border-radius: 12px; text-align: center; font-size: 24px; font-weight: bold; color: #1e3a8a; background: transparent; outline: none; transition: all 0.2s; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
            .pin-box:focus { border-color: #3b82f6; border-width: 2px; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
            
            /* Links */
            .link-row { width: 100%; display: flex; justify-content: space-between; font-size: 14px; font-weight: 700; color: #1e3a8a; cursor: pointer; margin-bottom: 50px; }
            
            /* Divider */
            .divider { width: 100%; display: flex; align-items: center; font-size: 14px; color: #64748b; margin-bottom: 30px; }
            .divider::before, .divider::after { content: ""; flex: 1; border-bottom: 1px dashed #cbd5e1; margin: 0 12px; }
            
            /* Biometric Section */
            .bio-row { width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
            .bio-icons { display: flex; gap: 16px; font-size: 32px; color: #1e293b; }
            
            /* Custom Toggle Switch */
            .switch { position: relative; display: inline-block; width: 52px; height: 30px; }
            .switch input { opacity: 0; width: 0; height: 0; }
            .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .3s; border-radius: 34px; }
            .slider:before { position: absolute; content: ""; height: 22px; width: 22px; left: 4px; bottom: 4px; background-color: white; transition: .3s; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
            input:checked + .slider { background-color: #3b82f6; }
            input:checked + .slider:before { transform: translateX(22px); }
            
            .bio-text { font-size: 12px; color: #64748b; line-height: 1.5; text-align: left; margin-bottom: 50px; }
            
            .diff-user { font-size: 16px; font-weight: 700; color: #1e3a8a; cursor: pointer; margin-top: auto; }
        </style>
    </head>
    <body>
        <div class="app-container">
            <div class="logo">RailOne</div>
            
            <h1>Login using mPIN</h1>
            <div class="welcome-text">Welcome Soham Khedekar!</div>
            
            <div class="pin-label">Enter mPIN below</div>
            <div class="pin-container">
                <input type="tel" maxlength="1" class="pin-box" autofocus>
                <input type="tel" maxlength="1" class="pin-box">
                <input type="tel" maxlength="1" class="pin-box">
                <input type="tel" maxlength="1" class="pin-box">
                <input type="tel" maxlength="1" class="pin-box">
                <input type="tel" maxlength="1" class="pin-box">
            </div>
            
            <div class="link-row">
                <span>Forgot Password?</span>
                <span>Reset mPIN?</span>
            </div>
            
            <div class="divider">Enable biometric ?</div>
            
            <div class="bio-row">
                <div class="bio-icons">
                    <!-- Face Scan Icon -->
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 7V5a2 2 0 0 1 2-2h2"></path>
                        <path d="M17 3h2a2 2 0 0 1 2 2v2"></path>
                        <path d="M21 17v2a2 2 0 0 1-2 2h-2"></path>
                        <path d="M7 21H5a2 2 0 0 1-2-2v-2"></path>
                        <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                        <line x1="9" y1="9" x2="9.01" y2="9"></line>
                        <line x1="15" y1="9" x2="15.01" y2="9"></line>
                    </svg>
                    <!-- Fingerprint Icon -->
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#1e293b" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4"></path>
                        <path d="M14 13.12c0 2.38 0 6.38-1 8.88"></path>
                        <path d="M17.29 21.02c.12-.6.43-2.3.5-3.02"></path>
                        <path d="M2 12a10 10 0 0 1 18-6"></path>
                        <path d="M2 16h.01"></path>
                        <path d="M21.8 16c.2-2 .131-5.354 0-6"></path>
                        <path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2"></path>
                        <path d="M8.65 22c.21-.66.45-1.32.57-2"></path>
                        <path d="M9 6.8a6 6 0 0 1 9 5.2v2"></path>
                    </svg>
                </div>
                <label class="switch">
                    <input type="checkbox">
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="bio-text">
                By enabling biometric authentication you will be able to login through your device set biometric.
            </div>
            
            <div class="diff-user">Different User?</div>
        </div>

        <script>
            // Logic to auto-advance PIN inputs and login on completion
            const inputs = document.querySelectorAll('.pin-box');
            inputs.forEach((input, index) => {
                input.addEventListener('input', (e) => {
                    if (e.target.value.length === 1) {
                        if (index < inputs.length - 1) {
                            inputs[index + 1].focus();
                        } else {
                            // Last box filled, redirect to home
                            setTimeout(() => {
                                window.location.href = '/home';
                            }, 300);
                        }
                    }
                });
                
                // Allow using Backspace to move backwards
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                        inputs[index - 1].focus();
                    }
                });
            });
        </script>
    </body>
    </html>
    """
@app.get("/bookings", response_class=HTMLResponse)
async def bookings_screen():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Bookings</title>
        <link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#0052cc">
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
        .then(() => console.log('Service Worker Registered'));
    }
</script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #f8fafc; color: #1e293b; display: flex; justify-content: center; }
            .app-container { width: 100%; max-width: 414px; position: relative; padding-bottom: 80px; background: #f8fafc; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.05); }
            
            /* Header & Tabs */
            /* Header color changed to #0052cc to match the bottom nav */
            .header { background: #0052cc; color: white; display: flex; align-items: center; padding: 16px; font-size: 18px; }
            .header-title { flex-grow: 1; padding-left: 16px; font-weight: 500; font-size: 18px; }
            .header-icon { font-size: 20px; cursor: pointer; }
            
            .tab-bar { display: flex; background: #f8fafc; padding: 16px 16px 8px 16px; }
            .tab { font-size: 14px; color: #d97706; font-weight: 600; }
            
            /* Main Card Styling */
            .booking-list { padding: 8px 16px; }
            .b-card { background: white; border: 1px solid #f97316; border-radius: 8px; display: flex; flex-direction: column; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
            
            .card-top { display: flex; padding: 16px; }
            .badge-unres { background: #e9d5ff; color: #6b21a8; writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; padding: 12px 6px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-right: 16px; display: flex; align-items: center; justify-content: center; }
            
            /* Data Grid */
            .card-content { flex-grow: 1; position: relative; }
            .refresh-icon { position: absolute; right: 0; top: 0; color: #64748b; font-size: 16px; font-weight: bold; }
            
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 8px; margin-bottom: 16px; padding-right: 16px; }
            .d-col { display: flex; flex-direction: column; gap: 2px; }
            .lbl { font-size: 12px; color: #94a3b8; }
            .val { font-size: 13px; font-weight: 700; color: #1e293b; }
            
            .route-row { display: flex; align-items: center; justify-content: space-between; margin-top: 8px; width: 100%; }
            .station { font-size: 14px; font-weight: 700; color: #1e293b; }
            .dist { font-size: 11px; color: #94a3b8; padding: 0 4px; }
            
            /* Divider & Cutouts */
            .divider { height: 1px; border-top: 1px dashed #cbd5e1; width: 100%; position: relative; }
            .b-card::before, .b-card::after { content: ''; position: absolute; bottom: 44px; width: 18px; height: 18px; background: #f8fafc; border: 1px solid #f97316; border-radius: 50%; z-index: 10; }
            .b-card::before { left: -10px; clip-path: inset(0 0 0 50%); }
            .b-card::after { right: -10px; clip-path: inset(0 50% 0 0); }
            
            /* Action Buttons */
            .card-actions { display: flex; justify-content: center; align-items: center; padding: 14px; gap: 24px; font-size: 15px; font-weight: 600; }
            .btn-txt { color: #1e293b; cursor: pointer; }
            .btn-txt.blue { color: #2563eb; }
            .sep { color: #cbd5e1; font-weight: 300; }
            
            /* Bottom Nav */
            .bottom-nav { position: fixed; bottom: 0; width: 100%; max-width: 414px; background: #0052cc; color: white; display: flex; justify-content: space-around; padding: 12px 0 20px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
            .nav-item { display: flex; flex-direction: column; align-items: center; font-size: 11px; opacity: 0.6; cursor: pointer; }
            .nav-item.active { opacity: 1; font-weight: 600; }
            .nav-icon { font-size: 22px; margin-bottom: 4px; }
        </style>
    </head>
    <body>
        <div class="app-container">
            <div class="header">
                <span class="header-icon" onclick="window.location.href='/home'">←</span>
                <div class="header-title">My Bookings</div>
                <span class="header-icon" style="font-size: 16px;">⇅</span>
            </div>
            
            <div class="tab-bar">
                <div class="tab">Upcoming (1)</div>
            </div>
            
            <div class="booking-list">
                <div class="b-card">
                    <div class="card-top">
                        <div class="badge-unres">Unreserved</div>
                        <div class="card-content">
                            <div class="refresh-icon">↻</div>
                            <div class="grid-2">
                                <div class="d-col">
                                    <span class="lbl">Ticket Type</span>
                                    <!-- CHANGE THIS TICKET TYPE -->
                                    <span class="val">QUARTERLY</span>
                                </div>
                                <div class="d-col">
                                    <span class="lbl">UTS: X0F7EES082</span>
                                </div>
                                <div></div> 
                                <div class="d-col">
                                    <span class="lbl">Booking Date</span>
                                    <!-- CHANGE THIS DATE -->
                                    <span class="lbl" style="color: #1e293b; font-weight: 500;">Mon, 20 Jul 26</span>
                                </div>
                            </div>
                            <div class="route-row">
                                <span class="station">MANKHURD</span>
                                <span class="dist">— 10 km —</span>
                                <span class="station">GHATKOPAR</span>
                            </div>
                        </div>
                    </div>
                    <div class="divider"></div>
                    <div class="card-actions">
                        <span class="btn-txt">Book Again</span>
                        <span class="sep">|</span>
                        <span class="btn-txt blue" onclick="window.location.href='/ticket-view'">View Details</span>
                    </div>
                </div>
            </div>
            
            <div class="bottom-nav">
                <div class="nav-item" onclick="window.location.href='/home'"><div class="nav-icon">🏠</div>Home</div>
                <div class="nav-item active" onclick="window.location.href='/bookings'"><div class="nav-icon">🎟️</div>My Bookings</div>
                <div class="nav-item"><div class="nav-icon">👤</div>You</div>
                <div class="nav-item"><div class="nav-icon">☰</div>Menu</div>
            </div>
        </div>
    </body>
    </html>
    """
@app.get("/ticket-view", response_class=HTMLResponse)
async def view_ticket():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Booking Details</title>

        <!-- PWA Links -->
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#0052cc">
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/sw.js')
                .then(() => console.log('Service Worker Registered'));
            }
        </script>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>

        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #e2e8f0; display: flex; justify-content: center; }
            .app-container { width: 100%; max-width: 414px; background: white; min-height: 100vh; box-shadow: 0 0 20px rgba(0,0,0,0.05); display: flex; flex-direction: column; }
            
            /* Header */
            .header { background: #0052cc; color: white; display: flex; align-items: center; padding: 12px 16px; gap: 16px; }
            .back-btn { font-size: 24px; cursor: pointer; padding-right: 8px; }
            .header-titles { flex-grow: 1; display: flex; flex-direction: column; }
            .h-title { font-size: 18px; font-weight: 500; }
            .h-sub { font-size: 11px; opacity: 0.8; margin-top: 2px; }
            .menu-btn { font-size: 24px; }
            
            /* Welcome Strip */
            .welcome-strip { background: #f8fafc; padding: 10px 16px; font-size: 12px; color: #64748b; border-bottom: 1px solid #e2e8f0; text-align: center; }
            
            /* Dynamic Banner */
            .dynamic-banner { 
                background-color: #000000;
                background-image: 
                    linear-gradient(45deg, #1a1a1a 25%, transparent 25%, transparent 75%, #1a1a1a 75%, #1a1a1a), 
                    linear-gradient(45deg, #1a1a1a 25%, transparent 25%, transparent 75%, #1a1a1a 75%, #1a1a1a);
                background-size: 20px 20px;
                background-position: 0 0, 10px 10px;
                color: white; padding: 24px 16px; text-align: center; position: relative;
                border-top: 18px solid #111; border-bottom: 18px solid #111;
                box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
            }
            
            /* English watermark on the left (bottom to top, single instance) */
            .dynamic-banner::before { 
                content: 'INDIAN RAILWAYS'; 
                position: absolute; left: 8px; top: 0; bottom: 0; 
                writing-mode: vertical-rl; transform: rotate(180deg);
                font-size: 16px; font-weight: bold; color: rgba(255,255,255,0.4); 
                letter-spacing: 3px; display: flex; align-items: center; justify-content: center;
            }
            
            /* Hindi watermark on the right (top to bottom, single instance) */
            .dynamic-banner::after { 
                content: 'भारतीय रेल'; 
                position: absolute; right: 8px; top: 0; bottom: 0; 
                writing-mode: vertical-rl; 
                font-size: 18px; font-weight: bold; color: rgba(255,255,255,0.4); 
                letter-spacing: 3px; display: flex; align-items: center; justify-content: center;
            }
            
            .d-text { font-size: 13px; color: #cbd5e1; margin-bottom: 4px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
            .timer { 
                font-size: 54px; font-weight: 800; color: #ff3b30; 
                margin: 4px 0 12px; font-family: monospace; letter-spacing: 2px;
                text-shadow: 0 0 8px rgba(255, 59, 48, 0.4); 
            }
            .d-date { color: #f59e0b; font-size: 22px; font-weight: 800; margin-bottom: 4px; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
            .r-code { font-size: 13px; font-weight: bold; margin: 8px 0; letter-spacing: 1px; }
            
            /* Data Grid */
            .ticket-data { background: white; padding: 20px 16px 12px; display: flex; flex-direction: column; gap: 16px; }
            .data-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
            .data-group { display: flex; flex-direction: column; gap: 4px; }
            .d-lbl { color: #475569; font-size: 11px; }
            .d-val { color: #0f172a; font-weight: 700; font-size: 14px; }
            .d-val-active { color: #16a34a; font-weight: bold; font-size: 12px; }
            .via-row { display: flex; gap: 8px; font-size: 13px; font-weight: 600; color: #0f172a; align-items: center; padding: 8px 0; border-top: 1px solid rgba(0,0,0,0.05); border-bottom: 1px solid rgba(0,0,0,0.05); margin: 4px 0; }
            
            /* Bottom Section Layout */
            .bottom-section { display: flex; flex-direction: column; align-items: center; padding: 0 16px 24px; background: white; }
            
            /* Pink Note Box */
            .pink-note { background: #ffe4e6; color: #e11d48; padding: 12px 16px; border-radius: 8px; font-size: 12px; text-align: center; width: 100%; box-sizing: border-box; margin: 16px 0; line-height: 1.4; }
            
            /* Upgrade Button */
            .upgrade-btn { background: #2563eb; color: white; border: none; padding: 14px 24px; border-radius: 30px; font-weight: 600; font-size: 14px; width: 90%; margin-bottom: 24px; cursor: pointer; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2); }
            
            /* QR Section */
            #qrcode { margin-bottom: 24px; }
            
            /* Footer Rules */
            .footer-rules { background: #f1f5f9; padding: 20px 16px; font-size: 12px; color: #475569; line-height: 1.6; border-top: 1px solid #e2e8f0; }
            .footer-rules strong { color: #1e293b; font-size: 14px; display: block; margin-bottom: 8px; }
            .footer-rules p { margin: 0 0 12px 0; }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Header -->
            <div class="header">
                <span class="back-btn" onclick="window.location.href='/bookings'">←</span>
                <div class="header-titles">
                    <div class="h-title">Booking Details</div>
                    <div class="h-sub">Mobile: 8169150830</div>
                </div>
                <span class="menu-btn">☰</span>
            </div>
            
            <div class="welcome-strip">
                Thank You Soham Khedekar, Happy Journey !
            </div>
            
            <!-- Dynamic Banner -->
            <div class="dynamic-banner">
                <div class="d-text">Dynamic preview will close in</div>
                <div class="timer" id="clock">04:56</div>
                <div class="d-text">Ticket Booking Date & Time</div>
                <div class="d-date">20 Sep 2026, 13:03</div>
                <div class="r-code">R17683</div>
                <div class="d-text">Ticket is Non-Transferable</div>
            </div>
            
            <!-- Data Grid -->
            <div class="ticket-data">
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Season Ticket</span><span class="d-val">X0F7EES082</span></div>
                    <div class="data-group"><span class="d-val-active" style="text-align: right;">● ACTIVE</span></div>
                </div>
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Source</span><span class="d-val">MANKHURD</span></div>
                    <div class="data-group"><span class="d-lbl">Destination</span><span class="d-val">GHATKOPAR</span></div>
                </div>
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Distance</span><span class="d-val">10 km</span></div>
                    <div class="data-group"><span class="d-lbl">Booked on</span><span class="d-val">20/09/2026 13:03:47</span></div>
                </div>
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Ticket Type</span><span class="d-val">QUARTERLY</span></div>
                    <div class="data-group"><span class="d-lbl">Train Types</span><span class="d-val">ORDINARY</span></div>
                </div>
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Class</span><span class="d-val">FIRST</span></div>
                    <div class="data-group"><span class="d-lbl">Fare</span><span class="d-val">925.00</span></div>
                </div>
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Valid From</span><span class="d-val">20/09/2026</span></div>
                    <div class="data-group"><span class="d-lbl">Valid Upto</span><span class="d-val">19/12/2026</span></div>
                </div>
                <div class="via-row"><span style="font-size: 16px; font-weight:normal;">⇄</span> Via: 1RT>>CLA</div>
                <div class="data-row">
                    <div class="data-group"><span class="d-lbl">Name</span><span class="d-val">Soham Khedekar</span></div>
                    <div class="data-group"><span class="d-lbl">Age</span><span class="d-val">19 years</span></div>
                </div>
                <div class="data-row" style="padding-bottom: 8px;">
                    <div class="data-group"><span class="d-lbl">ID Type*</span><span class="d-val">N/A</span></div>
                    <div class="data-group"><span class="d-lbl">ID Number</span><span class="d-val">PQQPK5756L</span></div>
                </div>
            </div>
            
            <!-- Bottom Section -->
            <div class="bottom-section">
                <div class="pink-note">
                    Note: This ticket is non refundable. Ticket is stored locally on the device. Please do not change your handset or perform factory reset.
                </div>
                
                <button class="upgrade-btn">Upgrade to Superfast</button>
                
                <div id="qrcode"></div>
            </div>
            
            <!-- Gray Footer -->
            <div class="footer-rules">
                <strong>Do you know?</strong>
                <p>IR recovers only 57% of cost of travel on an average.</p>
                <p>This ticket is booked on a personal user ID. It's sale/purchase is an offence u/s 143 of the Railways Act, 1989</p>
                <p style="margin-bottom: 0;">For enquiry and integrated railway helpline, please dial 139.</p>
            </div>
        </div>

        <script>
            // Generate QR Code
            new QRCode(document.getElementById("qrcode"), {
                text: "X0F7EES082-SOHAM-KHEDEKAR-MANKHURD-GHATKOPAR",
                width: 140,
                height: 140,
                colorDark : "#000000",
                colorLight : "#ffffff"
            });

            // Countdown Timer Logic
            let seconds = 296; // 04:56
            setInterval(() => {
                seconds--;
                if(seconds < 0) seconds = 300;
                let m = Math.floor(seconds / 60).toString().padStart(2, '0');
                let s = (seconds % 60).toString().padStart(2, '0');
                document.getElementById('clock').innerText = m + ':' + s;
            }, 1000);
        </script>
    </body>
    </html>
    """
