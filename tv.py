from playwright.async_api import async_playwright
import asyncio
import requests
from pathlib import Path
import os

async def scrape_images():
    # Create a directory to save images
    output_dir = Path("toffee_images")
    output_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Launch browser (headless=True for no UI, False to see the browser)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Navigate to toffeelive.com
            print("Navigating to https://toffeelive.com...")
            await page.goto("https://toffeelive.com", timeout=60000)

            # Wait for images to load (adjust selector or timeout as needed)
            await page.wait_for_selector("img", timeout=10000)
            print("Page loaded, scraping images...")

            # Find all image elements
            images = await page.locator("img").all()
            image_urls = []

            # Extract src attributes
            for img in images:
                src = await img.get_attribute("src")
                if src:
                    # Handle relative URLs
                    if src.startswith("/"):
                        src = f"https://toffeelive.com{src}"
                    elif not src.startswith("http"):
                        continue  # Skip data URLs or invalid URLs
                    image_urls.append(src)

            print(f"Found {len(image_urls)} images.")

            # Save image URLs to a file
            with open("toffee_image_urls.txt", "w", encoding="utf-8") as f:
                for url in image_urls:
                    f.write(url + "\n")

            # Optionally download images
            for i, url in enumerate(image_urls):
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        # Create a filename from the URL
                        filename = output_dir / f"image_{i+1}.{url.split('.')[-1].split('?')[0]}"
                        with open(filename, "wb") as f:
                            f.write(response.content)
                        print(f"Downloaded: {filename}")
                    else:
                        print(f"Failed to download: {url} (Status: {response.status_code})")
                except Exception as e:
                    print(f"Error downloading {url}: {e}")

        except Exception as e:
            print(f"Error during scraping: {e}")

        finally:
            await browser.close()

# Run the async function
asyncio.run(scrape_images())
