
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.prompt import InvalidResponse
from rich.layout import Layout
import utils
from rich.panel import Panel
from rich.live import Live
from rich.theme import Theme
from rich.table import Table
from rich.align import Align
#Theme for the CLI interface
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "repr.number" :"bold magenta",
    "repr.string" :"bold yellow"
})

console = Console(width=120,markup=True,highlight=True,style='on black',force_terminal=True,theme=custom_theme)

ASCII_art = r"""
.---------------------------------------------------------.
|  _____ _                               ____ _     ___   |
| |  ___(_)_ __   __ _ _ __   ___ ___   / ___| |   |_ _|  |
| | |_  | | '_ \ / _` | '_ \ / __/ _ \ | |   | |    | |   |
| |  _| | | | | | (_| | | | | (_|  __/ | |___| |___ | |   |
| |_|   |_|_| |_|\__,_|_| |_|\___\___|  \____|_____|___|  |
|                                                         |
'---------------------------------------------------------'"""
def make_layout():
    layout = Layout()
    layout.split_column(
        # Increase size to fit the height of your ASCII art
        Layout(name="header", size=10), 
        Layout(name="main", ratio=1)
    )
    # ... rest of your split logic
    return layout
def make_header(layout: Layout) -> None:
    layout["header"].update(
        Panel(Align(f"[bold cyan]{ASCII_art}[/bold cyan]",align='center'), style="bold cyan", padding=(0, 1), title="v1.0")
    )
def input_c():
    category = Prompt.ask("Enter category",choices=['Income','Expense'])
    type_ = Prompt.ask("Enter transaction type",choices=['Salary','Grocery','Rent','Wifi','Electricity','Subscription'],case_sensitive=False)
    amount = utils.numberprompt.ask("Enter amount")
    return category,type_,amount 

def handle_add():
    category,type_,amount = input_c()
    utils.add_record(category,type_,amount)
    console.print(f"[green]Transaction saved:[/green] {category} | {type_} | {amount}")

def handle_delete():
    choice = Prompt.ask("Do you want to delete specific transaction or all the data?",choices=['All','Specific','Escape'],case_sensitive=False)
    if choice=='All':
     utils.delete_all()
    elif choice=='Specific':
        utils.delete_sepcific()
    elif choice=='Escape':
        pass

def handle_summary():
    total_income,total_expense = utils.get_records()
    table = Table(title="Transaction Summary")
    table.add_column("Category",justify="right",no_wrap=True)
    table.add_column("Total",style='green')
    table.add_row("Total Income",f"${total_income or 0:,.2f}")
    table.add_row("Total Expense",f"${total_expense or 0:,.2f}")
    console.print(table)

def handloe_plot():
    utils.line_plot()

def main():
    utils.init_()
    layout = make_layout()
    make_header(layout)
    console.print(layout['header'].renderable)

    dispatch = {
        'Add': handle_add,
        'Delete':handle_delete,
        'Summary': handle_summary,
        'plot': handloe_plot
    }
    while True:
        console.print()
  
        command = Prompt.ask("Command: ",choices=[*dispatch.keys(),'exit'],case_sensitive=False)
        if command =="exit":
            break
        dispatch[command]()

if __name__ == "__main__":
    main()
