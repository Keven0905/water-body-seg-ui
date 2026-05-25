import os
import json
import time
from config import Config

HISTORY_FILE = os.path.join(Config.BASE_DIR, 'history.json')
MAX_RECORDS = 200


def _load() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save(records: list):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_record(original_name: str, result_filename: str, composite_filename: str,
               water_ratio: float, water_pixels: int, total_pixels: int) -> dict:
    records = _load()
    record = {
        'id': int(time.time() * 1000),
        'original_name': original_name,
        'result_filename': result_filename,
        'composite_filename': composite_filename,
        'water_ratio': water_ratio,
        'water_pixels': water_pixels,
        'total_pixels': total_pixels,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    records.insert(0, record)
    if len(records) > MAX_RECORDS:
        old = records[MAX_RECORDS:]
        records = records[:MAX_RECORDS]
        for r in old:
            _delete_result_files(r)
    _save(records)
    return record


def _delete_result_files(record: dict):
    for key in ('result_filename', 'composite_filename'):
        fname = record.get(key)
        if fname:
            path = os.path.join(Config.RESULTS_DIR, fname)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


def get_records() -> list:
    return _load()


def delete_record(record_id: int) -> bool:
    records = _load()
    target = None
    for r in records:
        if r['id'] == record_id:
            target = r
            break
    if not target:
        return False
    records.remove(target)
    _save(records)
    _delete_result_files(target)
    return True


def get_record_by_id(record_id: int) -> dict | None:
    for r in _load():
        if r['id'] == record_id:
            return r
    return None
