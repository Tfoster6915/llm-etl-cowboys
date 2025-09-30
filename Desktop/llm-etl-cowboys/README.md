\# Dallas Cowboys LLM ETL → Supabase → Streamlit on Modal



This project scrapes Dallas Cowboys stats from \[Pro-Football-Reference](https://www.pro-football-reference.com/teams/dal/), structures the raw text into JSON using an LLM (OpenAI API), loads the cleaned data into Supabase, and displays a dashboard in Streamlit (deployed via Modal).



---



\## 1. Setup



\### Clone repo \& install dependencies

```powershell

git clone https://github.com/<your-username>/llm-etl-cowboys.git

cd llm-etl-cowboys



\# virtual environment

py -m venv .venv

. .\\.venv\\Scripts\\Activate.ps1



\# Install package

pip install -r requirements.txt



