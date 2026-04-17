"""Shared UI primitives used by both cli and utils modules."""
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.theme import Theme

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
def exit_app(event: object) -> None:
    # Support clean exit cleanly returning None when Escape is pressed
    event.app.exit(result=None)

def bottom_toolbar() -> HTML:
    """Return the HTML toolbar shown at the bottom of every prompt."""
    return HTML(' <b><style bg="ansiyellow" fg="black"> TAB </style></b> Autocomplete  <b><style bg="ansired" fg="white"> ESC </style></b> Cancel/Exit ')

def ask_choice(message: str, choices: list[str]) -> str | None:
    """Prompt the user to pick one option from choices using tab-completion.

    Returns the matched choice string, or None if the user pressed Escape.
    """
    completer = WordCompleter(choices, ignore_case=True)
    choices_str = "/".join(choices)
    text = HTML(f"<b><ansicyan>{message}</ansicyan></b>"
                f"<ansigray>[{choices_str}]</ansigray>"
                "\n<ansigreen>❯</ansigreen> ")

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
