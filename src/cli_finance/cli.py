"""CLI entry point — handles user interaction, layout, and dispatching commands."""
try:
    from cli_finance import utils
    from cli_finance.shared import console, bindings, bottom_toolbar, ask_choice
except ModuleNotFoundError:
    import utils  # type: ignore[import-not-found]  # direct script execution
    from shared import console, bindings, bottom_toolbar, ask_choice  # type: ignore[import-not-found]
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.validation import ValidationError, Validator
from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

class NumberValidator(Validator):
    """Validates that the user enters a positive non-zero float."""

    def validate(self, document: Document) -> None:
        text = document.text
        if not text.strip():
            raise ValidationError(message="Please enter an amount.", cursor_position=0)
        try:
            val = float(text)
            if val <= 0.0:
                raise ValidationError(message="Amount must be > 0.", cursor_position=len(text))
        except ValueError:
            raise ValidationError(message="Please enter a valid number.", cursor_position=len(text)) from None

ASCII_art = r"""
  /$$$$$$  /$$       /$$$$$$       /$$$$$$$$ /$$$$$$ /$$   /$$  /$$$$$$  /$$   /$$  /$$$$$$  /$$$$$$$$
 /$$__  $$| $$      |_  $$_/      | $$_____/|_  $$_/| $$$ | $$ /$$__  $$| $$$ | $$ /$$__  $$| $$_____/
| $$  \__/| $$        | $$        | $$        | $$  | $$$$| $$| $$  \ $$| $$$$| $$| $$  \__/| $$      
| $$      | $$        | $$        | $$$$$     | $$  | $$ $$ $$| $$$$$$$$| $$ $$ $$| $$      | $$$$$   
| $$      | $$        | $$        | $$__/     | $$  | $$  $$$$| $$__  $$| $$  $$$$| $$      | $$__/   
| $$    $$| $$        | $$        | $$        | $$  | $$\  $$$| $$  | $$| $$\  $$$| $$    $$| $$      
|  $$$$$$/| $$$$$$$$ /$$$$$$      | $$       /$$$$$$| $$ \  $$| $$  | $$| $$ \  $$|  $$$$$$/| $$$$$$$$
 \______/ |________/|______/      |__/      |______/|__/  \__/|__/  |__/|__/  \__/ \______/ |________/
                                                                                                      
                                                                                                      
                                                                                                      """

def make_header() -> Panel:
    lines = ASCII_art.strip("\n").split("\n")
    colors = [
        "#00FFFF", "#00E5FF", "#00BFFF", "#0099FF", "#0077FF",
        "#0055FF", "#0033FF", "#0022CC", "#0011AA", "#000099"
    ]
    art = Text()

    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        art.append(line + "\n", style=f"bold {color}")

    return Panel(
        Align(art, align='center', vertical='middle'),
        border_style="#00BFFF",
        padding=(0, 2),
        title="[bold cyan]CLI-Finance v0.1.0[/bold cyan]",
        subtitle="[dim]Your personal finance tracker[/dim]",
        expand=False
    )

def input_c() -> tuple[str, str, float] | None:
    """Interactively collect category, type, and amount from the user.

    Returns a (category, type_, amount) tuple, or None if the user cancels.
    """
    category = ask_choice("Enter category", ['Income', 'Expense'])
    if category is None:
        console.print("[bold red]Action cancelled. Returning to main menu...[/bold red]")
        return None

    if category == "Income":
        type_ = ask_choice("Enter the type of Income", ['Salary', 'Dividends', 'Cash Back', 'Investment returns'])
    elif category == "Expense":
        type_ = ask_choice("Enter the type of Expense", ['Grocery', 'Rent', 'Wifi', 'Electricity', 'Subscription', 'Electronics'])

    if type_ is None:
        console.print("[bold red]Action cancelled. Returning to main menu...[/bold red]")
        return None

    text = HTML("<b><ansicyan>Enter amount</ansicyan></b>\n<ansigreen>❯ $</ansigreen> ")
    amount_str = prompt(text, validator=NumberValidator(), key_bindings=bindings, bottom_toolbar=bottom_toolbar)

    if amount_str is None:
        console.print("[bold red]Action cancelled. Returning to main menu...[/bold red]")
        return None

    return category, type_, float(amount_str)

def handle_add() -> None:
    """Ask the user for transaction details and save the record to the database."""
    result = input_c()
    if result is None:
        return
    category, type_, amount = result
    utils.add_record(category, type_, amount)

    details = f"[bold]Category:[/bold] [cyan]{category}[/cyan]\n[bold]Type:[/bold] [cyan]{type_}[/cyan]\n[bold]Amount:[/bold] [bold magenta]${amount:,.2f}[/bold magenta]"
    console.print(Panel(details, title="[bold green]✔ Transaction saved successfully![/bold green]", border_style="green", expand=False))

def handle_delete() -> None:
    """Prompt the user to delete all transactions or a specific one by ID."""
    choice = ask_choice("Do you want to delete specific transaction or all the data?", ['All', 'Specific'])
    if choice == 'All':
        utils.delete_all()
        console.print(Panel("[bold red]All data has been deleted.[/bold red]", title="Delete", border_style="red", expand=False))
    elif choice == 'Specific':
        utils.delete_specific()
        console.print(Panel("[bold yellow]Specific data deleted.[/bold yellow]", title="Delete", border_style="yellow", expand=False))
    elif choice is None:
        console.print("[dim]Operation cancelled.[/dim]")

def _summary_table_layout(total_income: float, total_expense: float, balance: float, last_date: str) -> None:
    """Render the summary as a Rich table inside a panel."""
    table = Table(
        title=f"Transaction Summary — Last updated: {last_date}",
        box=box.HEAVY_EDGE,
        header_style="bold cyan",
        show_lines=True
    )
    table.add_column("Category", justify="right", no_wrap=True)
    table.add_column("Total", style='green', justify="right")
    table.add_row("Total Income", f"[bold green]${total_income:,.2f}[/bold green]")
    table.add_row("Total Expense", f"[bold red]${total_expense:,.2f}[/bold red]")

    b_color = "green" if balance >= 0 else "red"
    table.add_row("[bold]Balance[/bold]", f"[bold {b_color}]${balance:,.2f}[/bold {b_color}]")

    console.print(Panel(Align(table, align="center"), border_style="cyan", expand=False, title="[bold cyan]Summary[/bold cyan]"))
    
def _summary_body(total_income: float, total_expense: float, balance: float, last_date: str) -> Panel:
    """Render a clean financial summary panel as the body layout."""
    b_color = "green" if balance >= 0 else "red"
    b_sign = "+" if balance >= 0 else "-"

    body = Text()
    body.append("   Total Income   ▸  ", style="bold cyan")
    body.append(f"${total_income:>12,.2f}\n", style="bold #00FF88")
    body.append("   Total Expense  ▸  ", style="bold cyan")
    body.append(f"${total_expense:>12,.2f}\n", style="bold #FF4444")
    body.append("  ─────────────────────────────────\n", style="dim")
    body.append("  Ending Balance        ▸ ", style="bold cyan")
    body.append(f"{b_sign}${abs(balance):>12,.2f}\n", style=f"bold {b_color}")
    body.append("\n")
    body.append(f"  Last updated: {last_date}", style="dim")

    return Panel(
        Align(body, align="center"),
        border_style="#00BFFF",
        padding=(1, 2),
        expand=True,
        title="[bold cyan]Financial Summary[/bold cyan]",
    )


def handle_summary() -> None:
    """Retrieve totals from the database and render the summary table."""
    total_income, total_expense, last_date = utils.get_records()
    total_income = total_income or 0
    total_expense = total_expense or 0
    balance = total_income - total_expense
    _summary_table_layout(total_income, total_expense, balance, last_date)

def handle_plot() -> None:
    """Render a line plot of cumulative income and expenses over time."""
    try:
        utils.line_plot()
    except Exception as e:
        console.print(f"[bold red]Failed to plot data:[/bold red] {e}")
def main() -> None:
    """Initialise the database, render the header, and run the main command loop."""
    utils.init_()

    dispatch = {
        'Add': handle_add,
        'Delete':handle_delete,
        'Summary': handle_summary,
        'plot': handle_plot
    }

    console.clear()
    console.print(make_header())

    # Show financial summary body below the header
    total_income, total_expense, last_date = utils.get_records()
    total_income = total_income or 0
    total_expense = total_expense or 0
    balance = total_income - total_expense
    summary_panel = _summary_body(total_income, total_expense, balance, last_date)

    future_panel = Panel(
        Align(Text("\n\n\n[ Placeholder for future features ]\n\n\n", style="dim"), align="center", vertical="middle"),
        border_style="#00BFFF",
        padding=(0, 2),
        expand=False,
        title="[bold cyan]Upcoming Features[/bold cyan]",
    )

    grid = Table.grid(expand=False, padding=(0, 2))
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_row(summary_panel, future_panel)

    console.print(grid)
    console.print()

    while True:
        try:
            command = ask_choice("Action", [*dispatch.keys(), 'Exit'])
            if command is None or command == 'Exit':
                console.print("\n[dim]Goodbye! Closing CLI-Finance...[/dim]")
                break
            console.print()
            dispatch[command]()
            console.print()
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye! Closing CLI-Finance...[/dim]")
            break

if __name__ == "__main__":
    main()
