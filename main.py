import asyncio
import os
import random
import sys
import shutil
import time
import requests
import uuid
from playwright.async_api import async_playwright

# Force immediate log flushing
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

START_TIME = time.time()
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
BASE_TEXT = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggᴀ"
EMOJIS = ["🔥", "🌟", "✨", "💫", "🚀", "💎", "🌙", "🧿", "🍃", "🦋"]

async def block_media(route):
    if route.request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()

# --- 🛡️ API NAME GUARDIAN ---
async def run_name_guardian(sid, tid, sig):
    print("🛡️ [GUARDIAN] Initializing API Name Guardian...", flush=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "X-IG-App-ID": "936619743392459"})
    session.cookies.set("sessionid", sid, domain=".instagram.com")
    
    while True:
        try:
            wait_time = random.uniform(300, 600)
            await asyncio.sleep(wait_time)
            resp = session.get(f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/")
            if resp.status_code == 200:
                if resp.json().get("thread", {}).get("thread_title") != sig:
                    csrf = session.cookies.get("csrftoken", "")
                    session.post(f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/update_title/",
                                 data={"title": sig, "_csrftoken": csrf, "_uuid": str(uuid.uuid4())},
                                 headers={"X-CSRFToken": csrf})
                    print("🔒 [GUARDIAN] Name secured.", flush=True)
        except Exception as e:
            print(f"⚠️ [GUARDIAN] Error: {e}", flush=True)

# --- 🔥 STRIKE ENGINE ---
async def run_engine(engine_id, sid, url):
    user_data_dir = f"./session_data_{engine_id}"
    
    while True:
        if time.time() - START_TIME > 18000:
            sys.exit(0)

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir, headless=True,
                args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
            )
            await browser.add_cookies([{"name": "sessionid", "value": sid, "domain": ".instagram.com", "path": "/", "secure": True, "httpOnly": True}])
            page = await browser.new_page()
            await page.route("**/*", block_media)
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                msg_box = page.locator('div[role="textbox"][contenteditable="true"]').first
                
                while True:
                    # Send 10 blocks + 1 signature (11 total)
                    for i in range(11):
                        if i < 10:
                            single_line = f"{BASE_TEXT} {random.choice(EMOJIS)}"
                            text_to_send = "\n\n".join([single_line] * 7)
                        else:
                            text_to_send = SIGNATURE
                        
                        await msg_box.focus()
                        await msg_box.fill(text_to_send) 
                        await page.keyboard.press("Enter")
                        print(f"✅ [Engine {engine_id}] Sent block {i+1}/11", flush=True)
                        await asyncio.sleep(random.uniform(0.5, 0.8))
                    
                    # Reload every cycle for stability
                    await page.reload(wait_until='domcontentloaded')
                    msg_box = page.locator('div[role="textbox"][contenteditable="true"]').first
                    
            except Exception as e:
                print(f"⚠️ [Engine {engine_id}] Error: {e}", flush=True)
            
            await browser.close()
            if os.path.exists(user_data_dir):
                shutil.rmtree(user_data_dir, ignore_errors=True)

async def main():
    sid = os.environ.get("SESSION_ID")
    url = os.environ.get("GROUP_URL")
    tid = url.strip('/').split('/')[-1] if url else ""
    
    tasks = [run_engine(i+1, sid, url) for i in range(2)]
    if tid:
        tasks.append(run_name_guardian(sid, tid, SIGNATURE))
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
