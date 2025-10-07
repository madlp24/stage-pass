import os

# ================================
# 🌍 Django Environment Variables
# ================================

# --- Security ---
# Generate your own key:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
os.environ.setdefault("SECRET_KEY", "Monteoscuro")

# --- Allowed hosts ---
os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000")

# (Optional) Debug locally
os.environ.setdefault("DEBUG", "True")

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
