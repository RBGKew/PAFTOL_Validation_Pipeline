#!/bin/bash
#SBATCH --job-name="Barcode_Validation"
#SBATCH --export=ALL
#SBATCH --cpus-per-task=1
#SBATCH --partition=medium
#SBATCH --ntasks=1
#SBATCH --mem=4000

##################################
# Author: Kevin Leempoel

# Copyright © 2020 The Board of Trustees of the Royal Botanic Gardens, Kew
##################################

### Command ###
# ./Barcode_Validation.sh 2021-07-27_paftol_export.csv 'OneKP'

###source activate py36 #Paul B removed - activate env outside
slurmThrottle=10

### Inputs:
# latest paftol_export. Needs the following fields : idSequencing, idPaftol, DataSource, Family, Genus, Species
paftol_export=$1
# DataSource: PAFTOL, SRA, GAP, OneKP, AG, UG
DataSource=$2
### Paul B. altered: if [[ $DataSource == OneKP || $DataSource == AG || $DataSource == UG ]]
if [[ $DataSource == OneKP ]]
then
type="contigs"  # Paul B - for Release 4.0 this only applies now to OneKP contigs data; "type" is only used in Blast_on_barcodes.sh for picking up the fasta files
elif [[ $DataSource == PAFTOL || $DataSource == SRA || $DataSource == GAP || $DataSource == genome || $DataSource == 'OneKP_HP' ]]
then
type="pt_nr"
else
  echo "ERROR, invalid datasource $DataSource"
  exit 0
fi

# Paul B. - added to clause to rename OneKP data source back from OneKP_HP (HybPiper recovery with reads)
# to OneKP once OneKP_HP has directed down the pt_nr route above
if [[ $DataSource == 'OneKP_HP' ]]; then
   DataSource = 'OneKP'
fi

### Directories
# All Datasource directories are expected to be in the same working directory as paftol_export and should look like OneKP/in_fasta, OneKP/blast, PAFTOL/fasta_pt, PAFTOL/fasta_nr etc.
mkdir -p $DataSource/out_blast
mkdir -p $DataSource/Barcode_Validation

### List samples to blast by DataSource. 
# Samples with existing validation cards will be omitted
python Make_samples_list.py --db $paftol_export --DataSource $DataSource
### Paul B. - to use another sample list, can comment out the above call and 
### and create a Samples_to_barcode.txt file to use instead: format e.g. PAFTOL_000948

Nsamples=($(wc -l $DataSource/'Samples_to_barcode.txt'))
echo "blast $Nsamples samples on barcode databases" 
if (( $Nsamples > 0 )); then
	sbatch -p short --array=1-${Nsamples}%$slurmThrottle Blast_on_barcodes.sh $DataSource $type
fi