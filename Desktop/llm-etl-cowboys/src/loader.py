import os, json, pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

DDL = """
-- Optional: run once in Supabase SQL editor if table doesn't exist.
create table if not exists {table_name} (
  season int primary key,
  team text not null,
  wins int not null,
  losses int not null,
  ties int not null,
  points_for int not null,
  points_against int not null,
  division_place text,
  coach text,
  playoffs text,
  source_url text,
  extracted_at timestamptz not null,
  updated_at timestamptz not null default now()
);
"""

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise SystemExit("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    return create_client(url, key)

def ensure_table_exists_hint(table_name: str):
    print("If table is missing, create it with:\n", DDL.format(table_name=table_name))

def load_json_to_supabase(json_path: str, table_name: str):
    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    df = pd.DataFrame(payload.get("records", []))
    if df.empty:
        print("No records to upsert.")
        return

    sb = get_client()
    ensure_table_exists_hint(table_name)

    records = df.to_dict(orient="records")
    # Upsert by primary key "season"
    res = sb.table(table_name).upsert(records, on_conflict="season").execute()
    return res

if __name__ == "__main__":
    load_dotenv()
    table = os.getenv("TABLE_NAME", "cowboys_seasons")
    res = load_json_to_supabase("data/structured.json", table)
    print("Upsert done.")
