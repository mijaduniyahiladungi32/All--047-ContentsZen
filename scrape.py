import asyncio
from playwright.async_api import async_playwright
import requests
import os
from urllib.parse import urlparse

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.jagobd.com/category/bangla-channel', wait_until='networkidle')  # Wait for full load
        
        # Extract all img elements and their srcs
        images = await page.eval_on_selector_all('img', 'elements => elements.map(el => el.src)')
        
        os.makedirs('images', exist_ok=True)
        
        for i, src in enumerate(images):
            if src and (src.startswith('http://') or src.startswith('https://')):
                try:
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200:
                        # Get file extension from URL (fallback to .jpg)
                        parsed = urlparse(src)
                        ext = os.path.splitext(parsed.path)[1] or '.jpg'
                        filename = f'images/channel_image_{i}{ext}'
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        print(f'Downloaded: {filename}')
                except Exception as e:
                    print(f'Error downloading {src}: {e}')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
