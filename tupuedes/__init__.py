import click




@click.group()
@click.option('--debug/--no-debug', default=False)
#@click.pass_context
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
#@click.pass_context
@click.option('--source', default=0, help='stream source', type=open_cap_validator)
@click.option('--record/--no-record', default=False)
@click.option('--plot/--no-plot', default=False)
def golive(source, record, plot):
    from tupuedes import live
    click.echo('Going live...')
    live.record(source, plot, record)

@cli.command()
@click.option('--source', default=0, help='stream source', type=open_cap_validator)
def dale(source):
    from tupuedes.main import loop
    loop(source)
