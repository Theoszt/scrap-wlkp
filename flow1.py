import streamlit as st
import requests
import os
import json
import pandas as pd
import glob
import zipfile
from io import BytesIO

# =========================
# Konfigurasi API
# =========================
BASE_URL = "https://api-wlkp.kemnaker.go.id/v1/companies"
st.sidebar.title("🔑 Pengaturan")
st.sidebar.text_input("Masukkan API Token", key="api_token", type="password")

def get_headers():
    token = st.session_state.get("api_token", "")
    return {
        "Authorization": f"Bearer {token}" if token else "",
        "Accept": "application/json"
    }

os.makedirs("data_perusahaan", exist_ok=True)

# =========================
# Inisialisasi session_state
# =========================
if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_companies" not in st.session_state:
    st.session_state.selected_companies = {}

# =========================
# Mapping referensi
# =========================
gender_map = {0: "Laki-laki", 1: "Perempuan"}
status_map = {0: "Tenaga Kerja PKWT", 1: "Tenaga Kerja Tetap"}
education_map = {
    "S1": "Strata 1", "S2": "Strata 2", "S3": "Strata 3",
    "SD": "SD/MI/Sederajat", "SMP": "SLTP/MTs/Sederajat",
    "SMA": "SLTA / MA / Sederajat", "SMK": "SMK / Sederajat",
    "D1": "Diploma 1", "D2": "Diploma 2", "D3": "Diploma 3", "D4": "Diploma 4",
}

# =========================
# STEP 1: Cari & Pilih Perusahaan
# =========================
if st.session_state.step == 1:
    st.title("Step 1️⃣ Cari & Pilih Perusahaan")

    company_names = st.text_area(
        "Masukkan nama perusahaan (pisahkan dengan enter)",
        "MAJAPAHIT SOLUSI BERSAMA\nCGV\nKaliwang"
    ).split("\n")

    if st.button("Cari Perusahaan"):
        st.session_state.search_results = {}

        for name in company_names:
            params = {
                "code": "",
                "name": name,
                "certificate": "",
                "email": "",
                "province": "d5b90b58-bfb2-4afa-b754-d1280dabe9b3",
                "city": "e4342dff-58ea-4834-b15d-00c5eb842d5d",
                "sub_district": "",
                "village": "",
                "type": "",
                "page": 1
            }
            res = requests.get(BASE_URL, headers=get_headers(), params=params)
            data = res.json().get("data", [])

            if not data:
                keyword = name.split("(")[0].strip()
                if keyword != name:
                    params["name"] = keyword
                    res = requests.get(BASE_URL, headers=get_headers(), params=params)
                    data = res.json().get("data", [])

            st.session_state.search_results[name] = data

        st.session_state.step = 1.5
        st.rerun()

# =========================
# STEP 1.5: Pilih perusahaan dari hasil
# =========================
if st.session_state.step == 1.5:
    st.title("Step 1️⃣ Pilih Perusahaan dari Hasil")

    if "selected_companies" not in st.session_state:
        st.session_state.selected_companies = {}

    for name, companies in st.session_state.search_results.items():
        st.subheader(f"Hasil pencarian: {name}")

        if not companies:
            st.warning("❌ Tidak ditemukan")
            continue

        if len(companies) == 1:
            c = companies[0]
            st.session_state.selected_companies[name] = c["id"]

            with st.expander(c.get("name", "-"), expanded=True):
                st.markdown(f"**ID:** {c.get('id', '-')}")
                st.markdown(f"**Alamat:** {c.get('address', '-')}")
                st.markdown(f"**NIB:** {c.get('nib', '-')}")
                st.success("✅ Dipilih otomatis")

        else:
            for c in companies:
                with st.expander(c.get("name", "-")):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**ID:** {c.get('id', '-')}")
                        st.markdown(f"**Alamat:** {c.get('address', '-')}")
                        st.markdown(f"**NIB:** {c.get('nib', '-')}")

                    with col2:
                        if st.button(f"Pilih", key=f"pilih_{c['id']}"):
                            st.session_state.selected_companies[name] = c["id"]
                            st.success(f"✅ {c.get('name')} dipilih")

    if st.button("Lanjut ke Step 2"):
        st.session_state.step = 2
        st.rerun()

# =========================
# STEP 2: Ambil Data Pekerja
# =========================
if st.session_state.step == 2:
    st.title("Step 2️⃣ Ambil Data Pekerja")

    if st.button("Ambil Data"):
        for f in glob.glob("*.json"):
            os.remove(f)

        for nama, cid in st.session_state.selected_companies.items():
            base_url = f"{BASE_URL}/{cid}/employees"
            page = 1
            employees = []

            while True:
                url = f"{base_url}?page={page}"
                res = requests.get(url, headers=get_headers())
                data = res.json()
                if not data.get("data"):
                    break
                employees.extend(data["data"])
                page += 1

            safe_name = nama.replace(" ", "_")
            filename = f"data_perusahaan/{safe_name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(employees, f, ensure_ascii=False, indent=2)

            st.success(f"📁 {nama}: {len(employees)} pekerja tersimpan")

        st.session_state.step = 3
        st.rerun()

# =========================
# STEP 3: Proses ke Excel
# =========================
elif st.session_state.step == 3:
    st.title("Step 3️⃣ Proses ke Excel")

    all_excel_files = []

    for nama in st.session_state.selected_companies.keys():
        safe_name = nama.replace(" ", "_")
        filepath = os.path.join("data_perusahaan", f"{safe_name}.json")

        if not os.path.exists(filepath):
            st.warning(f"⚠️ Data {nama} tidak ditemukan (belum ada file JSON)")
            continue

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            st.warning(f"⚠️ {nama} tidak ada pekerja")
            continue

        result = []
        for i, emp in enumerate(data, start=1):
            result.append({
                "#": str(i),
                "BADAN HUKUM": "-",
                "NAMA PERUSAHAAN": nama,
                "NO. KTP (NIK)": str(emp.get("employable", {}).get("id_number")),
                "NAMA PEGAWAI": str(emp.get("name")),
                "JENIS KELAMIN": gender_map.get(emp.get("gender"), "Tidak Diketahui"),
                "STATUS PERNIKAHAN": "-",
                "ALAMAT KTP": str(emp.get("address", "")),
                "KECAMATAN": "-",
                "ALAMAT DOMISILI": "-",
                "PENDIDIKAN": education_map.get(emp.get("education", {}).get("name")),
                "STATUS": status_map.get(emp.get("status"), emp.get("status")),
                "TAHUN MULAI KERJA": str(emp.get("join_date", "-").split("-")[0] if emp.get("join_date") else "-"),
                "JABATAN": str(emp.get("position", {}).get("name")),
            })

        df = pd.DataFrame(result)
        st.dataframe(df)

        excel_name = f"{safe_name}.xlsx"
        df.to_excel(excel_name, index=False, engine="openpyxl")
        all_excel_files.append(excel_name)

        with open(excel_name, "rb") as f:
            st.download_button(
                label=f"⬇️ Download {nama}.xlsx",
                data=f,
                file_name=excel_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    if all_excel_files:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file in all_excel_files:
                zipf.write(file)
        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Download Semua Perusahaan (ZIP)",
            data=zip_buffer,
            file_name="semua_perusahaan.zip",
            mime="application/zip"
        )