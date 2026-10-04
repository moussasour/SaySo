"""منطق SaySo المشترك بين الخادم وسكربت البناء والاختبارات."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "phrases.json"
FIELDS = ("arabic", "english", "category")

_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670\u0640]")
_PUNCT = re.compile(r"[^\w\s']", re.UNICODE)


def normalize(text: str) -> str:
    """تجاهل التشكيل وتوحيد الألف والياء والتاء المربوطة وحذف علامات الترقيم."""
    t = _DIACRITICS.sub("", str(text).lower())
    t = re.sub("[إأآٱ]", "ا", t).replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"\s+", " ", _PUNCT.sub(" ", t)).strip()


def load_phrases(path: Path = DATA_FILE) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(phrases: list[dict]) -> list[str]:
    """يعيد قائمة بالمشاكل (فارغة = البيانات سليمة)."""
    errors, seen = [], set()
    for i, p in enumerate(phrases):
        for k in FIELDS:
            if not str(p.get(k, "")).strip():
                errors.append(f"#{i}: الحقل «{k}» فارغ")
        if p.get("arabic") in seen:
            errors.append(f"#{i}: عبارة مكررة «{p.get('arabic')}»")
        seen.add(p.get("arabic"))
    return errors


class Index:
    def __init__(self, phrases: list[dict]):
        self.phrases = [dict(p, id=i) for i, p in enumerate(phrases)]
        self._n = [(normalize(p["arabic"]), normalize(p["english"]),
                    normalize(f'{p["arabic"]} {p["english"]}')) for p in self.phrases]
        self.categories = list(dict.fromkeys(p["category"] for p in self.phrases))

    def search(self, q: str = "", category: str = "") -> list[dict]:
        n = normalize(q)
        toks = n.split()
        scored = []
        for p, (a, e, allt) in zip(self.phrases, self._n):
            if category and p["category"] != category:
                continue
            if toks and not all(t in allt for t in toks):
                continue
            s = (100 if n in (a, e) else 0) + (40 if n and (a.startswith(n) or e.startswith(n)) else 0) \
                + (20 if n and (n in a or n in e) else 0)
            scored.append((s, p["id"], p))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [p for _, _, p in scored]

    def stats(self) -> dict:
        c = Counter(p["category"] for p in self.phrases)
        return {"total": len(self.phrases), "categories": [{"name": k, "count": c[k]} for k in self.categories]}
