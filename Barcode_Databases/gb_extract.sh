#!/bin/bash
#SBATCH --job-name="gb_extract"
#SBATCH --output=gb_extract_%j.out
#SBATCH --cpus-per-task=1
#SBATCH --partition=medium
#SBATCH --mem=8000

WCVP_TAXO_PATH=$1 # Absolute path to wcvp_taxo.py and wcvp_names.csv

python -u GB_extract.py NCBI_16s "$WCVP_TAXO_PATH"
python -u GB_extract.py NCBI_18s "$WCVP_TAXO_PATH"
python -u GB_extract.py NCBI_23s "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_26s "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_23s "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_rbcL "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_trnL "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_ITS1 "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_ITS2 "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_rpl2 "$WCVP_TAXO_PATH"
# python GB_extract.py NCBI_ndhf "$WCVP_TAXO_PATH"

