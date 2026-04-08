import sqlite3
from contextlib import contextmanager
from pathlib import Path
from rich.prompt import Prompt,InvalidResponse,IntPrompt
import plotext as plt
from datetime import datetime
APP_DIR = Path.home() / ".cli-finance"
APP_DIR.mkdir(mode=0o700, exist_ok=True)
DB = str(APP_DIR / "records.db")



class numberprompt(Prompt):
    """A custom rich prompt that only accepts integers annd float greater than 0.0"""
    def process_response(self,value:str) -> float:
        try:
            number = float(value)
        except ValueError:
            raise InvalidResponse("[prompt.invalid]Please Enter a valid integer.")
        if number<=0.0:
            raise InvalidResponse("[prompt.invalid]Please enter value greater than 0")
        return number
@contextmanager
def get_conn():
    """Yield a database connection that auto-commits and always closes."""
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


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


def add_record(category:str, type_:str, amount:float)->int:
    """Inserts financial transactions into the database
    Args:
        category(str): 'Income' or 'Expense'
        type(str): 'Salary' ,'Rent',etc.
        amount(float): The transaction amount
    """

    with get_conn() as con:
        con.execute("INSERT INTO transactions(category,type,amount) VALUES(?,?,?)", (category, type_, amount))


def get_records():
    with get_conn() as con:
        total_income =  con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Income';").fetchone()[0]
        total_expense =  con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Expense';").fetchone()[0]
        return total_income,total_expense
    
    


def delete_all():
    with get_conn() as con:
        confirm = Prompt.ask(f"[red]Confirm delete data [/red]",choices=['Confirm','Escape'],case_sensitive=False)
        if confirm == "Confirm":
            con.execute("DELETE FROM transactions")
            con.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
        else:
            pass

def delete_sepcific():
    with get_conn() as con:
        id_ = IntPrompt.ask("Which transaction data you would like to delete?: ",default=None)
        con.execute("DELETE FROM transactions WHERE id =?", (id_,))

def get_data():
    with get_conn() as con:
        Date = con.execute("SELECT DISTINCT  date FROM transactions ORDER BY date") .fetchall() 
        raw_dates = [str(row[0]) for row in Date]
        dates = [datetime.strptime(str(row[0]), "%Y-%m-%d").strftime("%d/%m/%Y") for row in Date]
        Incomes = []
        Expenses = []
        for date in raw_dates:
            inc = con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Income' And date=?",(date,)).fetchone()[0]
            exp =con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Expense' And date=?",(date,)).fetchone()[0]
            Incomes.append(inc or 0)
            Expenses.append(exp or 0)

    return dates ,Incomes,Expenses
def line_plot():
    Date , Incomes, Expenses = get_data()
    x = list(range(len(Date)))
    plt.clf()

    plt.theme('dark')
    plt.plot_size(100,30)
    plt.date_form('d/m/Y')
    plt.plot(x,Incomes,color='green',label='Income')
    plt.plot(x,Expenses,color='red',label='Expense')
    plt.xticks(x, Date)
    plt.title("Financial Overview")
    plt.show()



