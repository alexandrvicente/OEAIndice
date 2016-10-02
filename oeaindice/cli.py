import click
from .index import Index


@click.group()
def cli():
    pass


@cli.command()
@click.argument('cep_file')
@click.argument('index_file')
def generate(cep_file, index_file):
    index_file = open(index_file, 'w+b')
    cep_file = open(cep_file, 'rb')

    index = Index(index_file)
    number_ceps = index.generate(cep_file)
    click.echo(str(number_ceps) + ' CEPs adicionados')

    cep_file.close()
    index_file.close()


@cli.command()
@click.argument('index_file')
@click.argument('cep')
def search(index_file, cep):
    index_file = open(index_file, 'rb')
    index = Index(index_file)
    results = index.search(int(cep))
    no_results = True

    for result in results:
        no_results = False
        click.echo('CEP ' + cep + ' encontrado na posição ', nl=False)
        click.secho(str(result), fg='blue', bold=True)

    if no_results:
        click.secho('Nenhum resultado encontrado', err=True, fg='red', bold=True)


@cli.command()
@click.argument('index_file')
def stats(index_file):
    index_file = open(index_file, 'rb')
    index = Index(index_file)
    index.stats()
