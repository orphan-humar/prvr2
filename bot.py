# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import sys
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ BOLD PILLAR SETTINGS ---
TABS_PER_MACHINE = 2    
PULSE_DELAY = 100       
CYCLE_DURATION = 60     
SESSION_MAX_SEC = 21000 
sys.stdout.reconfigure(encoding='utf-8')

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

        # ⚡ BOLD ALIGNED SCRIPT (UPDATED WITH TITAN TEXT & PASTE METHOD)
        strike_script = """
            (name, delay) => {
                const getBlock = () => {
                    const emojis = ["💙", "❤️", "💚", "💛", "💜", "🖤", "🤍", "🤎", "🧡", "💖"];
                    const currentEmoji = emojis[Math.floor(Math.random() * emojis.length)];
                    const line = "ᴘʀᴀᴛɪᴋ-ᴠᴇᴇʀ-ꜱᴜʀᴀᴊ-ɴᴇᴍᴇꜱɪꜱ 𝚃𝙼𝙺𝙲 " + currentEmoji + "་༘࿐";
                    
                    let text = "";
                    for(let i = 0; i < 10; i++) { 
                        text += line + "\\n\\n\\n\\n"; 
                    }
                    return text;
                }

                const pulse = () => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const text = getBlock();
                        
                        // 1. Create a virtual clipboard event
                        const dataTransfer = new DataTransfer();
                        dataTransfer.setData('text/plain', text);
                        
                        const pasteEvent = new ClipboardEvent('paste', {
                            clipboardData: dataTransfer,
                            bubbles: true,
                            cancelable: true
                        });
                        
                        // 2. Focus and inject via paste event
                        box.focus();
                        box.dispatchEvent(pasteEvent);
                        
                        // 3. Trigger input event to update React state
                        box.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // 4. Trigger send button
                        setTimeout(() => {
                            const sendBtn = Array.from(document.querySelectorAll('div[role="button"], button')).find(el => 
                                el.textContent === 'Send' || el.innerText === 'Send'
                            );
                            if (sendBtn) {
                                sendBtn.click();
                            } else {
                                const fallbackBtn = document.querySelector('form button[type="button"], div[aria-label="Send"]');
                                if (fallbackBtn) fallbackBtn.click();
                            }
                        }, 200);
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
