try:
    from cli_finance import utils
except ModuleNotFoundError:
    import utils  # type: ignore[import-not-found]  # direct script execution
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich import box
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.validation import Validator, ValidationError




#Theme for the CLI interface
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "repr.number" :"bold magenta",
    "repr.string" :"bold yellow",
    "panel.border":"grey50"
})

console = Console(markup=True, highlight=True, force_terminal=True, theme=custom_theme)
bindings = KeyBindings()

@bindings.add('escape')
def exit_app(event):
    # Support clean exit cleanly returning None when Escape is pressed
    event.app.exit(result=None)

def bottom_toolbar():
    return HTML(' <b><style bg="ansiyellow" fg="black"> TAB </style></b> Autocomplete  <b><style bg="ansired" fg="white"> ESC </style></b> Cancel/Exit ')

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text.strip():
            raise ValidationError(message="Please enter an amount.", cursor_position=0)
        try:
            val = float(text)
            if val <= 0.0:
                raise ValidationError(message="Amount must be > 0.", cursor_position=len(text))
        except ValueError:
            raise ValidationError(message="Please enter a valid number.", cursor_position=len(text))

def ask_choice(message: str, choices: list[str]) -> str | None:
    completer = WordCompleter(choices, ignore_case=True)
    choices_str = "/".join(choices)
    text = HTML(f"<b><ansicyan>{message}</ansicyan></b> <ansigray>[{choices_str}]</ansigray>\n<ansigreen>❯</ansigreen> ")
    
    while True:
        result = prompt(
            text, 
            completer=completer, 
            key_bindings=bindings, 
            bottom_toolbar=bottom_toolbar,
            complete_while_typing=True
        )
        if result is None:
            return None
        result_lower = result.strip().lower()
        if not result_lower:
            continue
        for choice in choices:
            if choice.lower() == result_lower:
                return choice
        console.print(f"[bold red]Invalid option.[/bold red] Please choose from: {choices_str}")

ASCII_art = r"""
.---------------------------------------------------------.
|  _____ _                               ____ _     ___   |
| |  ___(_)_ __   __ _ _ __   ___ ___   / ___| |   |_ _|  |
| | |_  | | '_ \ / _` | '_ \ / __/ _ \ | |   | |    | |   |
| |  _| | | | | | (_| | | | | (_|  __/ | |___| |___ | |   |
| |_|   |_|_| |_|\__,_|_| |_|\___\___|  \____|_____|___|  |
|                                                         |
'---------------------------------------------------------'"""

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
        padding=(1, 2),
        title="[bold cyan]CLI-Finance v0.1.0[/bold cyan]",
        subtitle="[dim]Your personal finance tracker[/dim]",
        expand=False
    )

#Asks the user for input and the data is validated by the rich library
def input_c():
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

def handle_add():
    "Asks for input from the user and records the data"
    result = input_c()
    if result is None:
        return
    category, type_, amount = result
    utils.add_record(category, type_, amount)
    
    details = f"[bold]Category:[/bold] [cyan]{category}[/cyan]\n[bold]Type:[/bold] [cyan]{type_}[/cyan]\n[bold]Amount:[/bold] [bold magenta]${amount:,.2f}[/bold magenta]"
    console.print(Panel(details, title="[bold green]✔ Transaction saved successfully![/bold green]", border_style="green", expand=False))

def handle_delete():
    "Deletes the data from the sql file"
    choice = ask_choice("Do you want to delete specific transaction or all the data?", ['All', 'Specific'])
    if choice == 'All':
        utils.delete_all()
        console.print(Panel("[bold red]All data has been deleted.[/bold red]", title="Delete", border_style="red", expand=False))
    elif choice == 'Specific':
        utils.delete_specific()
        console.print(Panel("[bold yellow]Specific data deleted.[/bold yellow]", title="Delete", border_style="yellow", expand=False))
    elif choice is None:
        console.print("[dim]Operation cancelled.[/dim]")

def handle_summary():
    "Returns a table with the data of total income and total expense"
    total_income,total_expense,last_date = utils.get_records()
    table = Table(
        title=f"Transaction Summary — Last updated: {last_date}", 
        box=box.HEAVY_EDGE, 
        header_style="bold cyan",
        show_lines=True
    )
    table.add_column("Category", justify="right", no_wrap=True)
    table.add_column("Total", style='green', justify="right")
    table.add_row("Total Income", f"[bold green]${total_income or 0:,.2f}[/bold green]")
    table.add_row("Total Expense", f"[bold red]${total_expense or 0:,.2f}[/bold red]")
    
    balance = (total_income or 0) - (total_expense or 0)
    b_color = "green" if balance >= 0 else "red"
    
    table.add_row("[bold]Balance[/bold]", f"[bold {b_color}]${balance:,.2f}[/bold {b_color}]")
    
    console.print(Panel(Align(table, align="center"), border_style="cyan", expand=False, title="[bold cyan]Summary[/bold cyan]"))

def handle_plot():
    "plots the transaction data into a line plot"
    try:
        utils.line_plot()
    except Exception as e:
        console.print(f"[bold red]Failed to plot data:[/bold red] {e}")
def main():
    utils.init_()

    dispatch = {
        'Add': handle_add,
        'Delete':handle_delete,
        'Summary': handle_summary,
        'plot': handle_plot
    }
    
    console.clear()
    console.print(make_header())
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
