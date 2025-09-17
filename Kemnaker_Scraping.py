import subprocess

files = [
    ("step1.py", "python"),
    ("step2.py", "streamlit"),
    ("step3.py", "python"),
    ("step4.py", "python"),
]

for f, mode in files:
    print(f"▶️ Jalanin {f} dengan {mode}")
    if mode == "python":
        subprocess.run(["python", f], check=True)
    elif mode == "streamlit":
        proc = subprocess.Popen(["python", "-m", "streamlit", "run", f])
        print("🚀 Streamlit jalan. Tunggu sampai user selesai...")

        import time, os
        while not os.path.exists("done.flag"):
            time.sleep(2)

        print("✅ Step2 selesai")
        proc.terminate()
        proc.wait()