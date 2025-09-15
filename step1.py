from playwright.sync_api import sync_playwright
import json, time, os

base_dir = "list_perusahaan"
os.makedirs(base_dir, exist_ok=True)

# Cari nomor folder terakhir
existing_folders = [int(f) for f in os.listdir(base_dir) if f.isdigit()]
next_id = max(existing_folders) + 1 if existing_folders else 1

search_dir = os.path.join(base_dir, str(next_id))
os.makedirs(search_dir, exist_ok=True)

companies = [
    "Ken Citra Propertindo",
    "Kenari Golden Taxi",
    "Kenari Indah",
    "Kenari Manufacturing",
    "Kencana Abadi Sentosa",
    "Kencana Cipta Abadi",
    "Kencana Jaya Sakti",
    "Kencana Mulia Steel",
    "Kencana Mustika Sari",
    "Kencana Sari Jaya Abadi",
    "Kencana Sejahtera",
    "Kencana Sejahtera Lestari",
    "Kencana Utama Prima",
    "Kendra Indonesia",
    "Kenneth Adam Perkasa",
    "Kent Mandiri Teknik",
    "Keola Mega",
    "Keraton Karya Solusi",
    "Kerf Indonesia",
    "Keris Karya Sejahtera"
]

cookies = [
    {"name": "kemnaker_ri_session", "value": "eyJpdiI6ImZ1REhibTJ1UEE3c0FQbEhoeDFkNUE9PSIsInZhbHVlIjoiSFUra0VXRlZGdkl4ZlhQRGxIWVMvSXMwaFNzcUt5Q3Q2QSt5NjQrRWYyaU44MjJRK3FpYkxNRVdBSjVzb1pnbzk3cUxrazJzRjlrVXZuajVjeHgrUjlWZmM3RkFzS0lQR1Z0ai81ZUU2azJUd0JzWm1YNzVNV3pQVFpiRWF3ZjYiLCJtYWMiOiJkZGMxMmZlZjc3OGY4OGMxNmEzMTY0N2ZjMjFhZTc4ZjFiZDQ3YjY1NzIzNGNiNGY5Y2Y4MzZkZTM1ZTBhZjM1IiwidGFnIjoiIn0%3D", "domain": "account.kemnaker.go.id", "path": "/", "httpOnly": True},
    {"name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d", "value": "eyJpdiI6IlBVVVVPWWorUjRpZ2ZrWmZlL251dUE9PSIsInZhbHVlIjoia2toU21iN1p0NjJLZ2RXbWFEN0xrcGhuRXJEaTJEbzVMcUh2ZG9ZREhEQ242RGZybVptbyt5RGJ2cW1EOWR0Z2F6QnhnbnBRdVFGZmJJL1g5VmE1YjBPaTRpaHZtQkVaUC9ic3dRRSt5azF6NzgzNlBtaDFRMnNPZ214TVNYSDR2RlczYWhIbkRrQzBOalBLWldWM0xVQXlQaFZUUWpTa2N1RkY1ZHRwSHVjSTJsT29CbVQ3TnVwbVhxR3AxdHhLSlpvcjE4M01FamlSMlF0UG5mcHNnNFYxV0hiM2NpSkpOUE0yenRnd0tybk1Fa3JwN3pCRzRnNmhWWFpXVkpkbit4MlhFV3pHMUxUOEFaUS9Jd2Nkenc9PSIsIm1hYyI6IjZhMDc0NzEyMDc5NTcwOWU0MWJlZDA2MmExZTA2OTU0ZDEzZDQyYmUxODAyZjM5MTc4ODZmOWIxZmI1MjA3Y2MiLCJ0YWciOiIifQ%3D%3D", "domain": "account.kemnaker.go.id", "path": "/", "httpOnly": True},
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    page.goto("https://wajiblapor.kemnaker.go.id/admin/companies")
    time.sleep(5)

    for name in companies:
        print(f"🔎 Mencari: {name}")
        page.fill("input[placeholder='Cari berdasarkan nama perusahaan']", name)
        page.click("div.input-group-append button")

        while True:
            res = context.wait_for_event("response", timeout=10000)
            if "api-wlkp.kemnaker.go.id/v1/companies" in res.url:
                data = res.json().get("data", [])

                if not data:
                    print(f"⚠️ {name}: tidak ada hasil")
                else:
                    filename = os.path.join(search_dir, f"{name.replace(' ','_')}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    print(f"✅ {name}: {len(data)} hasil disimpan ke {filename}")
                break

        time.sleep(2)

    browser.close()

print(f"🎉 Semua search selesai, hasil disimpan di folder {search_dir}")