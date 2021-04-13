"""This is a script to generate sample.yml.
   PATH is traversed recursively and adds any file with '.fastq' or '.fq' in
   the file name with the file name minus extension as the sample ID.
"""

import logging
import os
import sys
import pandas as pd
from collections import defaultdict
sys.path.append(os.path.dirname(__file__))

#global vars
path_to_fastq = sys.argv[1]
#'/klaster/scratch/kkopera/COVID/microbiome/snakemake/QC_and_FT/raw_fastqs'
writing_dir = sys.argv[2]  

def get_samples_from_fastq(path):
    """creates table sampleID R1 R2 with the absolute paths of fastq files in a given folder"""
    samples = defaultdict(dict)
    seen = set()
    for dir_name, sub_dirs, files in os.walk(os.path.abspath(path)):
        for fname in files:

            if ".fastq" in fname or ".fq" in fname:

                sample_id = fname.split(".fastq")[0].split(".fq")[0]

                fq_path = os.path.join(dir_name, fname)

                sample_sth = sample_id

                if fq_path in seen: continue
                samples[sample_id]['path'] = fq_path

    samples= pd.DataFrame(samples).T

    if samples.isnull().any().any():
        logging.error(f"Missing files:\n\n {samples}")
        exit(1)

    if samples.shape[0]==0:
        logging.error(f"No files found in {path}\n"
                       "I'm looking for files with .fq or .fastq extension. ")
        exit(1)

    return samples


def prepare_sample_table(path_to_fastq,outfile='sample.yml'):
    """Write the file `samples.tsv` and complete the sample names and paths for all
    files in `path`.
    Args:
    path_to_fastq (str): fastq/fasta data directory"""

    samples = get_samples_from_fastq(path_to_fastq)
    samples.index = '    ' + samples.index.astype(str) + ':'

    logging.info("Found %d samples under %s" % (len(samples), path_to_fastq))

    sample_csv_file= os.path.join(writing_dir,'sample.txt')

    if os.path.exists(outfile):
        logging.error(f"Output file {outfile} already exists I don't dare to overwrite it.")
        exit(1)
    else:
        samples.to_csv(sample_csv_file,sep=' ', header=None) 

    with open(sample_csv_file, 'r') as infile, \
         open(sample_file, 'w') as outfile:
        data = infile.read()
        data = data.replace("\"", "")
        outfile.write('samples:\n' + data)
    
    try:
        os.remove(sample_csv_file)
    except OSError:
        pass


if not os.path.exists(writing_dir): os.makedirs(writing_dir)
sample_file = os.path.join(writing_dir,'sample.yml')
prepare_sample_table(path_to_fastq,outfile=sample_file)