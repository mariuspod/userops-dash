import gzip
import json
import requests
import os
from typing import Dict, List
from ape.logging import logger

BASE_URL = os.environ.get('VM_URL', 'http://victoria-metrics:8428')
IMPORT_URL = f'{BASE_URL}/api/v1/import'
VM_REQUEST_HEADERS = {'Content-Encoding': 'gzip'}

def track(name: str, user_ops: Dict, chain_id: int):
    metrics = []
    for ts, counters in user_ops.items():
        ts_millis = ts * 1000
        for label in ["biconomy", "others"]:
            num = counters[label]
            m = {
                "metric": {
                    "__name__": name,
                    "chain_id": str(chain_id),
                    "biconomy": str(label == "biconomy").lower(),
                },
                "values": [num],
                "timestamps": [ts_millis],
            }
            metrics.append(m)
    _post(metrics)

def has_data(name: str, ts: int) -> bool:
    url = f'{BASE_URL}/api/v1/query?query={name}&time={int(ts)}'
    response = requests.get(url)
    result = response.json()
    return result['status'] == 'success' and len(result['data']['result']) > 0

def _to_jsonl_gz(metrics_to_export: List[Dict]):
    lines = []
    for item in metrics_to_export:
        lines.append(json.dumps(item))

    jsonlines = "\n".join(lines)
    return gzip.compress(bytes(jsonlines, "utf-8"))


def _post(metrics_to_export: List[Dict]) -> None:
    data = _to_jsonl_gz(metrics_to_export)
    attempts = 0
    while True:
        try:
            requests.post(
                url = IMPORT_URL,
                headers = VM_REQUEST_HEADERS,
                data = data,
            )
            return
        except Exception as e:
            attempts += 1
            logger.error(e)
            if attempts >= 3:
                raise e

