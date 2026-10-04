# SaySo — تعلّم الإنجليزية من العربية

505 مثلًا عربيًا مع نظيره الإنجليزي في 11 فئة، مع بحث يتجاهل التشكيل، نطق، اختبارات، بطاقات تعليمية، تمرين كتابة، مفضلة وتتبّع تقدّم. يعمل دون اتصال (PWA).

## التشغيل
```bash
pip install -r requirements.txt
python build.py        # يتحقق من البيانات ويولّد assets/js/data.js
python app.py          # http://localhost:5000
python -m unittest discover -s tests
```
يمكن أيضًا فتح `index.html` مباشرة بعد `python build.py` (الموقع ثابت ولا يحتاج خادمًا).

## هيكل المشروع
| الملف | الدور |
|---|---|
| `data/phrases.json` | **المصدر الوحيد لبيانات SaySo** — عدّل هنا فقط |
| `phrases_core.py` | التطبيع والبحث والتحقق (مشترك) |
| `build.py` | التحقق + توليد `data.js` + تحديث كاش `sw.js` |
| `app.py` | خادم Flask وواجهة API |
| `tests/test_data.py` | اختبارات البيانات والـ API |
| `assets/css/style.css` | نظام التصميم (فاتح/داكن) |
| `assets/js/common.js` | الحالة والبحث والبطاقات والترويسة |

## تبديل اللغة
زر «EN / ع» في الترويسة يبدّل واجهة الموقع بين العربية والإنجليزية (النصوص في `D` داخل `assets/js/common.js`).

## إضافة مثل جديد
أضف كائنًا إلى `data/phrases.json` بالحقول `arabic, english, category` ثم شغّل `python build.py`.

## واجهة API
`/api/search?q=&c=&limit=&offset=` · `/api/categories` · `/api/category/<name>` · `/api/random` · `/api/daily` · `/api/quiz?n=10&c=` · `/api/stats` · `/api/export` · `/api/health`
