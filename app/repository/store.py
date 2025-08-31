import json
import os
import re
from collections import defaultdict
from typing import DefaultDict, Dict, List

from app.models.profile import RepositoryData


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)


class Repository:
    def __init__(self, data: RepositoryData):
        self._data = data
        self._ceo_by_name = {c.name: c.model_dump() for c in data.ceos}
        self._situations = [s.model_dump() for s in data.situations]

    def list_ceo_names(self) -> List[str]:
        return list(self._ceo_by_name.keys())

    def get_ceo(self, name: str) -> Dict:
        return self._ceo_by_name.get(name)

    def query_by_situation(self, user_query: str) -> Dict[str, List[Dict]]:
        q = user_query.lower()
        buckets: DefaultDict[str, List[Dict]] = defaultdict(list)
        for s in self._situations:
            matchable = " ".join(s.get("tags", [])).lower()
            if any(token in matchable for token in re.findall(r"[\w/-]+", q)):
                buckets[s["ceo"]].append(s)
        return buckets


def load_repository() -> "Repository":
    with open(os.path.join(DATA_DIR, "repository.json"), "r", encoding="utf-8") as f:
        raw = json.load(f)
    data = RepositoryData.model_validate(raw)
    return Repository(data)


