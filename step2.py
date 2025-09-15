import streamlit as st
import json, os
import sys

BASE_DIR = "list_perusahaan"
SELECTED_DIR = "selected_companies"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(SELECTED_DIR, exist_ok=True)

# Cari folder pencarian terakhir
existing_folders = [int(f) for f in os.listdir(BASE_DIR) if f.isdigit()]
if not existing_folders:
    st.error("⚠️ Belum ada hasil pencarian di folder data_perusahaan")
    st.stop()

latest_folder = str(max(existing_folders))
search_dir = os.path.join(BASE_DIR, latest_folder)

# Ambil semua file JSON hasil search (tiap file = hasil 1 kata pencarian)
files = [f for f in os.listdir(search_dir) if f.endswith(".json")]
if not files:
    st.error(f"⚠️ Tidak ada file JSON di {search_dir}")
    st.stop()

st.title("📋 Pilih Perusahaan per Pencarian")

for file in files:
    filepath = os.path.join(search_dir, file)
    with open(filepath, encoding="utf-8") as f:
        companies = json.load(f)

    if not companies:
        continue

    # Nama pencarian dari nama file (misalnya: cgv.json → "cgv")
    search_name = file.replace(".json", "").replace("_", " ")

    st.subheader(f"🔎 Hasil pencarian: **{search_name}**")

    company_options = [
        {
            "id": c.get("id", "-"),
            "nama": c.get("name", "-"),
            "nib": c.get("nib", "-"),
            "alamat": c.get("address", "-"),
            "kecamatan": c.get("district", "-"),
        }
        for c in companies
    ]

    st.dataframe(company_options, use_container_width=True)

    if len(company_options) == 1:
        comp = company_options[0]
        filename = os.path.join(
            SELECTED_DIR, f"{comp['nama'].replace(' ', '_')}.json"
        )
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(comp, f, ensure_ascii=False, indent=2)
        st.success(f"✅ Perusahaan '{comp['nama']}' otomatis disimpan ke folder {SELECTED_DIR}")

    else:
        selected_name = st.selectbox(
        f"Pilih perusahaan dari '{search_name}':",
        [c["nama"] for c in company_options],
        key=file,
        )

        if st.button(f"💾 Simpan pilihan dari {search_name}", key="btn_"+file):
            for comp in company_options:
                if comp["nama"] in selected_name:
                    filename = os.path.join(
                        SELECTED_DIR, f"{comp['nama'].replace(' ', '_')}.json"
                    )
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(comp, f, ensure_ascii=False, indent=2)

            st.success(f"✅ {len(selected_name)} perusahaan dari '{search_name}' disimpan ke folder {SELECTED_DIR}")