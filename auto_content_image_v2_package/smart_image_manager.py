# smart_image_manager.py — lightweight image assignment with infographic fallback
import os, io, json, hashlib, time, re
from pathlib import Path
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except Exception:
    PIL_OK = False

ROOT = Path(".")
STATIC_DIR = ROOT / "static" / "images"
DB_DIR = ROOT / "data"; DB_DIR.mkdir(parents=True, exist_ok=True)
USAGE_DB = DB_DIR / "images_usage.json"; META_DB = DB_DIR / "images_meta.json"

def _load_json(path, default):
    if path.exists():
        try: return json.loads(path.read_text(encoding="utf-8"))
        except Exception: return default
    return default

def _save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _hash_bytes(b: bytes): import hashlib; return hashlib.sha1(b).hexdigest()
def _ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

def _token_set(*parts):
    toks=[]; 
    for p in parts:
        if not p: continue
        p = re.sub(r"[^\w\-\s]", " ", str(p).lower())
        toks += [t for t in p.split() if t and len(t)>2]
    return set(toks)

def _score(tokens, meta):
    overlap = len(tokens & set(meta.get("tags", [])))
    bonus = 1 if meta.get("scene") in ("installation","energy","compatibility") else 0
    used = meta.get("used", 0)
    penalty = 2.0 if used >= 3 else 0.0
    return overlap + bonus - penalty

def _infographic(category: str, summary: str, size=(1280,720)):
    if not PIL_OK: return None, None
    W,H = size; from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (W,H), (255,255,255)); d = ImageDraw.Draw(im)
    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
        font_sm = ImageFont.truetype("DejaVuSans.ttf", 36)
    except Exception:
        font_big = font_sm = None
    d.text((60,60), f"{category.title()} — Specs Overview", fill=(0,0,0), font=font_big)
    s = re.sub(r"\s+"," ", summary or "").strip()
    y=160
    for ln in [s[i:i+70] for i in range(0, len(s), 70)][:8]:
        d.text((60,y), ln, fill=(0,0,0), font=font_sm); y+=48
    import io; b=io.BytesIO(); im.save(b, format="WEBP", quality=92, method=6); data=b.getvalue()
    return data, {"width":W, "height":H}

def _write_image(category: str, data: bytes, w: int, h: int):
    hsh = _hash_bytes(data)[:8]
    folder = STATIC_DIR / category.replace("_","-"); _ensure_dir(folder)
    name = f"{hsh}_{w}x{h}.webp"; (folder/name).write_bytes(data)
    return f"/images/{category.replace('_','-')}/{name}"

def _record_meta(url, alt, caption, credit, license):
    m = _load_json(META_DB, {}); m[url] = {"alt":alt,"caption":caption,"credit":credit,"license":license,"updated_at":int(time.time())}; _save_json(META_DB, m)
def _bump_usage(url):
    u = _load_json(USAGE_DB, {}); u[url] = u.get(url,0)+1; _save_json(USAGE_DB, u)

def search_and_assign(keyword: str, category: str, needs=None, why_selected: dict=None):
    needs = needs or {"hero":1,"inline":2}
    tokens = _token_set(keyword, category, (why_selected or {}).get("intent",""))
    assignment = {"hero": None, "inline": []}
    folder = STATIC_DIR / category.replace("_","-"); candidates=[]
    if folder.exists():
        usage = _load_json(USAGE_DB, {})
        for p in folder.glob("*.webp"):
            url = f"/images/{category.replace('_','-')}/{p.name}"
            meta = {"url": url, "tags": list(tokens), "scene":"compatibility", "used": usage.get(url,0)}
            meta["score"] = _score(tokens, meta); candidates.append(meta)
    if not candidates:
        data, sz = _infographic(category, (why_selected or {}).get("trend","")+"; "+(why_selected or {}).get("difficulty",""))
        if data:
            url = _write_image(category, data, sz["width"], sz["height"])
            alt = f"{category} specs and decision points"; cap = "Infographic based on public specifications."
            _record_meta(url, alt, cap, "AI Smart Home Hub", "CC BY 4.0"); _bump_usage(url)
            assignment["hero"] = {"src": url, "alt": alt, "caption": cap, "credit":"AI Smart Home Hub", "license":"CC BY 4.0"}
    candidates.sort(key=lambda m: (-m.get("score",0), m.get("used",0)))
    for meta in candidates:
        if not assignment["hero"]:
            alt = f"{category} compatibility / install overview"
            _record_meta(meta["url"], alt, "Category visual", "AI Smart Home Hub", "CC BY 4.0"); _bump_usage(meta["url"])
            assignment["hero"] = {"src": meta["url"], "alt": alt, "caption":"Category visual", "credit":"AI Smart Home Hub", "license":"CC BY 4.0"}
            continue
        if len(assignment["inline"]) < needs.get("inline",2):
            alt = f"{keyword} key points illustration"
            _record_meta(meta["url"], alt, "Illustration", "AI Smart Home Hub", "CC BY 4.0"); _bump_usage(meta["url"])
            assignment["inline"].append({"src": meta["url"], "alt": alt, "caption":"Illustration", "credit":"AI Smart Home Hub", "license":"CC BY 4.0"})
        if assignment["hero"] and len(assignment["inline"]) >= needs.get("inline",2):
            break
    return assignment