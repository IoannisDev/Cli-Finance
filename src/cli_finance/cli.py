
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.prompt import InvalidResponse
from rich.layout import Layout
import utils
from rich.panel import Panel
from rich.live import Live
from rich.theme import Theme
from rich.table import Table
from rich.text import Text
from rich.align import Align

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
def make_layout():
    "Creates layout for the ASCII art"
    layout = Layout()
    layout.split_column(
        # Increase size to fit the height of your ASCII art
        Layout(name="header", size=10), 
        Layout(name="main", ratio=1)
    )
    return layout
def make_header(layout: Layout) -> None:
    lines = ASCII_art.split("\n")
    colors = ["#00FFFF", "#00E5FF", "#00BFFF", "#0099FF", "#0077FF", "#0055FF", "#0033FF", "#0022CC", "#0011AA", "#000099"]
    
    art = Text()
    for line, color in zip(lines, colors):
        art.append(line + "\n", style=f"bold {color}")

    layout["header"].update(
        Panel(Align(art, align='center'), border_style="#00BFFF", padding=(0, 1), title="v1.0")
    )
#Asks the user for input and the data is validated by the rich library
def input_c():
    category = Prompt.ask("Enter category",choices=['Income','Expense'])
    if category =="Income":
        type_= Prompt.ask("Enter the type of Income: ",choices=['Salary','Dividends','Cash Back','Investment returns'],case_sensitive=False)
    elif category=="Expense":
        type_ = Prompt.ask("Enter the type of Expense: ",choices=['Grocery','Rent','Wifi','Electricity','Subscription','Electronics'],case_sensitive=False)
    amount = utils.numberprompt.ask("Enter amount")
    return category,type_,amount 

def handle_add():
    "Asks for input from the user and records the data"
    category,type_,amount = input_c()
    utils.add_record(category,type_,amount)
    console.print(f"[green]Transaction saved:[/green] {category} | {type_} | {amount}")

def handle_delete():
    "Deletes the data from the sql file"
    choice = Prompt.ask("Do you want to delete specific transaction or all the data?",choices=['All','Specific','Escape'],case_sensitive=False)
    if choice=='All':
     utils.delete_all()
    elif choice=='Specific':
        utils.delete_specific()
    elif choice=='Escape':
        pass

def handle_summary():
    "Returns a table with the data of total income and total expense"
    total_income,total_expense,last_date = utils.get_records()
    table = Table(title=f"Transaction Summary — Last updated: {last_date}")
    table.add_column("Category",justify="right",no_wrap=True)
    table.add_column("Total",style='green')
    table.add_row("Total Income",f"${total_income or 0:,.2f}")
    table.add_row("Total Expense",f"${total_expense or 0:,.2f}")
    console.print(table)

def handle_plot():
    "plots the transaction data into a line plot"
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
        'plot': handle_plot
    }
    while True:
        console.print()
  
        command = Prompt.ask("Command: ",choices=[*dispatch.keys(),'exit'],case_sensitive=False)
        if command =="exit":
            break
        dispatch[command]()

if __name__ == "__main__":
    main()
