#IMPLE CHECK TO CONRM IF DB IS WORKING
import sqlite3
import pandas as pd

# 1. Connect directly to the local SQLite file
conn = sqlite3.connect("tutor_storage.db")

# 2. Execute a raw SQL query and load it into a DataFrame
df = pd.read_sql_query("SELECT * FROM session_logs", conn)

# 3. Filter the columns to verify the core requirements
if not df.empty:
    print(df[["session_id", "input_text", "reply_text", "synced", "timestamp"]].tail())
else:
    print("The session_logs table is currently empty.")

conn.close()