import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.validation import Validator, ValidationError

APP_DIR = Path.home() / ".cli-finance"
APP_DIR.mkdir(mode=0o700, exist_ok=True)
DB = str(APP_DIR / "records.db")

class IDValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text.strip():
            raise ValidationError(message="Please enter an ID to delete.", cursor_position=0)
        try:
            val = int(text)
            if val < 0:
                raise ValidationError(message="ID must be positive.", cursor_position=len(text))
        except ValueError:
            raise ValidationError(message="Please enter a valid integer ID.", cursor_position=len(text))

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

#Initializes the sql database table if the table doesnot exist
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


def add_record(category:str, type_:str, amount:float) -> None:
    """Inserts financial transactions into the database
    Args:
        category(str): 'Income' or 'Expense'
        type(str): 'Salary' ,'Rent',etc.
        amount(float): The transaction amount
    """
    if category is None or type_ is None:
        print("Actions is canceled")
    with get_conn() as con:
        con.execute("INSERT INTO transactions(category,type,amount) VALUES(?,?,?)", (category, type_, amount))


def get_records():
    with get_conn() as con:
        total_income =  con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Income';").fetchone()[0]
        total_expense =  con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Expense';").fetchone()[0]
        date = con.execute("SELECT date FROM transactions ORDER BY date DESC LIMIT 1").fetchone()
        date = date[0] if date else "No records"
        return total_income,total_expense,date




def delete_all():
    from cli_finance.cli import ask_choice
    with get_conn() as con:
        # Prompt user using our new TUI standard
        confirm = ask_choice("Confirm delete data?", ['Confirm', 'Escape'])
        if confirm == 'Confirm':
            con.execute("DELETE FROM transactions")
            con.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")

def delete_specific():
    from cli_finance.cli import bindings, bottom_toolbar
    with get_conn() as con:
        text = HTML("<b><ansired>Which transaction ID would you like to delete?</ansired></b>\n<ansigreen>❯</ansigreen> ")
        id_str = prompt(text, validator=IDValidator(), key_bindings=bindings, bottom_toolbar=bottom_toolbar)
        
        if id_str is not None:
            con.execute("DELETE FROM transactions WHERE id =?", (int(id_str),))

def get_data():
    with get_conn() as con:
        Date = con.execute("SELECT DISTINCT  date FROM transactions ORDER BY date") .fetchall()
        raw_dates = [str(row[0]) for row in Date]
        dates = [datetime.strptime(str(row[0]), "%Y-%m-%d").strftime("%d/%m/%Y") for row in Date]
        Incomes = []
        Expenses = []
        total_income = 0
        total_expense = 0
        for date in raw_dates:
            inc = con.execute(
                "SELECT SUM(amount) FROM transactions WHERE category = 'Income' And date=?", (date,)
            ).fetchone()[0]
            exp = con.execute(
                "SELECT SUM(amount) FROM transactions WHERE category = 'Expense' And date=?", (date,)
            ).fetchone()[0]
            total_income += (inc or 0)
            total_expense += (exp or 0)
            Incomes.append(total_income)
            Expenses.append(total_expense)

    return dates ,Incomes,Expenses
def line_plot():
    import plotext as plt
    Date , Incomes, Expenses = get_data()
    x = list(range(len(Date)))
    plt.clf()

    plt.theme('clear')
    plt.plot_size(100,30)
    plt.date_form('d/m/Y')
    plt.plot(x,Incomes,color='green')
    plt.plot(x,Expenses,color='red')
    step = max(1, len(Date) // 10)
    sampled_x = x[::step]
    sampled_dates = Date[::step]
    plt.xticks(sampled_x, sampled_dates)
    plt.title("Financial Overview   [green: Income | red: Expense]")
    plt.show()



