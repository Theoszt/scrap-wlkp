import os
import json
import glob
from playwright.async_api import async_playwright

INPUT_DIR = "selected_companies"
OUTPUT_DIR = "data_perusahaan"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

existing_folders = [int(f) for f in os.listdir(INPUT_DIR) if f.isdigit()]
if not existing_folders:
    print("⚠️ Belum ada perusahaan yang dipilih di folder selected_companies")
    exit()

next_id = max(existing_folders) + 1
latest_folder = str(max(existing_folders))
base_dir = os.path.join(INPUT_DIR, latest_folder)
search_dir = os.path.join(OUTPUT_DIR, str(next_id))
os.makedirs(search_dir, exist_ok=True)
os.makedirs(base_dir, exist_ok=True)

cookies = [
    {"name": "kemnaker_ri_session", "value": "eyJpdiI6IkhVWUMyUGNrK2JpYnBBVFlpUEtwa2c9PSIsInZhbHVlIjoidWlNa1ZCSXh5c1JHbmFiNjFMNldjK2xOSHZSVDZmOEw2UnVzZ2UrSzRGZFBqNnVlZEtZdXdYdnRXcTlRRTFvb3dFc3RLbVJHck5wQk0zTmlRbU40MHVYekhySWozRUdXYXkxYVR4eCtZUUpHcmlZZE4wbURwQlJPRklHTVBacHUiLCJtYWMiOiJlYTM0ZTdiYjEzMWNjY2ZmNjIyM2Y0ZGI1MWZhMTM5OTA1YjBmY2NjZjk0ZmE0ZDMxMGU3YTliMjNiODdjMzhhIiwidGFnIjoiIn0%3D", "domain": "account.kemnaker.go.id", "path": "/", "httpOnly": True},
    {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IlBVVVVPWWorUjRpZ2ZrWmZlL251dUE9PSIsInZhbHVlIjoia2toU21iN1p0NjJLZ2RXbWFEN0xrcGhuRXJEaTJEbzVMcUh2ZG9ZREhEQ242RGZybVptbyt5RGJ2cW1EOWR0Z2F6QnhnbnBRdVFGZmJJL1g5VmE1YjBPaTRpaHZtQkVaUC9ic3dRRSt5azF6NzgzNlBtaDFRMnNPZ214TVNYSDR2RlczYWhIbkRrQzBOalBLWldWM0xVQXlQaFZUUWpTa2N1RkY1ZHRwSHVjSTJsT29CbVQ3TnVwbVhxR3AxdHhLSlpvcjE4M01FamlSMlF0UG5mcHNnNFYxV0hiM2NpSkpOUE0yenRnd0tybk1Fa3JwN3pCRzRnNmhWWFpXVkpkbit4MlhFV3pHMUxUOEFaUS9Jd2Nkenc9PSIsIm1hYyI6IjZhMDc0NzEyMDc5NTcwOWU0MWJlZDA2MmExZTA2OTU0ZDEzZDQyYmUxODAyZjM5MTc4ODZmOWIxZmI1MjA3Y2MiLCJ0YWciOiIifQ%3D%3D", "domain": "account.kemnaker.go.id", "path": "/", "httpOnly": True},
]

async def scrape_company(context, nama, cid):
    page = await context.new_page()
    target_api = f"https://api-wlkp.kemnaker.go.id/v1/companies/{cid}/employees"
    data_container = {"value": None}

    async def handle_response(response):
        if response.url.startswith(target_api):
            try:
                data = await response.json()
                data_container["value"] = data
                print(f"✅ {nama}: {len(data.get('data', []))} pekerja")
            except Exception as e:
                print(f"⚠️ {nama}: gagal parse JSON -> {e}")

    page.on("response", handle_response)

    await page.goto(
        f"https://wajiblapor.kemnaker.go.id/companies/{cid}/employment/employees",
        wait_until="networkidle"
        )

    await page.close()
    return data_container["value"]

async def main():
    files = [f for f in os.listdir(base_dir) if f.endswith(".json")]
    if not files:
        print("⚠️ Tidak ada file perusahaan di folder list_perusahaan")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context()
        await context.add_cookies(cookies)

        for file in files:
            filepath = os.path.join(base_dir, file)
            with open(filepath, encoding="utf-8") as f:
                comp = json.load(f)

            nama = comp["nama"]
            cid = comp["id"]

            print(f"\n📌 Ambil data pekerja {nama}")
            data = await scrape_company(context, nama, cid)

            if data and data.get("data"):
                safe_name = nama.replace(" ", "_")
                filename = os.path.join(search_dir, f"{safe_name}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                print(f"⚠️ {nama}: tidak ada pekerja")

        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())