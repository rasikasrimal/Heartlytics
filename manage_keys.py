"""Utility CLI for future key management tasks."""

import click


@click.command()
@click.option("--rewrap", "new_kid", help="Rewrap data keys to new KID")
def cli(new_kid):
    if new_kid:
        click.echo(f"Rewrap not implemented yet for {new_kid}")
    else:
        click.echo("No action specified")


if __name__ == "__main__":
    cli()
