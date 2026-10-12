# 查出 index.html 裡每個 NAVER 地圖連結的名稱與座標，寫成 NMAP 對照表，讓 App 能直接用 nmap:// 打開
# 用法：python tools/build_nmap.py   （只會查表裡還沒有的地點）
import html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
# 地鐵站連結（stationId）查不到座標，改用 App 內搜尋站名
STATIONS = {"211": "성수역", "239": "홍대입구역", "424": "명동역", "630": "이태원역", "631": "한강진역"}


def get(url, follow=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if not follow:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        opener = urllib.request.build_opener(NoRedirect)
        try:
            opener.open(req, timeout=20)
        except urllib.error.HTTPError as e:
            return e.headers.get("Location", "")
        return ""
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def place(pid):
    body = get(f"https://m.place.naver.com/place/{pid}/home")
    i = body.find(f'"PlaceDetailBase:{pid}"')
    if i < 0:
        return None
    chunk = body[i:i + 20000]
    name = json.loads('"' + re.search(r'"name":"((?:[^"\\]|\\.)*)"', chunk).group(1) + '"')
    c = re.search(r'"coordinate":\{[^}]*"x":"([\d.]+)","y":"([\d.]+)"', chunk)
    return [round(float(c.group(2)), 7), round(float(c.group(1)), 7), name] if c else None


def from_query(url):
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    if "stationId" in q:
        return STATIONS.get(q["stationId"][0])
    if "lat" in q and "lng" in q:
        return [float(q["lat"][0]), float(q["lng"][0]), q.get("title", [""])[0]]
    return None


def main():
    src = PAGE.read_text(encoding="utf-8")
    m = re.search(r"^var NMAP=(\{.*\});.*$", src, re.M)
    table = json.loads(m.group(1)) if m else {}
    urls = sorted({html.unescape(u) for u in re.findall(r'https://(?:map\.naver\.com|naver\.me)/[^"\s]*', src)})
    for u in urls:
        s = urllib.parse.urlsplit(u)
        if s.netloc == "naver.me":
            key = "s" + s.path.strip("/")
        elif (pm := re.match(r"/p/entry/place/(\d+)", s.path)):
            key = "p" + pm.group(1)
        elif (q := urllib.parse.parse_qs(s.query)).get("stationId"):
            key = "st" + q["stationId"][0]
        else:
            continue  # /p/search/… 在執行時直接用搜尋字串
        if key in table:
            continue
        try:
            if key[0] == "s" and not key.startswith("st"):
                val = from_query(get(u, follow=False))
            elif key.startswith("st"):
                val = from_query(u)
            else:
                val = place(key[1:])
                time.sleep(0.4)
        except Exception as e:
            print("FAIL", u, e, file=sys.stderr)
            continue
        if val:
            table[key] = val
            print(key, val)
        else:
            print("MISS", u, file=sys.stderr)
    line = "var NMAP=" + json.dumps(table, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "; // NAVER 地圖連結 → [緯度,經度,名稱] 或搜尋字串；由 tools/build_nmap.py 產生"
    if m:
        src = src[:m.start()] + line + src[m.end():]
    else:
        anchor = "var flying=false;"
        assert src.count(anchor) == 1
        src = src.replace(anchor, line + "\n" + anchor)
    PAGE.write_text(src, encoding="utf-8", newline="")
    print(len(table), "entries")


main()
