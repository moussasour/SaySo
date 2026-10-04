import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from phrases_core import Index, load_phrases, normalize, validate


class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ph = load_phrases(); cls.ix = Index(cls.ph)

    def test_count_and_valid(self):
        self.assertGreaterEqual(len(self.ph), 500)
        self.assertEqual(validate(self.ph), [])
        self.assertEqual(len(self.ix.categories), 11)
        self.assertTrue(all("meaning" not in p for p in self.ph))

    def test_normalize(self):
        self.assertEqual(normalize("مَرْحَبًا"), normalize("مرحبا"))
        self.assertEqual(normalize("أحمد"), normalize("احمد"))

    def test_search_ignores_tashkeel(self):
        self.assertTrue(self.ix.search("ربّ ضارّة"))
        self.assertEqual(self.ix.search("رُبَّ ضَارَّةٍ")[0]["english"], "Every cloud has a silver lining")

    def test_category_filter(self):
        r = self.ix.search("", "العدل والجزاء")
        self.assertTrue(r and all(p["category"] == "العدل والجزاء" for p in r))


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.ph = load_phrases()
        import app as a
        self.c = a.app.test_client()

    def test_endpoints(self):
        self.assertEqual(self.c.get("/api/health").json["phrases_count"], len(self.ph))
        self.assertGreater(self.c.get("/api/search?q=good").json["total"], 0)
        q = self.c.get("/api/quiz?n=5").json["questions"]
        self.assertEqual(len(q), 5); self.assertTrue(all(len(x["options"]) == 4 for x in q))
        self.assertEqual(self.c.get("/api/category/nope").status_code, 404)
        self.assertEqual(self.c.get("/index.html").status_code, 200)
        self.assertEqual(self.c.get("/data/phrases.json").status_code, 404)


if __name__ == "__main__":
    unittest.main()
