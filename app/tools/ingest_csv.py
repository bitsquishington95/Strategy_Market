import csv
import json
import os
from typing import Dict, Any, List


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
CEOS_CSV = os.path.join(DATA_DIR, "ceos.csv")
SITUATIONS_CSV = os.path.join(DATA_DIR, "situations.csv")
OUTPUT_JSON = os.path.join(DATA_DIR, "repository.json")


def set_nested(obj: Dict[str, Any], dotted_key: str, value: str) -> None:
	parts: List[str] = dotted_key.split(".")
	cursor: Dict[str, Any] = obj
	for key in parts[:-1]:
		if key not in cursor or not isinstance(cursor[key], dict):
			cursor[key] = {}
		cursor = cursor[key]
	cursor[parts[-1]] = value


def load_ceos() -> List[Dict[str, Any]]:
	profiles: List[Dict[str, Any]] = []
	with open(CEOS_CSV, "r", encoding="utf-8", newline="") as f:
		reader = csv.DictReader(f)
		for row in reader:
			profile: Dict[str, Any] = {}
			for k, v in row.items():
				if v is None or v == "":
					continue
				if k == "name":
					set_nested(profile, k, v)
				else:
					set_nested(profile, k, v)
			profiles.append(profile)
	return profiles


def load_situations() -> List[Dict[str, Any]]:
	items: List[Dict[str, Any]] = []
	with open(SITUATIONS_CSV, "r", encoding="utf-8", newline="") as f:
		reader = csv.DictReader(f)
		for row in reader:
			ceo = (row.get("ceo") or "").strip()
			tags_raw = (row.get("tags") or "").strip()
			title = (row.get("title") or "").strip()
			response = (row.get("response") or "").strip()
			if not ceo or not title or not response:
				continue
			# accept comma or semicolon separated tags
			delims = ",;"
			for d in delims:
				tags_raw = tags_raw.replace(d, ",")
			tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
			items.append({"ceo": ceo, "tags": tags, "title": title, "response": response})
	return items


def main() -> int:
	ceos = load_ceos()
	situations = load_situations()
	data = {"ceos": ceos, "situations": situations}
	os.makedirs(DATA_DIR, exist_ok=True)
	with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	print(f"Wrote {OUTPUT_JSON} with {len(ceos)} CEO profiles and {len(situations)} situations.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
