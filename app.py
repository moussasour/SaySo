#!/usr/bin/env python3
"""خادم Flask: يقدّم الموقع + واجهة API للبحث والاختبارات.

التشغيل:  python app.py   ثم افتح http://localhost:5000
"""
import json
import random
from datetime import date, datetime

from flask import Flask, abort, jsonify, request, send_from_directory

from phrases_core import ROOT, Index, load_phrases

app = Flask(__name__, static_folder=None)
app.json.ensure_ascii = False
INDEX = Index(load_phrases())
PAGES = {"", "index.html", "phrases.html", "practice.html", "favorites.html"}


def _page_args(default=24, cap=100):
    try:
        limit = max(1, min(int(request.args.get("limit", default)), cap))
        offset = max(0, int(request.args.get("offset", 0)))
    except ValueError:
        abort(400, "limit/offset must be integers")
    return limit, offset


# ---------- الموقع ----------
@app.get("/")
@app.get("/<path:name>")
def site(name="index.html"):
    if name.startswith(("api/", "data/")) or name.endswith(".py"):
        abort(404)
    return send_from_directory(ROOT, name or "index.html")


# ---------- API ----------
@app.get("/api/search")
def api_search():
    limit, offset = _page_args()
    res = INDEX.search(request.args.get("q", ""), request.args.get("c", ""))
    return jsonify(total=len(res), limit=limit, offset=offset, results=res[offset:offset + limit])


@app.get("/api/categories")
def api_categories():
    return jsonify(INDEX.stats())


@app.get("/api/category/<name>")
def api_category(name):
    res = INDEX.search("", name)
    if not res:
        abort(404, "unknown category")
    return jsonify(category=name, count=len(res), phrases=res)


@app.get("/api/random")
def api_random():
    return jsonify(random.choice(INDEX.search("", request.args.get("c", "")) or abort(404)))


@app.get("/api/daily")
def api_daily():
    return jsonify(INDEX.phrases[(date.today().toordinal() * 7919) % len(INDEX.phrases)])


@app.get("/api/quiz")
def api_quiz():
    """اختبار اختيار من متعدد: n أسئلة × 4 خيارات (الخيارات من نفس الفئة أولًا)."""
    n = min(max(request.args.get("n", 10, type=int), 1), 30)
    pool = INDEX.search("", request.args.get("c", ""))
    questions = []
    for p in random.sample(pool, min(n, len(pool))):
        same = [x for x in INDEX.phrases if x["category"] == p["category"] and x["english"] != p["english"]]
        rest = [x for x in INDEX.phrases if x["english"] != p["english"]]
        options, seen = [], {p["english"]}
        for x in random.sample(same, len(same)) + random.sample(rest, len(rest)):
            if x["english"] not in seen:
                seen.add(x["english"]); options.append(x["english"])
            if len(options) == 3:
                break
        opts = options + [p["english"]]
        random.shuffle(opts)
        questions.append({"id": p["id"], "arabic": p["arabic"], "options": opts, "answer": opts.index(p["english"])})
    return jsonify(questions=questions)


@app.get("/api/stats")
def api_stats():
    return jsonify(INDEX.stats())


@app.get("/api/export")
def api_export():
    return app.response_class(json.dumps(INDEX.phrases, ensure_ascii=False, indent=2),
                              mimetype="application/json",
                              headers={"Content-Disposition": "attachment; filename=phrases.json"})


@app.get("/api/health")
def health():
    return jsonify(status="healthy", timestamp=datetime.now().isoformat(), phrases_count=len(INDEX.phrases))


@app.errorhandler(404)
@app.errorhandler(400)
def err(e):
    return jsonify(error=getattr(e, "description", str(e))), e.code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
