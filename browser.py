import requests
import zipfile
import undetected_chromedriver as uc
from selenium import webdriver
import os
import time
from playwright.async_api import async_playwright
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import asyncio
import uvicorn
app = FastAPI()

class info(BaseModel):
    site: str
async def get_recaptcha_response(page):
    if await page.evaluate('document.getElementById("g-recaptcha-resp'
        'onse").value !== ""'):
        recaptcha_response = await page.evaluate('document.getElementById'
            '("g-recaptcha-response").value')
        return recaptcha_response
async def run(siteurl):
    # Replace with your key.
    extension_path = 'ext.xpi'
    NOPECHA_KEY = 'sub_1NpGINCRwBwvt6ptY1lwiCr4'
    user_data_dir = "/tmp/test-user-data-dir"
    
    async with async_playwright() as p:
        args = [
            f"--load-extension={extension_path}"
        ]
        context = await p.firefox.launch_persistent_context(
            user_data_dir,
            # headless=False,
            args=args
        )

        # Perform your actions within the context
        page = await context.new_page()
        # Your code here
        page.on("request", lambda request: print(">>", request.method, request.url))
        page.on("response", lambda response: print("<<", response.status, response.url))
        
        await page.goto(f"https://nopecha.com/setup#{NOPECHA_KEY}")
        await page.wait_for_timeout(500)
        await page.goto(siteurl)
        while True:
            token = await get_recaptcha_response(page)
            if "03A" in str(token):
                print(token)
                break
                
        # await page.wait_for_timeout(100000)

        # Close the browser and cleanup
        await page.close()
        await context.close()
        return token
@app.post("/solve_recaptchav2/")
async def solve_recaptchav2(info: info):
    # Perform your captcha verification logic here
    token = await run(info.site)
    return {"response": token}
    # if "03A" in info.token:
    #     return JSONResponse(content={"message": "Captcha verification successful"})
    # else:
    #     return JSONResponse(content={"message": "Captcha verification failed"})
# Run the script asynchronously

# asyncio.get_event_loop().run_until_complete(run())
if __name__ == '__main__':
    uvicorn.run(app="browser:app", port=8585, host='0.0.0.0')