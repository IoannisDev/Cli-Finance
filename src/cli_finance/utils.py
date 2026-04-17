"""Database operations and plotting utilities for CLI-Finance."""
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from rich.console import Console
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.validation import ValidationError, Validator
try:
    from cli_finance.shared import ask_choice, bindings, bottom_toolbar
except ModuleNotFoundError:
    from shared import ask_choice, bindings, bottom_toolbar  # type: ignore[import-not-found]

APP_DIR = Path.home() / ".cli-finance"
APP_DIR.mkdir(mode=0o700, exist_ok=True)
DB = str(APP_DIR / "records.db")
console =Console()

class IDValidator(Validator):
    """Validates that the user enters a non-negative integer transaction ID."""

    def validate(self, document: Document) -> None:
        text = document.text
        if not text.strip():
            raise ValidationError(message="Please enter an ID to delete.", cursor_position=0)
        try:
            val = int(text)
            if val < 0:
                raise ValidationError(message="ID must be positive.", cursor_position=len(text)) from None
        except ValueError:
            raise ValidationError(message="Please enter a valid integer ID.", cursor_position=len(text)) from None

@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
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

def init_() -> None:
    """Create the transactions table if it does not already exist."""
    with get_conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        amount REAL NOT NULL,
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
        print("Actions is cancelled")
    with get_conn() as con:
        con.execute("INSERT INTO transactions(category,type,amount) VALUES(?,?,?)", (category, type_, amount))


def get_records() -> tuple[float | None, float | None, str]:
    """Return (total_income, total_expense, last_date) aggregated across all transactions.

    total_income and total_expense are None when no records exist.
    last_date is the most recent transaction date string, or 'No records'.
    """
    with get_conn() as con:
        total_income =  con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Income';").fetchone()[0]
        total_expense =  con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Expense';").fetchone()[0]
        date = con.execute("SELECT date FROM transactions ORDER BY date DESC LIMIT 1").fetchone()
        date = date[0] if date else "No records"
        return total_income,total_expense,date




def delete_all() -> None:
    """Prompt the user for confirmation, then delete all transaction records."""
    with get_conn() as con:
        # Prompt user using our new TUI standard
        confirm = ask_choice("Confirm delete data?", ['Confirm', 'Escape'])
        if confirm == 'Confirm':
            con.execute("DELETE FROM transactions")
            con.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")

def delete_specific() -> None:
    """Prompt the user for a transaction ID and delete that row."""
    with get_conn() as con:
        text = HTML("<b><ansired>Which transaction ID would you like to delete?</ansired></b>\n<ansigreen>❯</ansigreen> ")
        id_str = prompt(text, validator=IDValidator(), key_bindings=bindings, bottom_toolbar=bottom_toolbar)

        if id_str is not None:
            con.execute("DELETE FROM transactions WHERE id =?", (int(id_str),))

def get_data() -> tuple[list[str], list[float] | int, list[float] | int]:
    """Return cumulative income and expense series grouped by date.

    Returns (dates, incomes, expenses) where incomes and expenses are
    cumulative running totals per date. Returns (dates, 0, 0) when empty.
    """
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
    if total_income ==0 and total_expense==0:
        return dates,0,0
    else:
        return dates ,Incomes,Expenses
def line_plot() -> None:
    """Plot cumulative income and expenses as a terminal line chart."""
    import plotext as plt
    Date , Incomes, Expenses = get_data()
    if Incomes ==0 and Expenses==0:
        console.print("There isn't enough data to plot")
    else:
        x = list(range(len(Date)))
        plt.clf()

        plt.theme('clear')
        plt.plot_size(100,20)
        plt.date_form('d/m/Y')
        plt.plot(x,Incomes,color='green')
        plt.plot(x,Expenses,color='red')
        step = max(1, len(Date) // 10)
        sampled_x = x[::step]
        sampled_dates = Date[::step]
        plt.xticks(sampled_x, sampled_dates)
        plt.title("Financial Overview   [green: Income | red: Expense]")
        plt.show()



