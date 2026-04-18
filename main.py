from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
import httpx
import uvicorn

app = FastAPI(title="IRCTC Charts API")

# Request payload ka structure
class ChartRequest(BaseModel):
    trainNo: str
    jDate: str
    boardingStation: str

@app.post("/get-charts")
async def get_train_charts(req: ChartRequest):
    async with async_playwright() as p:
        # Headless Chromium browser launch karna with STEALTH FLAGS (Anti-Bot bypass)
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled', # Sabse zaroori anti-bot flag
                '--ignore-certificate-errors',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-web-security'
            ]
        )
        
        # Ek ekdum real browser jaisa User-Agent set karna
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # Context create karte waqt bypass flags add karna
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            bypass_csp=True
        )
        
        # Ek choti si script jo browser ko batati hai ki "Main bot nahi hu"
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        page = await context.new_page()
        
        try:
            # 1. IRCTC ki website par jaana taaki Akamai hume fresh cookies de sake
            await page.goto("https://www.irctc.co.in/online-charts/", wait_until="domcontentloaded", timeout=60000)
            
            # Thoda extra wait karna (4 seconds) taaki Akamai apna JS check complete kar le
            await page.wait_for_timeout(4000)
            
            # 2. Browser session se fresh cookies nikalna
            cookies = await context.cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # 3. IRCTC API par bhejne ke liye Headers set karna
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": "https://www.irctc.co.in",
                "Referer": "https://www.irctc.co.in/online-charts/",
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            # Payload set karna
            payload = {
                "trainNo": req.trainNo,
                "jDate": req.jDate,
                "boardingStation": req.boardingStation
            }
            
            # 4. httpx ka use karke actual API par POST request marna (with fresh cookies)
            api_url = "https://www.irctc.co.in/online-charts/api/trainComposition"
            async with httpx.AsyncClient(cookies=cookie_dict, headers=headers) as client:
                response = await client.post(api_url, json=payload, timeout=30.0)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=response.status_code, detail=f"IRCTC Server Error: {response.text}")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await browser.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
