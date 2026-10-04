#!/usr/bin/env python3
"""يتحقق من البيانات ويولّد assets/js/data.js ويحدّث نسخة الكاش في sw.js.

الاستخدام:  python build.py
"""
import hashlib
import json
import re
import sys

from phrases_core import ROOT, load_phrases, validate


def main() -> int:
    phrases = load_phrases()
    errors = validate(phrases)
    if errors:
        print("أخطاء في البيانات:\n  " + "\n  ".join(errors))
        return 1
    clean = [{k: p[k] for k in ("arabic", "english", "category")} for p in phrases]
    body = json.dumps(clean, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "assets" / "js" / "data.js").write_text(
        "/* ملف مولَّد من data/phrases.json بواسطة build.py — لا تعدّله يدويًا */\n"
        f"const PHRASES={body};\n", encoding="utf-8")
    digest = hashlib.sha1(body.encode()).hexdigest()[:8]
    sw = ROOT / "sw.js"
    sw.write_text(re.sub(r"const C='ap-[^']*'", f"const C='ap-{digest}'", sw.read_text(encoding="utf-8")), encoding="utf-8")
    cats = len({p["category"] for p in clean})
    print(f"تم: {len(clean)} عبارة في {cats} فئة (cache ap-{digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
