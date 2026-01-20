import json
from datetime import datetime

def json_log(msg: str, **kwargs) -> str:
	payload = {"msg": msg, "at": datetime.utcnow().isoformat()}
	payload.update(kwargs)
	return json.dumps(payload)
