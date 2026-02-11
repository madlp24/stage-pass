import os

# ================================
# 🌍 Django Environment Variables
# ================================

# --- Security ---
os.environ.setdefault("SECRET_KEY", "u29k7i@ub!)gdj++qrx=e$87bvuj3l9b-x6vcao)=ov8js-u1_")

# --- Allowed hosts ---
os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000")


# ================================
# 🗄️ Database (PostgreSQL - Neon)
# ================================
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_xqn7Vw9fjueP@ep-muddy-river-agv7gk2y.c-2.eu-central-1.aws.neon.tech/fray_power_walk_623225"
)

# ================================
# ☁️ Cloudinary
# ================================

os.environ.setdefault(
    "CLOUDINARY_URL",
    "cloudinary://787422981385836:kXkciLYJ1K_nHZGR8zCiQw5Ai_s@dxttrchtg"
)