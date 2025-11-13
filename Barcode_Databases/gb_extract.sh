#!/bin/bash
#SBATCH --job-name="gb_extract"
#SBATCH --output=gb_extract_%j.out
#SBATCH --cpus-per-task=1
#SBATCH --partition=medium
#SBATCH --mem=8000


python -u GB_extract.py NCBI_16s
python -u GB_extract.py NCBI_18s
python -u GB_extract.py NCBI_23s
# python GB_extract.py NCBI_26s
# python GB_extract.py NCBI_23s
# python GB_extract.py NCBI_rbcL
# python GB_extract.py NCBI_trnL
# python GB_extract.py NCBI_ITS1
# python GB_extract.py NCBI_ITS2
# python GB_extract.py NCBI_rpl2
# python GB_extract.py NCBI_ndhf
