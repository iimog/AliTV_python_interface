"""
This script is mainly for quickly mapping locus id into detailed information

Accept a file with gene locus and its annotations AND a directory which stodge genbank files which could be used to map.
"""

import sys
from glob import glob
from os.path import *

import click

sys.path.insert(0, dirname(dirname(__file__)))
from api.truncate_genome_from_target import get_all_CDS_from_gbk


def parsed_infile(infile):
    locus2gene = {}
    locus2genome = {}
    gbk2gbk_obj = {}
    for row in open(infile):
        row = row.strip('\n')
        locus, gene, gbk_file = row.split('\t')
        gbk_name = basename(gbk_file).rpartition('.')[0]
        locus2genome[locus] = gbk_name
        gbk2gbk_obj[gbk_name] = get_all_CDS_from_gbk(gbk_file)
    return locus2gene, locus2genome, gbk2gbk_obj


def main(locus2gene, locus2genome, gbk2gbk_obj,
         ofile):
    rows = []
    for locus, gene in locus2gene.items():
        genome = locus2genome[locus]
        gbk_obj = gbk2gbk_obj[genome]
        contig_name = gbk_obj['contig_name']
        start = str(int(gbk_obj['start']))
        end = str(int(gbk_obj['end']))
        rows.append('\t'.join([genome,
                               contig_name, start, end,
                               gene]))
    with open(ofile, 'w') as f1:
        f1.write("\n".join(rows))


def find_f(genomes, indir):
    genome2path = {}
    for genome in genomes:
        files = glob(join(indir, f"{genome}*"))
        if len(files) >= 2:
            print("detect multiple files... may get wrong")
        genome2path[genome] = get_all_CDS_from_gbk(files[0])
    return genome2path


@click.command()
@click.option("-i", "infile")
@click.option("-indir", "indir", default=None)
@click.option("-o", "ofile")
def cli(infile, indir, ofile):
    locus2gene, locus2genome, gbk2gbk_obj = parsed_infile(infile)
    if not gbk2gbk_obj and indir is not None:
        print(f"search in {indir}")
        genomes = set([g for l, g in locus2genome.items()])
        gbk2gbk_obj = find_f(genomes, indir)
    main(locus2gene, locus2genome, gbk2gbk_obj,
         ofile)


if __name__ == '__main__':
    cli()