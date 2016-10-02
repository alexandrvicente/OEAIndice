from hashlib import sha256
from struct import Struct
from collections import Counter
import os
import click

class Index:
    INDEX_SIZE = 9000001
    INDEX_STRUCT = Struct('<IQQ')
    CEP_STRUCT = Struct('72s72s72s72s2s8s2s')

    @staticmethod
    def cep_hash(cep):
        sha256_hash = sha256()
        sha256_hash.update(cep.to_bytes(4, byteorder='little'))
        return int.from_bytes(sha256_hash.digest(), byteorder='little') % Index.INDEX_SIZE

    def __init__(self, index_file):
        self.index_file = index_file

    def read(self, index_position):
        self.index_file.seek(index_position)
        index_raw = self.index_file.read(Index.INDEX_STRUCT.size)
        return Index.INDEX_STRUCT.unpack(index_raw)

    def write(self, cep, position):
        index_position = Index.cep_hash(cep) * Index.INDEX_STRUCT.size
        current_data = list(self.read(index_position))
        created_item = [cep, position, 0]

        if current_data[0] == 0:
            self.index_file.seek(index_position)
            self.index_file.write(Index.INDEX_STRUCT.pack(*created_item))
        else:
            created_item[2] = current_data[2]
            self.index_file.seek(0, os.SEEK_END)
            next_position = self.index_file.tell()
            self.index_file.write(Index.INDEX_STRUCT.pack(*created_item))
            self.index_file.seek(index_position)
            current_data[2] = next_position
            self.index_file.write(Index.INDEX_STRUCT.pack(*current_data))

    def generate(self, cep_file):
        empty_index_item = Index.INDEX_STRUCT.pack(0,0,0)
        self.index_file.seek(0)

        for i in range(0, Index.INDEX_SIZE):
            self.index_file.write(empty_index_item)

        cep_file.seek(0, os.SEEK_END)
        cep_file_size = cep_file.tell()

        cep_file.seek(0)
        cep_raw = cep_file.read(Index.CEP_STRUCT.size)

        with click.progressbar(range(0, cep_file_size, Index.CEP_STRUCT.size)) as positions:
            for position in positions:
                cep_data = Index.CEP_STRUCT.unpack(cep_raw)
                cep = int(cep_data[5])
                self.write(cep, position)
                cep_raw = cep_file.read(Index.CEP_STRUCT.size)

        return int(cep_file_size / Index.CEP_STRUCT.size)

    def search(self, cep):
        index_position = Index.cep_hash(cep) * Index.INDEX_STRUCT.size

        while True:
            current_data = self.read(index_position)

            if current_data[0] == cep:
                yield current_data[1]

            if current_data[2] == 0:
                break

            index_position = current_data[2]

    def stats(self):
        list_sizes = [0] * Index.INDEX_SIZE
        max_list = 0
        min_list = Index.INDEX_SIZE
        sum_list = 0

        with click.progressbar(range(0, Index.INDEX_SIZE),
                               label='Verificando tamanhos de listas') as bar:
            for i in bar:
                index_position = i * Index.INDEX_STRUCT.size
                while True:
                    data = self.read(index_position)
                    if data[0] != 0:
                        list_sizes[i] += 1

                    if data[2] == 0:
                        max_list = max(max_list, list_sizes[i])
                        min_list = min(min_list, list_sizes[i])
                        sum_list += list_sizes[i]
                        break
                    else:
                        index_position = data[2]

        click.echo('Maior lista: ', nl=False)
        click.secho(str(max_list), fg='blue', bold=True)

        click.echo('Menor lista: ', nl=False)
        click.secho(str(min_list), fg='blue', bold=True)

        click.echo('Média de tamanho: ', nl=False)
        click.secho(str(sum_list / Index.INDEX_SIZE), fg='blue', bold=True)

        click.echo('')

        count_lists = Counter(list_sizes)

        for i in range(1, max_list + 1):
            click.echo('Probabilidade de encontrar CEP em ', nl=False)
            click.secho(str(i), nl=False, fg='blue', bold=True)
            click.echo(' passos: ', nl=False)

            options = 0

            for key, value in count_lists.items():
                if key >= i:
                    options += value

            probability = options / sum_list

            click.secho(str(probability), fg='blue', bold=True)


