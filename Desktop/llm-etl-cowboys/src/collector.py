import os, requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from .utils import ensure_dir

def fetch_webpage_blob(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # Strip non-visible elements
    for s in soup(["script", "style", "noscript"]):
        s.extract()
    # Get page text (including tables rendered as text)
    text = soup.get_text(separator=" ", strip=True)
    return text

def collect_blob(source_url: str, outpath: str = "data/raw_blob.txt") -> str:
    ensure_dir("data")
    blob = fetch_webpage_blob(source_url)
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(blob)
    return outpath

if __name__ == "__main__":
    load_dotenv()
    source_url = os.getenv("SOURCE_URL")
    if not source_url:
        raise SystemExit("Missing SOURCE_URL in .env")
    path = collect_blob(source_url, "data/raw_blob.txt")
    print(f"Saved blob to {path} from {source_url} at {datetime.utcnow().isoformat()}Z")
