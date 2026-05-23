from typing import List, Any

markdown_file = open("output.md", "w")


def write_markdown(content: str):
    from rich.console import Console
    from rich.markdown import Markdown

    # markdown_file.write(content)
    # markdown_file.write("\n")
    console = Console()
    console.print(Markdown(content))
    console.print("\n")


def to_markdown(items: List[Any]) -> str:
    markdown_str = ""

    for i, item in enumerate(items):
        markdown_str += item.markdown(i)

    return markdown_str
