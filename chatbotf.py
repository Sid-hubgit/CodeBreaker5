import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sqlite3
import subprocess
import requests
import json

# ------------------------------
# CONFIG
# ------------------------------
DB_PATH = "mydata.db"  # your SQL database
JOOBLE_API_KEY = "1a07f637-222e-43c6-8c97-f0a7d67f39b2"
JOOBLE_BASE_URL = "https://api.jooble.org/"

SYSTEM_PROMPT = """
You are an advanced AI Career Counselor and Job Navigator.
Use only the data from the SQL database provided.
Be professional, friendly, supportive, and realistic.
If information is missing, say: "I'm unable to fetch the information regarding this."
"""

# ------------------------------
# HELPER: QUERY SQL DATABASE
# ------------------------------
def query_sql(user_text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    preview = ""
    for table in tables:
        # Get text columns
        cursor.execute(f"PRAGMA table_info([{table}])")
        columns = [col[1] for col in cursor.fetchall() if col[2] in ('TEXT','VARCHAR','CHAR')]
        if not columns:
            continue

        # Dynamic query
        like_clauses = " OR ".join([f"[{col}] LIKE ?" for col in columns])
        sql_query = f"SELECT * FROM [{table}] WHERE {like_clauses} LIMIT 5"
        params = [f"%{user_text}%"] * len(columns)

        try:
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            if rows:
                preview += f"\nTABLE: {table}\n"
                col_names = [desc[0] for desc in cursor.description]
                for r in rows:
                    row_str = ", ".join(f"{c}: {v}" for c, v in zip(col_names, r))
                    preview += row_str + "\n"
        except Exception as e:
            continue

    conn.close()
    if not preview:
        preview = "No directly relevant rows found in the database.\n"
    return preview

# ------------------------------
# HELPER: FETCH LIVE JOBS
# ------------------------------
def fetch_live_jobs(user_text):
    url = JOOBLE_BASE_URL
    headers = {"Authorization": f"Bearer {JOOBLE_API_KEY}"}
    payload = {"query": user_text, "limit": 5}

    try:
        response = requests.post(
    url,
    json=payload,
    headers=headers,
    verify=False   # <‑‑ THIS BYPASSES SSL COMPLETELY
)
        if response.status_code != 200:
            return f"[API Error {response.status_code}]"
        data = response.json()
        jobs = data.get("jobs", [])
        if not jobs:
            return "No live jobs found for your query."
        result = ""
        for j in jobs:
            result += f"- {j['title']} at {j.get('company', 'N/A')} ({j.get('location', 'N/A')})\n  Link: {j.get('link')}\n"
        return result
    except Exception as e:
        return f"[API Error] Could not fetch live jobs: {e}"

# ------------------------------
# ASK LOCAL LLM
# ------------------------------
def ask_local_llm(user_text, sql_preview, live_jobs_preview):
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Relevant SQL data:\n{sql_preview}\n\n"
        f"Relevant live jobs:\n{live_jobs_preview}\n\n"
        f"User question: {user_text}"
    )

    # Call local LLaMA 2 via Ollama
    try:
        result = subprocess.run(
            ["ollama", "run", "llama2"],  # replace with your local model
            input=full_prompt,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[LLM Error] {e}"

# ------------------------------
# CHATBOT LOOP
# ------------------------------
def chatbot():
    print("Heyy!! I am Ace your AI powered career counsellor. Tell me how can i help you today??.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Bot: Goodbye!")
            break

        sql_preview = query_sql(user_input)
        live_jobs_preview = fetch_live_jobs(user_input)
        reply = ask_local_llm(user_input, sql_preview, live_jobs_preview)

        print("\nBot:", reply, "\n")

# ------------------------------
# ENTRY POINT
# ------------------------------
if __name__ == "__main__":
    chatbot()

