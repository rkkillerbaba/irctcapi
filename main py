from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
import httpx
import uvicorn

app = FastAPI(title="IRCTC Charts API")

# Request payload ka structure jo humari API accept karegi
class ChartRequest(BaseModel):
    trainNo: str
    jDate: str
    boardingStation: str

@app.post("/get-charts")
async def get_train_charts(req: ChartRequest):
    async with async_playwright() as p:
        # Headless Chromium browser launch karna
        # --no-sandbox aur --disable-setuid-sandbox Docker/Render environment ke liye zaroori hain
        browser = await p.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        
        # Ek real browser jaisa User-Agent set karna
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        
        try:
            # 1. IRCTC ki website par jaana taaki Akamai hume fresh cookies de sake
            await page.goto("https://www.irctc.co.in/online-charts/", wait_until="domcontentloaded", timeout=60000)
            
            # Thoda wait karna (3 seconds) taaki background JavaScript/Akamai execute ho jaye
            await page.wait_for_timeout(3000)
            
            # 2. Browser session se fresh cookies nikalna
            cookies = await context.cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # 3. IRCTC API par bhejne ke liye Headers set karna (aapke screenshot ke mutabiq)
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": "https://www.irctc.co.in",
                "Referer": "https://www.irctc.co.in/online-charts/",
                "User-Agent": user_agent
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

# Local testing ke liye (if you run this file directly)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
