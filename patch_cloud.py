from pathlib import Path

app = Path("frontend/app.py")
s = app.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1. Add backend imports after the existing imports
# ------------------------------------------------------------

anchor = "from textwrap import dedent\n"

imports = """from textwrap import dedent

import sys
from pathlib import Path as _Path

PROJECT_ROOT = _Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.mandi_service import get_mandi_prices
from backend.irrigation_service import get_irrigation_recommendation
from backend.model_service import price_prediction_service
"""

if anchor not in s:
    raise SystemExit("Import anchor not found")

s = s.replace(anchor, imports, 1)

# ------------------------------------------------------------
# 2. Replace localhost API configuration
# ------------------------------------------------------------

old_api = 'API_BASE = "http://127.0.0.1:8000"'

new_api = """# Backend services run inside the Streamlit deployment.
API_BASE = None"""

if old_api not in s:
    raise SystemExit("API_BASE line not found")

s = s.replace(old_api, new_api, 1)

# ------------------------------------------------------------
# 3. Locate the existing API helper functions
# ------------------------------------------------------------

start = s.find("def api_get(")

if start == -1:
    raise SystemExit("api_get function not found")

end_marker = "\n# ============================================================\n# MANDI DATA"

end = s.find(end_marker, start)

if end == -1:
    raise SystemExit("MANDI DATA section not found")

# ------------------------------------------------------------
# 4. Replace HTTP helpers with direct backend service calls
# ------------------------------------------------------------

new_helpers = '''def api_get(endpoint, params=None, timeout=70):
    try:
        params = params or {}

        if endpoint == "/market-price":
            return get_mandi_prices(
                state=params.get("state"),
                district=params.get("district"),
                market=params.get("market"),
                commodity=params.get("commodity"),
                limit=int(params.get("limit", 100)),
            )

        if endpoint == "/model-status":
            return {
                "status": "loaded",
                "model": price_prediction_service.model_data["model_name"],
                "features": len(price_prediction_service.features),
            }

        return {
            "status": "error",
            "message": f"Unsupported backend endpoint: {endpoint}",
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }


def api_post(endpoint, payload, timeout=30):
    try:
        if endpoint == "/irrigation":
            return get_irrigation_recommendation(
                payload.get("weather", {})
            )

        if endpoint == "/predict":
            result = price_prediction_service.predict(payload)
            return {
                "status": "success",
                "prediction": result["prediction"],
                "confidence": result["confidence"],
            }

        return {
            "status": "error",
            "message": f"Unsupported backend endpoint: {endpoint}",
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }

'''

s = s[:start] + new_helpers + s[end:]

app.write_text(s, encoding="utf-8")

# ------------------------------------------------------------
# 5. Patch mandi service for Streamlit Cloud Secrets
# ------------------------------------------------------------

mandi = Path("backend/mandi_service.py")
m = mandi.read_text(encoding="utf-8")

old_key = 'API_KEY = os.getenv("DATA_GOV_API_KEY")'

if old_key in m:
    new_key = '''def _get_api_key():
    key = os.getenv("DATA_GOV_API_KEY")
    if key:
        return key

    try:
        import streamlit as st
        return st.secrets.get("DATA_GOV_API_KEY")
    except Exception:
        return None'''

    m = m.replace(old_key, new_key, 1)

if "def _get_api_key():" not in m:
    raise SystemExit("Could not create _get_api_key")

m = m.replace(
    'if not API_KEY:',
    'api_key = _get_api_key()\n\n    if not api_key:',
    1
)

m = m.replace(
    '"api-key": API_KEY,',
    '"api-key": api_key,',
    1
)

mandi.write_text(m, encoding="utf-8")

print("KISSAN SEVA CLOUD PATCH APPLIED")
