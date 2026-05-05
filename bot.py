# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import sys
import httpx
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ BOLD PILLAR SETTINGS ---
TABS_PER_MACHINE = 2    
PULSE_DELAY = 100       
CYCLE_DURATION = 60     
SESSION_MAX_SEC = 21000 
sys.stdout.reconfigure(encoding='utf-8')

# 🔱 TELEGRAM CONFIG
TG_TOKEN = "7968897685:AAHWWUFmfRFYUFQxjV0GE_9Avhn-iRH2j7M"
TG_CHAT_ID = "1225435208"

async def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
    except: pass

async def run_strike(node_id, cookie, target_id, target_name):
    async with async_playwright() as p:
        user_agent = "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
        profile_path = os.path.join(os.getcwd(), f"n_{node_id}")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=True,
            user_agent=user_agent,
            viewport={'width': 400, 'height': 300},
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-background-timer-throttling",
                "--disable-threaded-scrolling"
            ]
        )

        await Stealth().apply_stealth_async(context)

        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{
            'name': 'sessionid', 'value': sid.strip(), 
            'domain': '.instagram.com', 'path': '/', 'secure': True, 'httpOnly': True
        }])

        await send_tg(f"🔱 <b>Machine {node_id} BOLD PILLAR</b>\nAlign: Ultra-Vertical | Delay: 100ms")

        # ⚡ BOLD ALIGNED SCRIPT
        strike_script = """
            (name, delay) => {
                const getBlock = (n) => {
                    const lines = [
                        `__________________[${n}] 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑲𝑨 𝑮𝑼𝑳𝑨𝑴 🔱__________________`,
                        `__________________[${n}] 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑩𝑯𝑶𝑺𝑫𝑨 🔥__________________`,
                        `__________________[${n}] 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑵𝑬 𝑴𝑨𝑨 𝑪𝑯𝑶𝑫 𝑫𝑰 😂__________________`,
                        `__________________[${n}] 𝑹𝑼𝑵𝑫𝑰 𝑲𝑬 𝑩𝑨𝑪𝑪𝑯𝑬 𝑩𝑨𝑨𝑷 𝑺𝑬 𝑫𝑨𝑹 🤡__________________`,
                        `__________________[${n}] 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑻𝑬𝑹𝑨 𝑴𝑨𝑨𝑳𝑰𝑲 𝑯𝑨𝑰 👑__________________`,
                        `__________________[${n}] 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑰 𝑪𝑯𝑼𝑻 𝑴𝑨𝑰 𝑯𝑨𝑻𝑯𝑶𝑫𝑨 🔨__________________`
                    ];
                    const baseLine = lines[Math.floor(Math.random() * lines.length)];
                    let block = "";
                    for(let i = 0; i < 21; i++) { block += baseLine + "\\n"; }
                    return block + "🔱 " + Math.random().toString(36).substring(8).toUpperCase();
                }

                const pulse = () => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        box.focus();
                        document.execCommand('insertText', false, getBlock(name));
                        box.dispatchEvent(new Event('input', { bubbles: true }));
                        box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 }));
                        box.innerHTML = "";
                    }
                    setTimeout(() => { requestAnimationFrame(pulse); }, delay);
                }
                pulse();
            }
        """

        elapsed = 0
        while elapsed < SESSION_MAX_SEC:
            pages = []
            for i in range(TABS_PER_MACHINE):
                pg = await context.new_page()
                await pg.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,woff,woff2,ttf}", lambda route: route.abort())
                try:
                    await pg.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=15000)
                    await pg.evaluate(strike_script, [target_name, PULSE_DELAY])
                    pages.append(pg)
                except: pass
            
            await asyncio.sleep(CYCLE_DURATION)
            for pg in pages: await pg.close()
            elapsed += CYCLE_DURATION

        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")
    m_id = os.environ.get("MACHINE_ID", "1")
    if cookie and target_id:
        await run_strike(m_id, cookie, target_id, target_name)

if __name__ == "__main__":
    asyncio.run(main())
