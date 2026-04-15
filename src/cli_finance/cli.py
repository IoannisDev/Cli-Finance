try:
    from cli_finance import utils
except ModuleNotFoundError:
    import utils  # type: ignore[import-not-found]  # direct script execution
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich import box

#Theme for the CLI interface
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "repr.number" :"bold magenta",
    "repr.string" :"bold yellow",
    "panel.border":"grey50"
})

console = Console(width=120,markup=True,highlight=True,force_terminal=True,theme=custom_theme)

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
        title="[bold cyan]CLI-Finance v1.0[/bold cyan]",
        subtitle="[dim]Your personal finance tracker[/dim]",
        expand=False
    )

#Asks the user for input and the data is validated by the rich library
def input_c():
    category = Prompt.ask("[bold cyan]Enter category[/bold cyan]",choices=['Income','Expense'])
    if category =="Income":
        type_= Prompt.ask(
            "[bold cyan]Enter the type of Income[/bold cyan]",
            choices=['Salary','Dividends','Cash Back','Investment returns'],
            case_sensitive=False
        )
    elif category=="Expense":
        type_ = Prompt.ask(
            "[bold cyan]Enter the type of Expense[/bold cyan]",
            choices=['Grocery','Rent','Wifi','Electricity','Subscription','Electronics'],
            case_sensitive=False
        )
    amount = utils.numberprompt.ask("[bold cyan]Enter amount[/bold cyan]")
    return category,type_,amount

def handle_add():
    "Asks for input from the user and records the data"
    category,type_,amount = input_c()
    utils.add_record(category,type_,amount)
    
    details = f"[bold]Category:[/bold] [cyan]{category}[/cyan]\n[bold]Type:[/bold] [cyan]{type_}[/cyan]\n[bold]Amount:[/bold] [bold magenta]${amount:,.2f}[/bold magenta]"
    console.print(Panel(details, title="[bold green]✔ Transaction saved successfully![/bold green]", border_style="green", expand=False))

def handle_delete():
    "Deletes the data from the sql file"
    choice = Prompt.ask(
        "[bold red]Do you want to delete specific transaction or all the data?[/bold red]",
        choices=['All','Specific','Escape'],
        case_sensitive=False
    )
    if choice=='All':
        utils.delete_all()
        console.print(Panel("[bold red]All data has been deleted.[/bold red]", title="Delete", border_style="red", expand=False))
    elif choice=='Specific':
        utils.delete_specific()
        console.print(Panel("[bold yellow]Specific data deleted.[/bold yellow]", title="Delete", border_style="yellow", expand=False))
    elif choice=='Escape':
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
    utils.line_plot()

def main():
    utils.init_()

    dispatch = {
        'Add': handle_add,
        'Delete':handle_delete,
        'Summary': handle_summary,
        'plot': handle_plot
    }
    
    console.clear()
    console.print(Align(make_header(), align="left"))
    console.print()
    
    while True:
        try: 
            command = Prompt.ask("[bold cyan]Command[/bold cyan]", choices=[*dispatch.keys(),'exit'], case_sensitive=False)
            
            if command =="exit":
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
