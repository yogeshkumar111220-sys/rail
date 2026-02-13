import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import random

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="🦂",
    layout="wide",
    initial_sidebar_state="collapsed"
)

custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    * { box-sizing: border-box; margin: 0; padding: 0; }

    /* ── BACKGROUND WALLPAPER ── */
    .stApp {
        min-height: 100vh;
        background:
            linear-gradient(rgba(0,0,0,0.72), rgba(0,0,0,0.78)),
            url('https://i.postimg.cc/TYhXd0gG/d0a72a8cea5ae4978b21e04a74f0b0ee.jpg') center/cover no-repeat fixed;
    }

    /* animated grid overlay */
    .stApp::before {
        content: '';
        position: fixed; top:0; left:0; right:0; bottom:0;
        background-image:
            linear-gradient(rgba(120,0,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(120,0,255,0.06) 1px, transparent 1px);
        background-size: 48px 48px;
        z-index: 0; pointer-events: none;
        animation: gridDrift 25s linear infinite;
    }
    @keyframes gridDrift { 0%{transform:translateY(0)} 100%{transform:translateY(48px)} }

    /* ── MAIN CONTAINER ── */
    .main .block-container {
        background: rgba(4,0,18,0.82);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 20px;
        padding: 1.6rem 2.2rem 2.5rem;
        border: 1px solid rgba(130,0,255,0.30);
        box-shadow:
            0 0 80px rgba(100,0,255,0.18),
            0 0 200px rgba(255,0,100,0.06),
            inset 0 1px 0 rgba(255,255,255,0.04);
        margin-top: 0.6rem;
        position: relative; z-index: 1;
    }

    /* ── HEADER ── */
    .hdr { text-align:center; padding:1.2rem 1rem 0.5rem; }
    .hdr::after {
        content:''; display:block; height:2px; margin-top:1.1rem;
        background:linear-gradient(90deg,transparent,#7b00ff,#ff0080,#00c8ff,transparent);
        animation:lineGlow 3s ease-in-out infinite;
    }
    @keyframes lineGlow { 0%,100%{opacity:.55} 50%{opacity:1;box-shadow:0 0 18px rgba(255,0,128,.7)} }

    .hdr-title {
        font-family:'Orbitron',sans-serif; font-weight:900; font-size:2.5rem;
        letter-spacing:5px; text-transform:uppercase;
        background:linear-gradient(135deg,#b400ff,#ff0080,#00c8ff);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        filter:drop-shadow(0 0 18px rgba(180,0,255,.55));
        animation:hdrPulse 4s ease-in-out infinite;
    }
    @keyframes hdrPulse {
        0%,100%{filter:drop-shadow(0 0 14px rgba(180,0,255,.5))}
        50%{filter:drop-shadow(0 0 28px rgba(255,0,128,.8))}
    }
    .hdr-sub {
        font-family:'Share Tech Mono',monospace; font-size:0.78rem;
        color:rgba(170,0,255,.75); letter-spacing:3px; text-transform:uppercase; margin-top:0.35rem;
    }

    /* ── STATUS METRICS ── */
    .metrics { display:flex; gap:10px; margin:1.1rem 0; flex-wrap:wrap; }
    .mbox {
        flex:1; min-width:100px;
        background:rgba(8,0,25,0.75); border:1px solid rgba(110,0,255,0.38);
        border-radius:12px; padding:0.8rem 0.5rem; text-align:center;
    }
    .mval {
        font-family:'Orbitron',sans-serif; font-size:1.3rem; font-weight:900;
        background:linear-gradient(135deg,#b400ff,#ff0080);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        display:block; line-height:1.2;
    }
    .mlbl {
        font-family:'Share Tech Mono',monospace; font-size:0.56rem;
        color:rgba(160,90,255,.55); letter-spacing:2px; text-transform:uppercase; margin-top:4px; display:block;
    }
    .run { color:#00ff88!important; -webkit-text-fill-color:#00ff88!important; background:none!important;
           text-shadow:0 0 10px rgba(0,255,136,.55); animation:blink 1.6s ease-in-out infinite; }
    .stp { color:#ff4444!important; -webkit-text-fill-color:#ff4444!important; background:none!important; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.5} }

    /* ── BUTTONS ── */
    .stButton > button {
        background:linear-gradient(135deg,rgba(110,0,255,.28),rgba(255,0,110,.22)) !important;
        color:#fff !important; border:1px solid rgba(110,0,255,.55) !important;
        border-radius:10px !important; padding:0.65rem 1rem !important;
        font-family:'Orbitron',sans-serif !important; font-weight:700 !important;
        font-size:0.68rem !important; letter-spacing:2px !important;
        text-transform:uppercase !important; width:100% !important;
        transition:all .28s ease !important;
    }
    .stButton > button:hover {
        background:linear-gradient(135deg,rgba(110,0,255,.6),rgba(255,0,110,.55)) !important;
        border-color:#ff0080 !important; box-shadow:0 0 18px rgba(255,0,128,.4) !important;
        transform:translateY(-1px) !important;
    }
    .stButton > button:disabled { opacity:.28 !important; transform:none !important; }

    /* ── INPUTS ── */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input {
        background:rgba(8,0,25,.9) !important; border:1px solid rgba(110,0,255,.48) !important;
        border-radius:9px !important; color:#ddb8ff !important;
        padding:.65rem .95rem !important;
        font-family:'Share Tech Mono',monospace !important; font-size:.86rem !important;
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {
        border-color:#ff0080 !important; box-shadow:0 0 0 2px rgba(255,0,128,.18) !important; outline:none !important;
    }
    .stTextArea>div>div>textarea {
        background:rgba(8,0,25,.9) !important; border:1px solid rgba(110,0,255,.48) !important;
        border-radius:9px !important; color:#ddb8ff !important;
        font-family:'Share Tech Mono',monospace !important; font-size:.82rem !important;
    }
    .stTextArea>div>div>textarea:focus {
        border-color:#ff0080 !important; box-shadow:0 0 0 2px rgba(255,0,128,.18) !important;
    }

    /* ── LABELS ── */
    label, .stTextInput label, .stTextArea label, .stNumberInput label,
    [data-testid="stFileUploader"] label {
        color:rgba(190,90,255,.9) !important;
        font-family:'Orbitron',sans-serif !important;
        font-size:.63rem !important; font-weight:700 !important;
        letter-spacing:1.8px !important; text-transform:uppercase !important;
    }

    /* ── RADIO ── */
    .stRadio>div {
        background:rgba(8,0,25,.55) !important; border-radius:9px !important;
        padding:.6rem .9rem !important; border:1px solid rgba(110,0,255,.28) !important;
    }
    .stRadio label {
        color:rgba(190,90,255,.88) !important; font-family:'Share Tech Mono',monospace !important;
        font-size:.85rem !important; letter-spacing:.5px !important; text-transform:none !important;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] {
        background:rgba(8,0,25,.65) !important;
        border:1.5px dashed rgba(110,0,255,.45) !important;
        border-radius:10px !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color:rgba(255,0,128,.6) !important;
    }

    /* ── PILL CHIPS ── */
    .pill {
        display:inline-block; background:rgba(110,0,255,.15);
        border:1px solid rgba(110,0,255,.4); border-radius:6px;
        padding:.35rem .7rem; margin:.25rem; color:rgba(180,90,255,.88);
        font-family:'Share Tech Mono',monospace; font-size:.72rem;
        letter-spacing:.5px;
    }

    /* ── HR ── */
    hr {
        border:0; height:1px; margin:1.5rem 0;
        background:linear-gradient(90deg,transparent,rgba(110,0,255,.45),transparent);
    }

    /* ── CONSOLE LOGS ── */
    .console-wrap {
        background:rgba(0,0,0,0.7); border:1px solid rgba(110,0,255,.42);
        border-radius:10px; overflow:hidden; margin-top:.8rem;
    }
    .console-bar {
        background:rgba(110,0,255,.18); padding:.55rem .8rem;
        font-family:'Share Tech Mono',monospace; font-size:.65rem;
        color:rgba(180,90,255,.75); letter-spacing:1px; display:flex; align-items:center;
    }
    .cd {
        width:9px; height:9px; border-radius:50%; display:inline-block; margin-right:5px;
    }
    .cr { background:#ff4444; }
    .cy { background:#ffaa00; }
    .cg { background:#00ff88; }
    .console-out {
        padding:.7rem .9rem; max-height:320px; overflow-y:auto;
        font-family:'Share Tech Mono',monospace; font-size:.74rem; line-height:1.5;
        color:rgba(200,200,255,.72);
    }
    .lg { padding:.18rem 0; }
    .lg-ok  { color:#00ff88; }
    .lg-err { color:#ff4444; }
    .lg-inf { color:rgba(0,200,255,.85); }

    /* ── FOOTER ── */
    .ftr {
        text-align:center; margin-top:2rem; padding:1rem;
        font-family:'Share Tech Mono',monospace; font-size:.62rem;
        color:rgba(180,90,255,.45); letter-spacing:2px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════
if 'cfg' not in st.session_state:
    st.session_state.cfg = {
        'chat_id': '',
        'name_prefix': '',
        'delay': 30,
        'cookies': '',
        'messages': ''
    }

if 'astate' not in st.session_state:
    class AutomationState:
        def __init__(self):
            self.running = False
            self.message_count = 0
            self.logs = []
            self.rot_idx = 0
    st.session_state.astate = AutomationState()

if 'cookie_mode' not in st.session_state:
    st.session_state.cookie_mode = 'single'

if 'single_cookie' not in st.session_state:
    st.session_state.single_cookie = ''

if 'multi_cookies' not in st.session_state:
    st.session_state.multi_cookies = []

if 'msg_list' not in st.session_state:
    st.session_state.msg_list = []

cfg = st.session_state.cfg
astate = st.session_state.astate

# ══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════
def lg(msg, s=None):
    """Add log message"""
    if s is None:
        s = st.session_state.astate
    ts = time.strftime('%H:%M:%S')
    s.logs.append(f'[{ts}] {msg}')

def log_cls(log):
    """Return log CSS class based on content"""
    if '✅' in log or 'sent' in log.lower() or 'success' in log.lower():
        return 'lg-ok'
    elif '❌' in log or 'error' in log.lower() or 'fail' in log.lower():
        return 'lg-err'
    return 'lg-inf'

def get_chrome_options():
    """Configure Chrome options for cloud deployment - BALANCED VERSION"""
    options = Options()
    
    # Essential headless settings
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Basic optimization
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1280,720')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    
    # Memory optimization
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-sync')
    options.add_argument('--no-first-run')
    options.add_argument('--password-store=basic')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Logging
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    
    # IMPORTANT: ENABLE IMAGES AND CSS (otherwise message box won't appear!)
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'profile.managed_default_content_settings.images': 1,  # ENABLE images
        'profile.managed_default_content_settings.stylesheets': 1,  # ENABLE CSS
        'profile.managed_default_content_settings.cookies': 1,
        'profile.managed_default_content_settings.javascript': 1,
        'profile.managed_default_content_settings.popups': 2,
    }
    options.add_experimental_option('prefs', prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    return options

def parse_cookies(cookie_string):
    """Parse cookie string into list of cookie dictionaries"""
    if not cookie_string or not cookie_string.strip():
        return []
    
    cookies = []
    parts = [p.strip() for p in cookie_string.split(';') if '=' in p]
    
    for part in parts:
        try:
            key, value = part.split('=', 1)
            
            # Add cookie for BOTH facebook.com AND messenger.com
            # This ensures cookies work on both domains
            cookies.append({
                'name': key.strip(),
                'value': value.strip(),
                'domain': '.messenger.com',  # Messenger domain
                'path': '/',
                'secure': True
            })
            cookies.append({
                'name': key.strip(),
                'value': value.strip(),
                'domain': '.facebook.com',  # Facebook domain (backup)
                'path': '/',
                'secure': True
            })
        except:
            continue
    
    return cookies

def send_message(driver, message, chat_id, name_prefix, s):
    """Send a single message to the chat - OPTIMIZED VERSION"""
    try:
        # USE MESSENGER.COM (lighter and more reliable than facebook.com)
        url = f'https://www.messenger.com/t/{chat_id}'
        lg(f'📍 Opening chat: {chat_id[:15]}...', s)
        driver.get(url)
        
        # Wait longer for Messenger to load (needs time to render)
        lg('⏳ Waiting for page to load (15 seconds)...', s)
        time.sleep(15)  # Increased wait time
        
        # Log current URL for debugging
        current_url = driver.current_url
        lg(f'🔗 Current URL: {current_url[:50]}...', s)
        
        # Check if redirected to login
        if 'login' in current_url.lower():
            lg('❌ COOKIE EXPIRED! Redirected to login page!', s)
            lg('🔴 Get fresh cookies from messenger.com and try again!', s)
            return False
        
        # Find message input box - MESSENGER-SPECIFIC SELECTORS
        input_selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[aria-label="Message"]',
            'div[aria-label="Type a message"]',
            'div[aria-placeholder="Aa"]',
            'div[contenteditable="true"]',
            'textarea',
        ]
        
        message_box = None
        lg('🔍 Searching for message input box...', s)
        
        # Try each selector with proper wait
        for i, selector in enumerate(input_selectors):
            try:
                lg(f'  Try {i+1}/6: {selector[:35]}...', s)
                
                # Wait for elements to appear
                elements = WebDriverWait(driver, 8).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                
                lg(f'  Found {len(elements)} elements', s)
                
                # Check which one is visible and enabled
                for elem in elements:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            message_box = elem
                            lg(f'✅ Message box found!', s)
                            break
                    except:
                        continue
                
                if message_box:
                    break
                    
            except Exception as e:
                lg(f'  Failed: {str(e)[:25]}', s)
                continue
        
        if not message_box:
            lg('❌ Message box not found!', s)
            lg('💡 Possible solutions:', s)
            lg('  1. Get FRESH cookies from messenger.com', s)
            lg('  2. Verify chat ID is correct', s)
            lg('  3. Check if you have access to this chat', s)
            lg('  4. Wait 24 hours if you sent too many messages', s)
            return False
        
        # Prepare final message
        final_msg = f"{name_prefix} {message}".strip()
        
        # Click message box
        lg(f'⌨️  Typing: {final_msg[:30]}...', s)
        try:
            # Scroll into view first
            driver.execute_script("arguments[0].scrollIntoView(true);", message_box)
            time.sleep(0.5)
            
            # Click the message box
            message_box.click()
            time.sleep(1)
            
            # Type the message (all at once for speed)
            message_box.send_keys(final_msg)
            lg('✓ Typed successfully', s)
            time.sleep(1)
            
        except Exception as e:
            lg(f'❌ Typing failed: {str(e)[:50]}', s)
            return False
        
        # Send message via Enter key (fastest method)
        try:
            message_box.send_keys(Keys.RETURN)
            lg('✅ MESSAGE SENT!', s)
            time.sleep(2)
            return True
        except Exception as e:
            lg(f'⚠️  Enter key failed: {str(e)[:30]}, trying send button...', s)
        
        # Fallback: Find and click send button
        send_selectors = [
            'div[aria-label="Send"]',
            'div[aria-label="Press Enter to send"]',
            'button[aria-label="Send"]',
            'div[role="button"]',
        ]
        
        for selector in send_selectors:
            try:
                send_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                send_btn.click()
                lg('✅ MESSAGE SENT via button!', s)
                time.sleep(2)
                return True
            except:
                continue
        
        lg('❌ Could not send message', s)
        return False
            
    except Exception as e:
        lg(f'❌ Error: {str(e)[:80]}', s)
        return False
        
        # Find and click send button
        send_selectors = [
            'div[aria-label*="Send" i]',
            'div[aria-label*="Press enter" i]',
            'button[aria-label*="Send" i]',
            'div[role="button"][tabindex="0"]',
            'div[type="submit"]',
            'svg[aria-label*="Send" i]'
        ]
        
        send_button = None
        lg('🔍 Searching for send button...', s)
        
        for i, selector in enumerate(send_selectors):
            try:
                lg(f'  Trying selector {i+1}/{len(send_selectors)}: {selector[:40]}...', s)
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if buttons:
                    lg(f'  Found {len(buttons)} buttons', s)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            send_button = btn
                            lg(f'✅ Send button found', s)
                            break
                
                if send_button:
                    break
                    
            except Exception as e:
                lg(f'  Button selector failed: {str(e)[:30]}', s)
                continue
        
        if send_button:
            try:
                send_button.click()
                time.sleep(random.uniform(1, 2))
                lg(f'✅ Message sent: {final_msg[:50]}...', s)
                return True
            except Exception as e:
                lg(f'❌ Click failed: {str(e)[:50]}', s)
                return False
        else:
            lg('❌ Could not find send button', s)
            return False
            
    except TimeoutException:
        lg('❌ Timeout waiting for page elements', s)
        return False
    except Exception as e:
        lg(f'❌ Error sending message: {str(e)[:100]}', s)
        import traceback
        lg(f'📝 Full error: {traceback.format_exc()[:200]}', s)
        return False

def send_loop(config, s, pid='MAIN'):
    """Main automation loop"""
    driver = None
    try:
        # Setup Chrome
        lg(f'{pid}: Initializing Chrome...', s)
        options = get_chrome_options()
        
        try:
            driver = webdriver.Chrome(options=options)
            lg(f'{pid}: ✓ Chrome started', s)
        except Exception as e:
            lg(f'{pid}: ❌ Chrome init failed: {str(e)[:100]}', s)
            return
        
        # Load MESSENGER.COM and set cookies (lighter than facebook.com)
        lg(f'{pid}: Loading Messenger...', s)
        driver.get('https://www.messenger.com')
        time.sleep(5)
        
        # Parse and add cookies
        cookies = parse_cookies(config.get('cookies', ''))
        if cookies:
            added_count = 0
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                    added_count += 1
                except Exception as e:
                    # Silently skip domain errors (some cookies may not work on messenger.com)
                    if 'invalid cookie domain' not in str(e).lower():
                        lg(f'{pid}: Cookie error: {str(e)[:50]}', s)
            lg(f'{pid}: ✓ Added {added_count} cookies successfully', s)
            
            # Refresh to apply cookies
            driver.refresh()
            time.sleep(3)
            
            # VERIFY LOGIN
            try:
                current_url = driver.current_url
                page_source = driver.page_source[:500]
                
                # Check if logged in
                if 'login' in current_url.lower() or 'login' in page_source.lower():
                    lg(f'{pid}: ❌ NOT LOGGED IN! Cookie expired or invalid!', s)
                    lg(f'{pid}: Current URL: {current_url[:60]}', s)
                    lg(f'{pid}: 🔴 SOLUTION: Get fresh cookies from Facebook!', s)
                    return
                else:
                    lg(f'{pid}: ✅ Login verified! Cookie working!', s)
                    
            except Exception as e:
                lg(f'{pid}: ⚠️ Could not verify login: {str(e)[:50]}', s)
        else:
            lg(f'{pid}: ❌ No cookies provided! Cannot proceed!', s)
            return
        
        # Get messages
        messages = [m.strip() for m in config.get('messages', '').split('\n') if m.strip()]
        if not messages:
            lg(f'{pid}: ❌ No messages configured', s)
            return
        
        chat_id = config.get('chat_id', '')
        if not chat_id:
            lg(f'{pid}: ❌ No chat ID configured', s)
            return
        
        # VERIFY CHAT ID FORMAT
        if not chat_id.isdigit() or len(chat_id) < 10:
            lg(f'{pid}: ⚠️ WARNING: Chat ID looks invalid: {chat_id}', s)
            lg(f'{pid}: Expected format: 15-digit number (e.g., 123456789012345)', s)
        
        name_prefix = config.get('name_prefix', '')
        delay = config.get('delay', 30)
        
        lg(f'{pid}: 🚀 Starting message loop...', s)
        lg(f'{pid}: 📋 {len(messages)} messages loaded', s)
        lg(f'{pid}: ⏱️  Delay: {delay}s', s)
        
        # Message sending loop
        while s.running:
            # Get next message (rotate)
            msg = messages[s.rot_idx % len(messages)]
            s.rot_idx += 1
            
            lg(f'{pid}: → Sending message #{s.message_count + 1}', s)
            
            # Send message with timeout
            try:
                success = send_message(driver, msg, chat_id, name_prefix, s)
            except Exception as e:
                lg(f'{pid}: ❌ Send failed with error: {str(e)[:100]}', s)
                success = False
            
            if success:
                s.message_count += 1
                lg(f'{pid}: ✅ Total sent: {s.message_count}', s)
            else:
                lg(f'{pid}: ⚠️ Message sending failed, will retry next cycle', s)
            
            # Wait for next message
            if s.running:
                lg(f'{pid}: ⏸️  Waiting {delay}s...', s)
                for _ in range(delay):
                    if not s.running:
                        break
                    time.sleep(1)
        
        lg(f'{pid}: 🛑 Automation stopped', s)
        
    except Exception as e:
        lg(f'{pid}: ❌ Fatal error: {str(e)[:150]}', s)
        import traceback
        lg(f'{pid}: 📝 Traceback: {traceback.format_exc()[:300]}', s)
    finally:
        if driver:
            try:
                driver.quit()
                lg(f'{pid}: Browser closed', s)
            except:
                pass

def run_multi(cfgs, s):
    """Run multiple cookie sessions"""
    ts = [threading.Thread(target=send_loop, args=(c, s, f'COOKIE-{i+1}'), daemon=True) for i, c in enumerate(cfgs)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()

def start_auto(config):
    """Start automation"""
    s = st.session_state.astate
    if s.running:
        return
    
    s.running = True
    s.message_count = 0
    s.logs = []
    s.rot_idx = 0
    lg('🚀 Automation starting...', s)
    
    if st.session_state.cookie_mode == 'multiple' and st.session_state.multi_cookies:
        cfgs = [{**config, 'cookies': ck} for ck in st.session_state.multi_cookies]
        t = threading.Thread(target=run_multi, args=(cfgs, s), daemon=True)
    else:
        t = threading.Thread(target=send_loop, args=(config, s), daemon=True)
    t.start()

def stop_auto():
    """Stop automation"""
    st.session_state.astate.running = False
    lg('⚠️ Stop requested.', st.session_state.astate)

# ══════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="hdr">
    <div class="hdr-title">YKTI RAWAT</div>
    <div class="hdr-sub">PREMIUM E2EE OFFLINE CONVO SYSTEM</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  STATUS BAR
# ══════════════════════════════════════════════
is_run = astate.running
scls = 'run' if is_run else 'stp'
stxt = 'RUNNING' if is_run else 'STOPPED'
cid_disp = (cfg['chat_id'][:10] + '…') if cfg['chat_id'] and len(cfg['chat_id']) > 10 else (cfg['chat_id'] or 'NOT SET')
ck_disp = f"{len(st.session_state.multi_cookies)} COOKIES" if st.session_state.cookie_mode == 'multiple' else ("SET" if st.session_state.single_cookie.strip() else "NONE")
mc_cnt = len([m for m in cfg['messages'].split('\n') if m.strip()]) if cfg['messages'] else 0

st.markdown(f"""
<div class="metrics">
    <div class="mbox"><span class="mval">{astate.message_count}</span><span class="mlbl">SENT</span></div>
    <div class="mbox"><span class="mval {scls}">{stxt}</span><span class="mlbl">STATUS</span></div>
    <div class="mbox"><span class="mval" style="font-size:.88rem;">{cid_disp}</span><span class="mlbl">CHAT ID</span></div>
    <div class="mbox"><span class="mval" style="font-size:.88rem;">{ck_disp}</span><span class="mlbl">COOKIE</span></div>
    <div class="mbox"><span class="mval" style="font-size:.88rem;">{mc_cnt}</span><span class="mlbl">MESSAGES</span></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  START / STOP / REFRESH BUTTONS
# ══════════════════════════════════════════════
b1, b2, b3 = st.columns([2, 2, 1], gap="small")
with b1:
    if st.button("START AUTOMATION", key="start_btn", disabled=is_run or not cfg['chat_id'], use_container_width=True):
        start_auto(cfg)
        st.success("Automation started!")
        st.rerun()
with b2:
    if st.button("STOP AUTOMATION", key="stop_btn", disabled=not is_run, use_container_width=True):
        stop_auto()
        st.warning("Stop signal sent!")
        st.rerun()
with b3:
    if st.button("REFRESH", key="ref_btn", use_container_width=True):
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  PANEL 1 — TARGET SETTINGS
# ══════════════════════════════════════════════
with st.expander("TARGET SETTINGS", expanded=True):
    c1, c2, c3 = st.columns([2, 2, 1], gap="medium")
    with c1:
        v_chatid = st.text_input("CHAT / E2EE ID", value=cfg['chat_id'], placeholder="1362400298935018")
    with c2:
        v_prefix = st.text_input("NAME PREFIX", value=cfg['name_prefix'], placeholder="[YKTI RAWAT]")
    with c3:
        v_delay = st.number_input("DELAY (SEC)", min_value=1, max_value=300, value=cfg['delay'])
    # auto-save on change
    st.session_state.cfg['chat_id'] = v_chatid
    st.session_state.cfg['name_prefix'] = v_prefix
    st.session_state.cfg['delay'] = int(v_delay)

# ══════════════════════════════════════════════
#  PANEL 2 — COOKIE CONFIG
# ══════════════════════════════════════════════
with st.expander("COOKIE CONFIG", expanded=False):
    ck_mode = st.radio("COOKIE MODE",
                       ["Single Cookie", "Multiple Cookies (Upload TXT)"],
                       index=0 if st.session_state.cookie_mode == 'single' else 1,
                       horizontal=True)
    st.session_state.cookie_mode = 'single' if ck_mode == "Single Cookie" else 'multiple'

    if st.session_state.cookie_mode == 'single':
        sc = st.text_area("PASTE YOUR FACEBOOK COOKIE", value=st.session_state.single_cookie,
                          placeholder="c_user=xxxx; xs=xxxx; datr=xxxx; ...", height=100)
        st.session_state.single_cookie = sc
        st.session_state.cfg['cookies'] = sc
    else:
        ck_f = st.file_uploader("UPLOAD cookie.txt (one cookie per line)", type=['txt'], key="ck_up")
        if ck_f:
            lines = [l.strip() for l in ck_f.read().decode('utf-8', 'ignore').split('\n') if l.strip()]
            st.session_state.multi_cookies = lines
            if lines:
                st.session_state.cfg['cookies'] = lines[0]
            st.success(f"Loaded {len(lines)} cookies")
        for i, c in enumerate(st.session_state.multi_cookies):
            p = c[:52] + '…' if len(c) > 52 else c
            st.markdown(f'<span class="pill">Cookie {i + 1}: {p}</span>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  PANEL 3 — MESSAGE FILE UPLOAD
# ══════════════════════════════════════════════
with st.expander("MESSAGE CONFIG", expanded=False):
    msg_f = st.file_uploader("UPLOAD messages.txt  —  one message per line", type=['txt'], key="msg_up")
    if msg_f:
        lines = [l.strip() for l in msg_f.read().decode('utf-8', 'ignore').split('\n') if l.strip()]
        st.session_state.msg_list = lines
        st.session_state.cfg['messages'] = '\n'.join(lines)
        st.success(f"Loaded {len(lines)} messages")
    if st.session_state.msg_list:
        for i, m in enumerate(st.session_state.msg_list[:6]):
            p = m[:58] + '…' if len(m) > 58 else m
            st.markdown(f'<span class="pill">Line {i + 1}: {p}</span>', unsafe_allow_html=True)
        if len(st.session_state.msg_list) > 6:
            st.markdown(f'<span class="pill">+{len(st.session_state.msg_list) - 6} more messages…</span>', unsafe_allow_html=True)
    elif not st.session_state.msg_list:
        st.markdown('<span class="pill">No messages loaded yet — upload a TXT file above</span>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  LIVE LOGS
# ══════════════════════════════════════════════
total_l = len(astate.logs)
success_l = sum(1 for l in astate.logs if '✅' in l or 'sent' in l.lower())
error_l = sum(1 for l in astate.logs if '❌' in l.lower() or 'error' in l.lower())

with st.expander(f"LIVE LOGS  —  {total_l} lines  |  {success_l} ok  |  {error_l} err", expanded=is_run):
    _, clr_col = st.columns([5, 1])
    with clr_col:
        if st.button("CLEAR", use_container_width=True, key="clr_logs"):
            st.session_state.astate.logs = []
            st.rerun()

    if astate.logs:
        html = '<div class="console-wrap"><div class="console-bar"><span class="cd cr"></span><span class="cd cy"></span><span class="cd cg"></span>&nbsp;&nbsp;YKTI RAWAT // CONSOLE</div><div class="console-out" id="co">'
        for log in astate.logs[-100:]:
            esc = log.replace('<', '&lt;').replace('>', '&gt;')
            html += f'<div class="lg {log_cls(log)}">{esc}</div>'
        html += '</div></div><script>var c=document.getElementById("co");if(c)c.scrollTop=c.scrollHeight;</script>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="console-wrap"><div class="console-bar"><span class="cd cr"></span><span class="cd cy"></span><span class="cd cg"></span>&nbsp;&nbsp;YKTI RAWAT // CONSOLE</div><div class="console-out" style="text-align:center;color:rgba(0,255,136,.2);padding:2rem 1rem;">// NO LOGS YET — START AUTOMATION TO SEE OUTPUT</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  AUTO-REFRESH
# ══════════════════════════════════════════════
if is_run:
    st.markdown('<div style="text-align:center;margin:.6rem 0"><span class="pill" style="border-color:rgba(0,255,136,.45);color:#00ff88;">AUTOMATION RUNNING — auto refresh every 3s</span></div>', unsafe_allow_html=True)
    time.sleep(3)
    st.rerun()

st.markdown('<div class="ftr">MADE WITH ❤ BY YKTI RAWAT &nbsp;|&nbsp; 2026 &nbsp;|&nbsp; PREMIUM E2EE SYSTEM</div>', unsafe_allow_html=True)
