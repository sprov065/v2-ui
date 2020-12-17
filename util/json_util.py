import json


def dumps(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=True, indent=2, separators=(',', ': '))
