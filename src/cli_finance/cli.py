"""Console script for cli_finance."""

import typer
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.layout import Layout
import utils
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "repr.number" :"bold magenta",
    "repr.string" :"bold yellow"
})
console = Console(width=120,markup=True,highlight=True,style='on black',force_terminal=True,theme=custom_theme)

def input_c():
    category = Prompt.ask("Enter category")
    type_ = Prompt.ask("Enter transaction type(Income/Expense)")
    amount = IntPrompt.ask("Enter amount")
    return category,type_,amount 

def main():
    records = []
    utils.init_()
    while True:
        console.print()
        type_ = Prompt.ask("Type",choices=['income','expense','show','exit','summary'])
      
        if type_ =='summary':
            rec = utils.get_records()
            console.print(f"Record count: {len(rec)}")  # debug
            for r in rec:
                console.print(dict(r))
            Prompt.ask("Press Enter to continue")
        elif type_=='income' or type_=='expense':
            category ,tp, amount = input_c()
            utils.add_record(category,tp,amount)
            console.print(f"[green]Saved:[/green]{category}|{amount}|{type_}")
        elif type_ =="exit":
            break


if __name__ == "__main__":
    main()
