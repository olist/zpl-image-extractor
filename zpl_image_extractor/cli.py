import sys
import click

from zpl_image_extractor.utils import normalise_zpl
from zpl_image_extractor.zpl import ZplLine

@click.group()
def entry():
    ...

@entry.command()
@click.option("--zpl-line", help="String with zpl instruction")
@click.option("--output", default="output.png", help="File path output with generated image")
def convert_zpl_line_to_png(zpl_line, output):
    zpl_line = ZplLine.build(line=zpl_line)
    file_path = zpl_line.to_image(file_path=output)
    click.echo(file_path)


@entry.command()
@click.option("--zpl", help="Path to zpl")
def tokenize_zpl(zpl):
    with open(zpl, 'r') as file:
        click.echo(normalise_zpl(file.read()))
    

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        entry(sys.argv[1:])
    else:
        entry()