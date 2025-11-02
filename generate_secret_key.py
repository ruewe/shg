import secrets
import string
from pathlib import Path

# Pfad zur .env-Datei
env_path = Path(__file__).resolve().parent / ".env"

# Sicheren Key generieren (Django-kompatibel)
def generate_secret_key(length=50):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

# Wenn .env existiert, prüfen ob SECRET_KEY schon drin ist
if env_path.exists():
    with open(env_path, "r") as f:
        lines = f.readlines()
        if any(line.startswith("SECRET_KEY=") for line in lines):
            print("✅ SECRET_KEY existiert bereits in .env — keine Änderung nötig.")
            exit(0)

# Neuen Key erzeugen und in .env schreiben
key = generate_secret_key()
with open(env_path, "a") as f:
    f.write(f"\nSECRET_KEY={key}\n")

print(f"🔐 Neuer SECRET_KEY wurde in {env_path.name} geschrieben.")
