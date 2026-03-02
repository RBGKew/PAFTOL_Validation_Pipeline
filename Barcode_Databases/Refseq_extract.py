#!/usr/bin/env python
# coding: utf-8

##################################

# Copyright © 2020 The Board of Trustees of the Royal Botanic Gardens, Kew
##################################

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import pandas as pd
import os
import sys

ref = sys.argv[1]
# ref = 'Refseq_pt'
wcvp_taxo_path = sys.argv[2]
# wcvp_taxo_path = "/mnt/apps/user/.../PAFTOL_Validation_Pipeline/WCVP_Taxo"

fasta_file=f"{ref}.fasta"

records=[]
for record in SeqIO.parse("Refseq_pt.fasta", "fasta"):
    locus = record.id
    mol_type="genomic DNA"
    length = len(record.seq)
    parts = record.description.split()
    sci_name = " ".join(parts[1:3]) if len(parts) >= 3 else "NA"
    records.append({
    "Locus": locus,
    "mol_type": mol_type,
    "Len": length,
    "sci_name": sci_name
    })


rec_df = pd.DataFrame(records)

rm_char='[]()×'
for char in rm_char:
    rec_df['sci_name'] = rec_df['sci_name'].str.replace(char,'')

rec_df.groupby('sci_name').head(1).sci_name.to_csv(fasta_file.replace('.fasta','.csv'),index=False)

wcvp_taxo_script_path = os.path.join(wcvp_taxo_path, "wcvp_taxo.py")
wcvp_taxo_export_path = os.path.join(wcvp_taxo_path, "wcvp_names.csv")
print('running wcvp_taxo',end='...')
# print(os.system('python ../../PAFTOL_DB/wcvp_taxo.py ../../PAFTOL_DB/wcvp_v5_jun_2021.txt ' + \
#           fasta_file.replace('.fasta','_NCBI.csv') + ' -g -s similarity_genus -d divert_genusOK'))
print(os.system(f'python {wcvp_taxo_script_path} {wcvp_taxo_export_path} ' +           fasta_file.replace('.fasta','.csv') + ' -g -s similarity_genus -d divert_genusOK'))
wcvp = pd.read_csv(fasta_file.replace('.fasta','_wcvp.csv'))
wcvp = wcvp[wcvp.sci_name.notnull()]
print('found',wcvp.sci_name.nunique(),'species in WCVP')
print(rec_df.shape[0],end=' > ')
rec_df = pd.merge(rec_df.rename(columns={'sci_name':'Ini_sci_name'}),wcvp,how='inner',on='Ini_sci_name')
print(rec_df.shape[0])


for char in rm_char:
    rec_df['sci_name'] = rec_df['sci_name'].str.replace(char,'')

# delete sequences in fasta that don't have a reconciled name
locus_reconciled_names=set(rec_df["Locus"])
output_file=f"filtered_{fasta_file}"
with open(output_file, "w") as out_handle:
    for record in SeqIO.parse(fasta_file, "fasta"):
        if record.id in locus_reconciled_names:
            SeqIO.write(record, out_handle, "fasta")

rec_df[['Locus','mol_type', 'Len',
          'sci_name', 'kew_id','family', 'genus', 'species', 'infraspecies', 'Duplicates',
          'Ini_sci_name']].to_csv(fasta_file.replace('.fasta','_TAXO.csv'),index=False)
