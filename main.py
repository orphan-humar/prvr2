import asyncio
import os
import random
import sys
import shutil
import time
import requests
import uuid
from playwright.async_api import async_playwright

START_TIME = time.time()
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
SIGNATURE_CHANCE = 0.15 

def get_payload():
    base_text = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx ᴛʀʏ. ᴍᴀ ғʟᴏᴡᴇʀ."
    fire_part = "ʏᴀ ғɪʀᴇ 🔥??"
    flowers = ["🌸", "🌹", "🌺", "🌻", "🌼", "🌷"]
    line = f"{base_text} {random.choice(flowers)} {fire_part}"
    return ("\n" * 50).join([line] * 3)

async def block_media(route):
    if route.request.resource_type in ["image", "media", "font"]:
        await route.abort()
    else:
        await route.continue_()

# --- 🛡️ API NAME GUARDIAN ---
async def run_name_guardian(sid, tid, sig):
    print("🛡️ [GUARDIAN] Initializing API Name Guardian...", flush=True)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", 
        "X-IG-App-ID": "936619743392459"
    })
    session.cookies.set("sessionid", sid, domain=".instagram.com")
    
    while True:
        try:
            # Randomized delay: 300 to 600 seconds (5 to 10 minutes)
            wait_time = random.uniform(300, 600)
            print(f"⏳ [GUARDIAN] Sleeping for {wait_time:.1f}s before next check...", flush=True)
            await asyncio.sleep(wait_time)
            
            resp = session.get(f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/")
            if resp.status_code == 200:
                current_title = resp.json().get("thread", {}).get("thread_title")
                if current_title != sig:
                    print(f"🚨 [GUARDIAN] BREACH DETECTED! Name changed to '{current_title}'. Re-securing...", flush=True)
                    csrf = session.cookies.get("csrftoken", "")
                    session.post(
                        f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/update_title/",
                        data={"title": sig, "_csrftoken": csrf, "_uuid": str(uuid.uuid4())},
                        headers={"X-CSRFToken": csrf}
                    )
                    print("🔒 [GUARDIAN] Name successfully secured.", flush=True)
                else:
                    print("🛡️ [GUARDIAN] Thread name is secure.", flush=True)
        except Exception as e: 
            print(f"⚠️ [GUARDIAN] Error checking name: {e}", flush=True)

# --- 🔥 STRIKE ENGINE ---
async def run_engine(engine_id, sid, url):
    user_data_dir = f"./session_data_{engine_id}"
    print(f"💥 [Engine {engine_id}] Waking up. Preparing to breach target...", flush=True)
    
    while True:
        if time.time() - START_TIME > 18000:
            print(f"⏰ [Engine {engine_id}] 5-hour limit reached. Evacuating matrix.", flush=True)
            sys.exit(0)

        async with async_playwright() as p:
            print(f"🌐 [Engine {engine_id}] Launching stealth browser...", flush=True)
            browser = await p.chromium.launch_persistent_context(
                user_data_dir, headless=True,
                args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
            )
            await browser.add_cookies([{"name": "sessionid", "value": sid, "domain": ".instagram.com", "path": "/", "secure": True, "httpOnly": True}])
            page = await browser.new_page()
            await page.route("**/*", block_media)
            
            try:
                print(f"🔗 [Engine {engine_id}] Connecting to target URL...", flush=True)
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                msg_box = page.locator('div[role="textbox"], div[aria-label="Message"]').first
                print(f"✅ [Engine {engine_id}] TARGET SECURED. Initializing payload loop.", flush=True)
                
                msg_count = 0
                while msg_count < 150: 
                    if msg_count > 0 and msg_count % 30 == 0:
                        print(f"🔄 [Engine {engine_id}] RELOADING PAGE...", flush=True)
                        await page.reload(wait_until='domcontentloaded')
                        msg_box = page.locator('div[role="textbox"], div[aria-label="Message"]').first
                    
                    if random.random() < SIGNATURE_CHANCE:
                        text_to_send = SIGNATURE
                        msg_type = "SIGNATURE"
                        icon = "☠️"
                    else:
                        text_to_send = get_payload()
                        msg_type = "PAYLOAD"
                        icon = "🚀"

                    await msg_box.focus()
                    await msg_box.fill(text_to_send) 
                    await page.keyboard.press("Enter")
                    
                    msg_count += 1
                    print(f"{icon} [Engine {engine_id}] MESSAGE SENT [{msg_type}] | Strike {msg_count}/150", flush=True)
                    await asyncio.sleep(0.3)
                    
            except Exception as e:
                print(f"⚠️ [Engine {engine_id}] CONNECTION LOST: {e}", flush=True)
            
            print(f"🧹 [Engine {engine_id}] Closing browser and wiping session data...", flush=True)
            await browser.close()
            if os.path.exists(user_data_dir):
                shutil.rmtree(user_data_dir, ignore_errors=True)

async def main():
    sid = os.environ.get("SESSION_ID")
    url = os.environ.get("GROUP_URL")
    
    print("🔥 INITIALIZING PHOENIX MATRIX SYSTEM 🔥", flush=True)
    
    tid = url.strip('/').split('/')[-1] if url else ""
    tasks = [run_engine(i+1, sid, url) for i in range(2)]
    
    if tid:
        tasks.append(run_name_guardian(sid, tid, SIGNATURE))
    else:
        print("⚠️ [SYSTEM] Could not parse Thread ID. Guardian offline.", flush=True)
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
