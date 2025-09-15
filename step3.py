import os
import json
import glob
from playwright.async_api import async_playwright

SELECTED_DIR = "selected_companies"
OUTPUT_DIR = "data_perusahaan"

os.makedirs(OUTPUT_DIR, exist_ok=True)

cookies = [
    {"name": "kemnaker_ri_session", "value": "eyJpdiI6ImZ1REhibTJ1UEE3c0FQbEhoeDFkNUE9PSIsInZhbHVlIjoiSFUra0VXRlZGdkl4ZlhQRGxIWVMvSXMwaFNzcUt5Q3Q2QSt5NjQrRWYyaU44MjJRK3FpYkxNRVdBSjVzb1pnbzk3cUxrazJzRjlrVXZuajVjeHgrUjlWZmM3RkFzS0lQR1Z0ai81ZUU2azJUd0JzWm1YNzVNV3pQVFpiRWF3ZjYiLCJtYWMiOiJkZGMxMmZlZjc3OGY4OGMxNmEzMTY0N2ZjMjFhZTc4ZjFiZDQ3YjY1NzIzNGNiNGY5Y2Y4MzZkZTM1ZTBhZjM1IiwidGFnIjoiIn0%3D", "domain": "account.kemnaker.go.id", "path": "/", "httpOnly": True},
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

    # buka halaman employees
    await page.goto(f"https://wajiblapor.kemnaker.go.id/companies/{cid}/employment/employees")
    await page.wait_for_timeout(4000)  

    await page.close()
    return data_container["value"]

async def main():
    files = [f for f in os.listdir(SELECTED_DIR) if f.endswith(".json")]
    if not files:
        print("⚠️ Tidak ada file perusahaan di folder selected_companies")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context()
        await context.add_cookies(cookies)

        for file in files:
            filepath = os.path.join(SELECTED_DIR, file)
            with open(filepath, encoding="utf-8") as f:
                comp = json.load(f)

            nama = comp["nama"]
            cid = comp["id"]

            print(f"\n📌 Ambil data pekerja {nama}")
            data = await scrape_company(context, nama, cid)

            if data and data.get("data"):
                safe_name = nama.replace(" ", "_")
                filename = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"📁 {nama}: data tersimpan di {filename}")
            else:
                print(f"⚠️ {nama}: tidak ada pekerja, file tidak disimpan")

        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())