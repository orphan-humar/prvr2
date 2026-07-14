# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import sys
import shutil
import gc
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ BOLD PILLAR SETTINGS ---
TABS_PER_MACHINE = 2
MIN_DELAY = 500         
MAX_DELAY = 800         
CYCLE_MIN_MINUTES = 30  
CYCLE_MAX_MINUTES = 40  
REST_SECONDS = 300      

sys.stdout.reconfigure(encoding='utf-8')

USER_AGENTS = [
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36"
]

async def run_strike(node_id, cookie, target_id, target_name):
    async with async_playwright() as p:
        current_ua = random.choice(USER_AGENTS)
        profile_path = os.path.join(os.getcwd(), f"n_{node_id}_{random.randint(10000, 99999)}")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            channel="chrome",
            headless=True,
            user_agent=current_ua,
            viewport={'width': random.randint(370, 410), 'height': random.randint(650, 700)},
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-background-timer-throttling",
                "--disable-threaded-scrolling",
                "--excludeSwitches=enable-automation"
            ]
        )

        await Stealth().apply_stealth_async(context)

        # MOCKING HARDWARE
        stealth_js = """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Apple Inc.';
                if (parameter === 37446) return 'Apple GPU';
                return getParameter(parameter);
            };
        """
        await context.add_init_script(stealth_js)

        # STRIKE SCRIPT LOGIC (WITH 2-MINUTE AUTO-RELOAD)
        strike_script = f"""
            ((name, minD, maxD) => {{
                const flowers = ["🌸", "🌹", "🌺", "🌻", "🌼", "🌷", "💐", "🪷"];
                const startTime = Date.now();
                const RELOAD_INTERVAL = 120000; // 2 minutes

                const getBlock = () => {{
                    const randomFlower = flowers[Math.floor(Math.random() * flowers.length)];
                    const baseText = "ᴘʀᴀᴛɪᴋ-ᴠᴇᴇʀ-ꜱᴜʀᴀᴊ-ɴᴇᴍᴇꜱɪꜱ ᴛʀʏ. ᴍᴀ ғʟᴏᴡᴇʀ. " + randomFlower + " ʏᴀ ғɪʀᴇ 🔥??";
                    return baseText + "\\n".repeat(15) + baseText + "\\n".repeat(15) + baseText;
                }};

                const pulse = () => {{
                    // Trigger reload after 2 minutes
                    if (Date.now() - startTime > RELOAD_INTERVAL) {{
                        window.location.reload();
                        return;
                    }}
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {{
                        const dt = new DataTransfer();
                        dt.setData('text/plain', getBlock());
                        box.focus();
                        box.dispatchEvent(new ClipboardEvent('paste', {{ clipboardData: dt, bubbles: true }}));
                        box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        setTimeout(() => {{
                            const btn = Array.from(document.querySelectorAll('div[role="button"], button')).find(el => el.textContent === 'Send' || el.innerText === 'Send');
                            if (btn) btn.click();
                        }}, 200);
                    }}
                    setTimeout(pulse, Math.floor(Math.random() * (maxD - minD + 1) + minD));
                }};
                pulse();
            }})('{target_name}', {MIN_DELAY}, {MAX_DELAY})
        """
        # Inject script so it runs every time the page loads/reloads
        await context.add_init_script(strike_script)

        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/', 'secure': True, 'httpOnly': True}])

        pages = []
        for i in range(TABS_PER_MACHINE):
            pg = await context.new_page()
            await pg.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,woff,woff2,ttf}", lambda route: route.abort())
            try:
                await pg.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded", timeout=15000)
                pages.append(pg)
            except: pass
        
        await asyncio.sleep(random.randint(CYCLE_MIN_MINUTES * 60, CYCLE_MAX_MINUTES * 60))
        for pg in pages: 
            try: await pg.close()
            except: pass
        await context.close()
        
        try:
            if os.path.exists(profile_path): shutil.rmtree(profile_path)
        except: pass

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")
    m_id = os.environ.get("MACHINE_ID", "1")
    
    if not cookie or not target_id: return

    while True:
        try:
            await run_strike(m_id, cookie, target_id, target_name)
            gc.collect() 
            await asyncio.sleep(REST_SECONDS)
        except Exception:
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
