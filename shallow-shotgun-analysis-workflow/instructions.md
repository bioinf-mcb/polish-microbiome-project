# Shallow shotgun analysis pipeline

This is a bioinformatics shallow shotgun analysis pypeline intended for use with single-end metagenomic data sequenced at around 500 000 reads per sample depth. It can be used for other shotgun data as well by modifying congiguration file. 

In the final step of this workflow BIOM tables are generated in [woltka](https://github.com/qiyunzhu/woltka) - a classifiaction tool -, which is preceded by quality control and adapter trimming (fastp), contamination removal (minimap2) and alignemnt to refernece genomes (bowtie2). This step is implemented in Snakemake workflow management system. More details [here](#workflow-execution).

## Contents
- [Getting started](#getting-started)
- [Workflow execution](#workflow-execution)
  - [Snakemake environemnt setup](#snakemake-environment-setup)
  - [Configure snakemake](#configure-snakemake)
  - [Execution](#execution)
- [Workflow description](#workflow-description)
  - [rula all](#rule-all)
  - [rule fastp_se](rule-fastp_se)
  - [rule multiqc](rule-multiqc)
  - [rule minimap2_index](#rule-minimap2_index)
  - [rule minimap2](#rule-minimap2)
  - [rule samtools_decontaminated](#rule-samtools_decontaminated)
  - [rule bowtie2_build](#rule-bowtie2_build)
  - [rule bowtie2](#rule-bowtie2)
  - [rule woltka_gotu](#rule-woltka_gotu)
  - [rule woltka_classify](#rule-woltka-gotu)


## Getting started

~~~bash
git clone https://github.com/bioinf-mcb/polish-microbiome-project.git
cd shallow-shotgun-analysis-pipeline
~~~

## Workflow execution

Workflow is implemented as a straightforward metagenomic pipeline based on snakemake. It handles all steps from QC, adapter trimming, contamination removal, alignment, to classification. The final output of this workflow can be later used as a feature table and used for 

The scheme of the snakemake workflow for a single sample (not a DAG!!):

![scheme of workflow](resources/images/step1-dag.png?raw=true)

### Snakemake environment setup

The setup is based on creation of conda environment. Make sure you have [anaconda](https://www.anaconda.com/) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) installed. 

Create a conda environment with all dependencies (metagenomic analysis tools) used in snakemake rules workflow and snakemake dependencies itself. To do this execute the below command from `polish-gut-microbiome/`:

~~~bash
conda env create -n shallow-snakemake -f shallow-shotgun-analysis-workflow/workflow/envs/environment.yml
~~~

To use the environment: 

~~~bash
conda activate shallow-snakamake
~~~

### Configure snakemake

In order to execute the snakemake workflow, you will need two configuration files that are fed into Snakefile. 
- samples.yml - containing all input files (ID and directory). 
- config.yml - containing all parameters and other prerequisite data files to execute Snakefile

**samples.yml**
You can generate this file directly by executing `samples.py` located under `shallow-shotgun-analysis-workflow/workflow/samples.py` for example by the below command:

~~~bash
python samples.py INPUT_PATH OUTPUT_PATH
~~~

where: 
        *INPUT_PATH* - path to directory containing all raw samples. INPUT_PATH is traversed recursively and adds any file with `.fastq` or `.fq` in the file name with the file name minus extension as the sample ID.
        *OUTPUT_PATH* - path to directory where `samples.yml` will be saved. 

The file should look something like this:
~~~
samples:
    sampleid1: path/to/sampleid1.fastq.gz 
    sampleid2: path/to/sampleid2.fastq.gz
    .....
    .....
    .....
~~~

**config.yml**
This file is pre-built and can be found under `polish-microbiome-project/shallow-shotgun-analysis-workflow/config/config_template.yaml`. It allows you to pass all parameters to the workflow. Parameters were preset to suit shallow shotgun analysis specifically. For example parameters passed to Bowtie2 were chosen based on the ones implemented in [SHOGUN](https://github.com/knights-lab/SHOGUN).

Furthermore, each rule was prepared in a way that you can pass extra optional arguments except those explicitly given in `config_template.yml`. Just pass them to `config_template.yml` where variables like `rule_extra:` are defined the same way you would do this according to program's documentation.

#### NOTE: You can not execute the workflow without specifing a few requirements inside it. First you need to provide input definition for working directory - WORKDIR - where all results will be written.

#### Secondly you will need additional files like reference genomes or adapter sequence fasta file:
1) For rule fastp: a fasta file containing adapters sequence (`adapter_fasta: ''` in config file) prepared according to [fastp documenation](https://github.com/OpenGene/fastp).
2) For rule minimap2_index: `ref_hum_gen: ''` - path to reference contaminant genome file
3) For rule bowtie2_index: `ref_bac_gen: ''` #path to refernce genome file for alignment
4) For rule woltka_classify: woltka allows for different classification systems and methods. You need to provide and specify (with a flag) any hierarchy files you need in the `hierarchy: ''` in the config file.
More details about this files in the Description

### After you have both file don't forget to update config files directories in `Snakefile` (`polish-microbiome-project/shallow-shotgun-analysis-workflow/workflow/Snakefile`) under `#Load configuration dicts`

~~~python
#Load configuration dicts
configfile: "../config/samples.yml" #please change the path if your samples.yml file is saved under other directory   
samples = config.copy()

configfile: "../config/config_template.yml" #please change the path if your config.yml file is saved under other directory
~~~

### Execution

If you hahe done the configuration properly you should be able to execute the `Snakefile` from its directory.

Dry-run:

~~~bash
snakemake -n
~~~

Actual execution (all rules):

~~~bash
snakemake --cores X
~~~
where X is number of cores to use. Number of threads to use will be than determined based on threads = min(threads, cores), with threads taken form the config file.

You can try other types of execution according to [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/executing/cli.html) for example you may want to execute only a part of the workflow.

## Workflow description

### rule all


Execute all rules and get all outputs.



### rule fastp_se


This step implements [FASTP](https://github.com/OpenGene/fastp) - QC and adapter removal - **at this point only single end reads are allowed** 
1) comprehensive quality profiling for both before and after filtering data (quality curves, base contents, KMER, Q20/Q30, GC Ratio, duplication, adapter contents)
2) filter out bad reads (too low quality, too short, or too many N...)
3) cut adapters. Adapter sequences can be automatically detected, which means you don't have to input the adapter sequences to trim them

fastp_se first trims the autodetected adapter,then trims the adapters given by adapter_fasta one by one

HTML and JSON reports are saved. Unfortunately adapter_fasta removes the adapter_cutting section from the output html.



### rule multiqc 


Generates [MultiQC](https://github.com/ewels/MultiQC) report for all samples.

Reports are generated by scanning given directories for recognised log files. These are parsed and a single HTML report is generated summarising the statistics for all logs found. MultiQC reports can describe multiple analysis steps and large numbers of samples within a single plot, and multiple analysis tools making it ideal for routine fast quality control.



### rule minimap2_index


This rule implements one of two [minimap2](https://github.com/lh3/minimap2) - generates a minimizer index for the reference before mapping. 

This step requires you to provide reference contaminant genome file path to the config file (`ref_hum_gen: ''`). For example if you expact human conatmination you can obtain [human genome GRCh38, last major release, primary genome](https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.26/) and use it.
Minimap2 seamlessly works with gzip'd FASTA and FASTQ formats as input. You don't need to convert between FASTA and FASTQ or decompress gzip'd files first.



### rule minimap2


The second step of the minimap2 -  mapping to reference contamination based on index built in the previous step.



### rule samtools_decontaminated


After minimap2 has done mapping of the sample reads to contaminant genome we need to extract the reads that were not mapped - bacterial sequences. This is done in [SAMtools](http://samtools.sourceforge.net/). 

The output will be contamination free samples in `.fastq` format.



### rule bowtie2_index


First of the two steps in [Bowtie 2](https://github.com/BenLangmead/bowtie2) - building an index from refernce genome.

Will generate 6 index files (4 forward and two reverse) with bt2 suffix (small index) or bt2l (large index). An example of a reference genenome can be [NCBI RefSeq 82](https://ncbiinsights.ncbi.nlm.nih.gov/2017/05/15/refseq-release-82-now-public/) genome
Rep82 requires large index to pass, otherwise not all seqs will be loaded and the error will appear.

Refernce genome path needs to be provided to `ref_bac_gen: ''` in the config file.



### rule bowtie2

Bowtie 2 alignement. By default, Bowtie 2 performs end to end read alignment. That is, it searches for alignments involving all of the read characters.

Shallow shotgun sequences require special parameters (based on [SHOGUN](https://github.com/knights-lab/SHOGUN)).
Params from SHOGUN:

~~~
--no-unal,    Suppress SAM records for reads that failed to align.
-x database, index name base path
-S outfile, #output file, SAM by default
-np 1, penalty for having an N in either the read or the reference
-mp '1,1', mismatch penalty
-rdg '0,1', affine read gap penalty
-rfg '0,1', affine reference gap penalty
--score-min 'L,0,-0.02', score min based on a function
-f infile,  reads, fasta
--very-sensitive, same as: D 20 R 3 N 0 L 20 i s,1,0.50
-k 16, alignments_to_report
-p str, num threads
--reorder, guarantee sort order at the expense of more time and RAM
--no-hd, Suppress SAM header lines
~~~



### rule woltka_gotu


[Woltka](https://github.com/qiyunzhu/woltka) is a classifier. It serves as a middle layer between sequence alignment and community ecology analyses. Woltka processes alignments the mappings of query sequences against reference sequences (such as microbial genomes or genes) and infers the best placement of the queries in a hierarchical classification system.

In this rule gOTU analysis (gOTU is analogous to sOTU in 16S rRNA studies).

Returns a BIOM table tahn can be processed in QIIME 2 according to this [instructions](https://github.com/qiyunzhu/woltka/blob/master/doc/gotu.md).



### rule woltka_classify

Will peform a taxonomic profiling at given ranks ([details](https://github.com/qiyunzhu/woltka/blob/master/doc/hierarchy.md)). For this rule you are supposed to provide ranks to config files as well as obtain hierarchy files and pass them to hierarchy argument with appropriate flags. 

For every rank specified output directory will contain feature tables like phylum.biom, genus.biom and species.biom, each representing a taxonomic profile at one of the ranks.