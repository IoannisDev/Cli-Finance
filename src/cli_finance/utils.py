"""Database operations and plotting utilities for CLI-Finance."""
import os
import sys
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
    """Yield a database connection that checks if the database exists, auto commits and always closes."""
    if not os.path.exists(DB):
        console.print("[bold red]Database not found.[/bold red] Restart the terminal and initialize the database first.")
        sys.exit(1)
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
    """Create the transactions and savings tables if they do not already exist."""
    with get_conn() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        amount REAL NOT NULL,
        savings REAL DEFAULT NULL,
        date TEXT DEFAULT (date('now'))
         )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS savings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        date TEXT DEFAULT (date('now'))
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS goal(
        id INTEGER PRIMARY KEY CHECK (id = 1),
        amount REAL NOT NULL,
        date TEXT DEFAULT (date('now'))
        )
        """)

def get_last_savings() -> float:
    """Return the most recent cumulative savings amount."""
    with get_conn() as con:
        result = con.execute(
            "SELECT savings FROM transactions WHERE savings IS NOT NULL ORDER BY date DESC, id DESC LIMIT 1"
        ).fetchone()
    return result[0] if result else 0.0

def get_total_savings() -> float:
    """Return the sum of all deposits in the savings table."""
    with get_conn() as con:
        result = con.execute("SELECT SUM(amount) FROM savings").fetchone()
    return result[0] if result[0] is not None else 0.0

def get_savings_history() -> list[tuple[int, float, str]]:
    """Return all savings rows as (id, amount, date) sorted by date desc."""
    with get_conn() as con:
        rows = con.execute(
            "SELECT id, amount, date FROM savings ORDER BY date DESC, id DESC"
        ).fetchall()
    return [(r[0], r[1], r[2]) for r in rows]

def add_savings(user_entered_amount: float) -> None:
    """Insert a new savings deposit into the dedicated savings table."""
    with get_conn() as con:
        con.execute("INSERT INTO savings(amount) VALUES(?)", (float(user_entered_amount),))

def set_goal(amount: float) -> None:
    """Upsert the savings goal — replaces any existing goal (only one row, id=1)."""
    with get_conn() as con:
        con.execute(
            "INSERT INTO goal(id, amount) VALUES(1, ?) ON CONFLICT(id) DO UPDATE SET amount=excluded.amount, date=date('now')",
            (amount,)
        )

def load_goal() -> float | None:
    """Return the current savings goal amount, or None if not set."""
    with get_conn() as con:
        row = con.execute("SELECT amount FROM goal WHERE id = 1").fetchone()
    return float(row[0]) if row else None

def add_record(category:str, type_:str, amount:float) -> None:
    """Inserts financial transactions into the database
    Args:
        category(str): 'Income' or 'Expense'
        type(str): 'Salary' ,'Rent',etc.
        amount(float): The transaction amount
    """
    savings = get_last_savings()
    if category is None or type_ is None:
        print("Actions is cancelled")
    with get_conn() as con:
        con.execute("INSERT INTO transactions(category,type,amount,savings) VALUES(?,?,?,?)", (category, type_, amount,savings))

def get_records() -> tuple[float | None, float | None, float, str]:
    """Return (total_income, total_expense, total_savings, last_date).

    total_income and total_expense are None when no records exist.
    last_date is the most recent transaction date string, or 'No records'.
    """
    with get_conn() as con:
        total_income = con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Income';").fetchone()[0]
        total_expense = con.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Expense';").fetchone()[0]
        total_savings_row = con.execute("SELECT SUM(amount) FROM savings").fetchone()
        total_savings = total_savings_row[0] if total_savings_row[0] is not None else 0.0
        date = con.execute("SELECT date FROM transactions ORDER BY date DESC LIMIT 1").fetchone()
        date = date[0] if date else "No records"
        return total_income, total_expense, total_savings, date
    

def delete_all() -> None:
    """Prompt the user for confirmation, then delete the database."""
    confirm = ask_choice("Confirm delete data?", ['Confirm', 'Escape'])
    if confirm == 'Confirm':
        db_path = DB  # replace with your actual path
        if os.path.exists(db_path):
            os.remove(db_path)

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



