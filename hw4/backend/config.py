"""application configuration loaded from the class-root .env file."""
import os
from pathlib import Path
from dotenv import load_dotenv

# backend/ -> Homework 4/ -> AI Foundations/ (class root holds the shared .env)
backend_dir = Path(__file__).resolve().parent
project_dir = backend_dir.parent
class_root = project_dir.parent

# load the shared class .env (keeps the portkey key out of the repo)
load_dotenv(class_root / ".env")
load_dotenv(project_dir / ".env", override=False)

portkey_api_key = os.environ.get("PORTKEY_API_KEY", "")
portkey_base_url = os.environ.get("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")
portkey_provider = os.environ.get("PORTKEY_PROVIDER", "openai")

# a capable 5.6-series model for the shopping agent
chat_model = os.environ.get("CAMPUS_CHAT_MODEL", "5.6luna")

# auth settings
jwt_secret = os.environ.get("CAMPUS_JWT_SECRET", "dev-secret-change-me")
jwt_algorithm = "HS256"
jwt_ttl_hours = int(os.environ.get("CAMPUS_JWT_TTL_HOURS", "72"))
pbkdf2_iterations = int(os.environ.get("CAMPUS_PBKDF2_ITERATIONS", "200000"))
# the seed users' hashes do not record their iteration count, so login accepts any
# of these common PBKDF2 cost presets. the primary cost above is always used when
# writing a new account. override/extend with a comma-separated env var if needed.
_extra = os.environ.get("CAMPUS_PBKDF2_ACCEPT", "")
pbkdf2_accept_iterations = []
for _value in [str(pbkdf2_iterations)] + _extra.split(",") + [
    "600000", "390000", "320000", "260000", "210000", "180000",
    "150000", "120000", "100000", "50000", "29000", "10000", "1000",
]:
    _value = _value.strip()
    if _value.isdigit() and int(_value) not in pbkdf2_accept_iterations:
        pbkdf2_accept_iterations.append(int(_value))

# data locations (database + product images live outside git)
db_path = Path(os.environ.get("CAMPUS_DB_PATH", project_dir / "data" / "campus_customs.db"))
products_dir = Path(os.environ.get("CAMPUS_PRODUCTS_DIR", project_dir / "data" / "products"))
