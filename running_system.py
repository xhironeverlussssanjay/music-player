import os
import sys
import subprocess

python_path = r"C:\Users\sirodex\AppData\Local\Programs\Python\Python311\python.exe"

if not os.path.exists(python_path):
    print("❌ Python 3.11 tidak ditemukan di path tersebut!")
    sys.exit(1)

libraries = ["PyQt5", "pygame", "colorama", "requests", "python-dotenv"]

for lib in libraries:
    try:
        __import__(lib)
        print(f"✅ {lib} sudah terinstall")
    except ImportError:
        print(f"📦 {lib} sedang diinstall...")
        subprocess.check_call([python_path, "-m", "pip", "install", lib])

print("\n🚀 Menjalankan SoundWave...\n")
os.system(f'"{python_path}" main.py')