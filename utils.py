import hmac, hashlib, json
from urllib.parse import parse_qsl
from config import settings

def verify_telegram_init_data(init_data: str) -> dict | None:
    if not init_data:
        return None
    try:
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        if "hash" not in parsed_data:
            return None
        received_hash = parsed_data.pop("hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated_hash == received_hash:
            return json.loads(parsed_data.get("user", "{}"))
        return None
    except Exception:
        return None
