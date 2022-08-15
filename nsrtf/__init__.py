from email.policy import default
import click




@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    # click.echo('Hello World!')
    if debug:
        click.echo(f"Debug mode is on")

def open_cap_validator(source):
    try:
        return int(source)
    except:
        return source

@cli.command()  # @cli, not @click!
@click.option('--source', default=0, help='stream source', type=open_cap_validator)
@click.option('--debug/--no-debug', default=False)
@click.option('--record/--no-record', default=False)
def golive(source, debug, record):
    from nsrtf import live
    click.echo('Going live...')
    live.record(source, debug, record)