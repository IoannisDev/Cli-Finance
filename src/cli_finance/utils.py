import sqlite3
import pathlib as path



DB = "records.db"
def get_conn():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con
def init_():
    with get_conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT DEFAULT (date('now'))
         )
        """)
def add_record(category,type_,amount):
    with get_conn() as con:
        con.execute("INSERT INTO transactions(category,type,amount) VALUES(?,?,?)",(category,type_,amount))
def get_records():
    with get_conn() as con:
        return con.execute("SELECT *FROM transactions").fetchall()
def delete_all():
    with get_conn() as con:
        con.execute("DELETE FROM transactions")
        con.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
def delete_sepcific(id_):
    with get_conn() as con:
        con.execute("DELETE FROM transactions WHERE id =?",(id_,))
# def main():
#     init_()
#     add_record('test','income',500)
#     rec = get_records()
#     for r in rec:
#         print(dict(r))
#     delete_sepcific(1)
#     print("Specific deleted")
#     rec = get_records()
#     for r in rec:
#         print(dict(r))
#     rec = get_records()
#     delete_all()
#     print("All deleted")
#     for r in rec:
#        print(dict(r))
# main()


