import modal, os, shlex

image = modal.Image.debian_slim().pip_install(
    "streamlit", "supabase", "pandas", "plotly"
)

# In Modal Dashboard → Secrets: create "my-secret" with SUPABASE_URL & SUPABASE_KEY
secret = modal.Secret.from_name("my-secret")

app = modal.App("cowboys-streamlit")
volume = modal.Volume.from_name("my-data", create_if_missing=True)

@app.function(image=image, secrets=[secret], volumes={"/mnt/data": volume})
def run():
    target = "streamlit_app.py"
    cmd = f"streamlit run {shlex.quote(target)} --server.port 8000 --server.address 0.0.0.0"
    os.system(cmd)

@app.local_entrypoint()
def main():
    run.remote()
