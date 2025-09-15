import os
import json
import pandas as pd

# === mapping data ===
gender_map = {0: "Laki-laki", 1: "Perempuan"}
status_map = {0: "Tenaga Kerja PKWT", 1: "Tenaga Kerja Tetap"}
education_map = {
    "S1": "Strata 1", "S2": "Strata 2", "S3": "Strata 3",
    "SD": "SD/MI/Sederajat", "SMP": "SLTP/MTs/Sederajat",
    "SMA": "SLTA / MA / Sederajat", "SMK": "SMK / Sederajat",
    "D1": "Diploma 1", "D2": "Diploma 2", "D3": "Diploma 3", "D4": "Diploma 4",
}

# === folder input & output ===
INPUT_DIR = "data_perusahaan"
OUTPUT_DIR = "data_pekerja"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_json_to_excel():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    if not files:
        print("⚠️ Tidak ada file JSON perusahaan di folder", INPUT_DIR)
        return

    for file in files:
        filepath = os.path.join(INPUT_DIR, file)
        nama = os.path.splitext(file)[0].replace("_", " ")

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        if not data or "data" not in data:
            print(f"⚠️ {nama}: tidak ada data pekerja")
            continue

        result = []
        for i, emp in enumerate(data["data"], start=1):
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

        outpath = os.path.join(OUTPUT_DIR, f"{os.path.splitext(file)[0]}.xlsx")
        df.to_excel(outpath, index=False)

        print(f"📁 {nama}: Excel tersimpan di {outpath}")

if __name__ == "__main__":
    process_json_to_excel()