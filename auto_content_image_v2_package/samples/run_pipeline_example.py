
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from smart_image_manager import search_and_assign

tp = json.loads((ROOT/'samples'/'top_picks_example.json').read_text(encoding='utf-8'))[0]
out = search_and_assign(tp['keyword'], tp['category'], {'hero':1,'inline':2}, tp.get('why_selected'))
print(json.dumps(out, ensure_ascii=False, indent=2))
