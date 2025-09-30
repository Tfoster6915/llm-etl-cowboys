import os, json, re
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

def strict_json(s: str):
    m = re.search(r'(\[.*\]|\{.*\})', s, flags=re.S)
    if not m:
        raise ValueError("No JSON found in model response.")
    return json.loads(m.group(1))

PROMPT_TMPL = """You are given raw text scraped from a Dallas Cowboys seasons page (may be Wikipedia or a stats site).
Extract a JSON ARRAY where each element is ONE SEASON record with EXACT keys:

season (integer),
team (string, 'Dallas Cowboys'),
wins (integer),
losses (integer),
ties (integer, 0 if none),
points_for (integer),
points_against (integer),
division_place (short string like '1st NFC East'),
coach (string or 'Unknown'),
playoffs (string summary like 'Missed Playoffs', 'Lost Wild Card', 'Won Super Bowl'),
source_url (string),
extracted_at (UTC ISO 8601 timestamp).

Rules:
- Parse as many seasons as clearly present (recent decades are enough).
- Integers for numeric fields; fill missing numeric with 0 and missing strings with 'Unknown'.
- Output ONLY valid JSON (no markdown, no commentary).

Text:
---
{blob}
---
"""

def run_structurer(blob_path: str, source_url: str, model: str, base_url: str, api_key: str):
    # 1) read blob
    with open(blob_path, "r", encoding="utf-8") as f:
        blob = f.read()

    # 2) call OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    msg = PROMPT_TMPL.format(blob=blob[:12000])  # keep prompt reasonably small
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": msg}],
        temperature=0.1,
    )
    raw = resp.choices[0].message.content

    # 3) parse + normalize
    arr = strict_json(raw)
    if not isinstance(arr, list) or not arr:
        raise ValueError("Expected a non-empty JSON array.")

    now = datetime.now(timezone.utc).isoformat()
    for rec in arr:
        rec.setdefault("team", "Dallas Cowboys")
        rec.setdefault("source_url", source_url)
        rec.setdefault("extracted_at", now)
        for k in ["wins", "losses", "ties", "points_for", "points_against"]:
            rec[k] = int(rec.get(k, 0) or 0)
        rec["season"] = int(rec["season"])
        for k in ["division_place", "coach", "playoffs"]:
            rec[k] = rec.get(k) or "Unknown"

    # 4) write out
    os.makedirs("data", exist_ok=True)
    out = {"records": arr}
    with open("data/structured.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    return out

if __name__ == "__main__":
    load_dotenv()
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    source_url = os.getenv("SOURCE_URL", "")

    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY")
    if not source_url:
        raise SystemExit("Missing SOURCE_URL")

    res = run_structurer("data/raw_blob.txt", source_url, model, base_url, api_key)
    print(f"Wrote data/structured.json with {len(res['records'])} records.")
