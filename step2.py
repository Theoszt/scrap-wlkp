import streamlit as st
import json
import os

BASE_DIR = "list_perusahaan"
SELECTED_DIR = "selected_companies"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(SELECTED_DIR, exist_ok=True)

# cek folder hasil pencarian (list_perusahaan)
existing_folders = [int(f) for f in os.listdir(BASE_DIR) if f.isdigit()]
if not existing_folders:
    st.error("⚠️ Belum ada data di list_perusahaan. Jalankan step 1 dulu!")
    st.stop()

latest_folder = str(max(existing_folders))
base_dir = os.path.join(BASE_DIR, latest_folder)

# tentuin sekali aja folder tujuan untuk hasil pilihan
if "selected_dir" not in st.session_state:
    selected_folders = [int(f) for f in os.listdir(SELECTED_DIR) if f.isdigit()]
    next_id = max(selected_folders) + 1 if selected_folders else 1
    st.session_state["selected_dir"] = os.path.join(SELECTED_DIR, str(next_id))
    os.makedirs(st.session_state["selected_dir"], exist_ok=True)

selected_dir = st.session_state["selected_dir"]

# ambil semua file JSON hasil pencarian
files = [f for f in os.listdir(base_dir) if f.endswith(".json")]
if not files:
    st.error("⚠️ Tidak ada file JSON di folder pencarian!")
    st.stop()

st.title("📋 Pilih Perusahaan per Pencarian")

for f in files:
    filepath = os.path.join(base_dir, f)
    with open(filepath, "r", encoding="utf-8") as jf:
        data = json.load(jf)

    if not data:
        continue

    # ambil nama pencarian (dari nama file)
    search_name = os.path.splitext(f)[0].replace("_", " ")
    st.subheader(f"🔎 Hasil pencarian: **{search_name}**")

    # normalisasi data ke list
    companies = data if isinstance(data, list) else [data]

    # rapikan field yang dibutuhkan
    company_options = [
        {
            "id": c.get("id", "-"),
            "nama": c.get("name", "-"),
            "nib": c.get("nib", "-"),
            "alamat": c.get("address", "-"),
            "kecamatan": c.get("village", {}).get("sub_district", {}).get("name", "-"),
        }
        for c in companies
    ]

    st.dataframe(company_options, use_container_width=True)

    # kalau hasil cuma 1 perusahaan → simpan / batalkan
    if len(company_options) == 1:
        comp = company_options[0]

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💾 Simpan '{comp['nama']}'", key="save_"+f):
                filename = os.path.join(selected_dir, f"{comp['nama'].replace(' ', '_')}.json")
                with open(filename, "w", encoding="utf-8") as out:
                    json.dump(comp, out, ensure_ascii=False, indent=2)
                st.success(f"✅ Perusahaan '{comp['nama']}' disimpan ke folder {selected_dir}")

        with col2:
            if st.button(f"❌ Batalkan", key="cancel_"+f):
                st.warning(f"🚫 Pilihan '{comp['nama']}' dibatalkan. Tidak ada yang disimpan.")

    # kalau hasil lebih dari 1 perusahaan → kasih selectbox
    else:
        selected_name = st.selectbox(
            f"Pilih perusahaan dari '{search_name}':",
            [c["nama"] for c in company_options],
            key="select_"+f,
        )

        if st.button(f"💾 Simpan pilihan dari {search_name}", key="btn_"+f):
            for comp in company_options:
                if comp["nama"] == selected_name:
                    filename = os.path.join(selected_dir, f"{comp['nama'].replace(' ', '_')}.json")
                    with open(filename, "w", encoding="utf-8") as out:
                        json.dump(comp, out, ensure_ascii=False, indent=2)
            st.success(f"✅ Perusahaan '{selected_name}' disimpan ke folder {selected_dir}")

# tombol selesai
if st.button("Selesai"):
    with open("done.flag", "w") as f:
        f.write("ok")
    st.success(f"Step 2 selesai ✅ Semua pilihan tersimpan di folder: {selected_dir}")
    st.stop()