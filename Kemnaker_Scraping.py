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
        subprocess.run(["python", "-m", "streamlit", "run", f], check=True)