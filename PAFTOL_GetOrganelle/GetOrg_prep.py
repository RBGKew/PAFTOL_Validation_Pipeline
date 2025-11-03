#!/usr/bin/env python
# coding: utf-8

##################################
# Author: Kevin Leempoel

# Copyright © 2020 The Board of Trustees of the Royal Botanic Gardens, Kew
##################################

import pandas as pd
import os; import sys
import argparse
from pathlib import Path


def main():
    ## Parameters
    parser = argparse.ArgumentParser(
        description='Prepare sample list for the organelle recovery pipeline.')
    parser.add_argument("--db", type=str, help="latest paftol_export")
    parser.add_argument("--DataSource", type=str, help="DataSource (e.g. PAFTOL, SRA)")
    parser.add_argument("--src_path", type=str, help="Absolute path to the directory with all the symlinks to the source files (e.g. /mnt/projects/...)")
    parser.add_argument("--rem_search", type=str, help="List completed samples if fasta or log exist")
    args = parser.parse_args()

    export_file = args.db
    DataSource = args.DataSource
    rem_search = args.rem_search
    src_path = Path(args.src_path)

    # Load export for datasource
    db = pd.read_csv(export_file)
    db = db[(db.DataSource==DataSource)]
    print("PAFTOL export loaded.\n")

    db = add_fastq_files_paths(db, DataSource)
    db = flag_existing_recoveries(db, DataSource)
    db = add_past_recoveries_metadata_from_logs(db, DataSource)
    todo_pt, todo_nr = get_input_files_for_missing_recoveries(db, DataSource, rem_search)
    todo_pt, todo_nr = check_if_fastq_files_exists(db, DataSource)
    save_recovery_pipeline_input_accessions_files(todo_pt, todo_nr)
    print("Done: prepared input files with accessions for recovery pipeline.")


def add_fastq_files_paths(db, DataSource, src_path):
    """
    Add Sample_Name, R1_path, and R2_path columns to db based on the DataSource.
    DataSource can be 'PAFTOL', 'GAP', or 'SRA'.
    """
    fastq_path = src_path
    if DataSource == 'PAFTOL':
        db['Sample_Name'] = 'PAFTOL_' + db['idSequence'].astype(int).astype('str').str.zfill(6)
        fastq_suffix = "R"
    elif DataSource == 'GAP':
        db['Sample_Name'] = 'GAP_' + db['idSequence'].astype(int).astype('str').str.zfill(6)
        fastq_suffix = "R"
    elif DataSource == 'SRA':
        db['Sample_Name'] = db['ExternalSequenceID']
        fastq_suffix = ""
    else:
        print('unknown action for',DataSource)
        sys.exit()
    db["R1_path"] = db['Sample_Name'].apply(lambda x: fastq_path / f"{x}_{fastq_suffix}1.fastq.gz")
    db["R2_path"] = db['Sample_Name'].apply(lambda x: fastq_path / f"{x}_{fastq_suffix}2.fastq.gz")
    print(db.shape[0],'samples in total')
    return db

def flag_existing_recoveries(db, DataSource):
    """
    Searches fasta files in fasta_pt and fasta_nr directories, if exist.
    Adds two boolean columns:
        - fasta_pt: True if there is a file <Sample_Name>_pt.fasta
        - fasta_nr: True if there is a file <Sample_Name>_nr.fasta
    """
    def mark_recovered(table, suffix):
        fasta_dir = f"fasta_{suffix}"
        path = os.path.join(DataSource, fasta_dir)
        if not os.path.isdir(path):
            table[f"{fasta_dir}"] = False
            print(f"{fasta_dir} directory does not exist.")
            return table
        files = [f for f in os.listdir(path) if f.endswith('.fasta')]
        if not files:
            table[f"{fasta_dir}"] = False
            print(f"No fasta files found in {fasta_dir}.")
            return table
        recovered = pd.Series(files).str.split(f"_{suffix}", expand=True)[0].unique()
        table[f"fasta_{suffix}"] = table["Sample_Name"].isin(recovered)
        print(f"{table[f'fasta_{suffix}'].sum()}/{len(table)} {suffix} recovered")
        return table

    db['fasta_pt'] = False
    db['fasta_nr'] = False
    db = mark_recovered(db, "pt")
    db = mark_recovered(db, "nr")
    return db


def add_past_recoveries_metadata_from_logs(db, DataSource):
    db = db.copy()
    db['log_pt'] = False
    db['log_nr'] = False
    db['error_pt'] = False
    db['error_nr'] = False

    log_path = os.path.join(DataSource, 'logs')
    os.makedirs(log_path, exist_ok=True)
    logs_df = pd.DataFrame(os.listdir(log_path), columns=['file'])

    if not logs_df.empty:
        # Add metadata to log file names
        logs_df['Sample_Name'] = logs_df['file'].str.split('log_', expand=True)[1]
        logs_df['Type'] = logs_df['Sample_Name'].str.split('.', expand=True)[1]
        logs_df['Sample_Name'] = logs_df['Sample_Name'].str.split('.', expand=True)[0]
        logs_df['Organelle'] = logs_df['Sample_Name'].str.split('_').str[-1]
        logs_df['Sample_Name'] = logs_df['Sample_Name'].str.replace('_nr','').str.replace('_pt','')
        logs_df['filesize'] = logs_df['file'].apply(lambda x: os.stat(os.path.join(log_path, x)).st_size)

        # Add True if log file exists
        db['log_pt'] = db['Sample_Name'].isin(
            logs_df.query("Type == 'log' and Organelle == 'pt'")['Sample_Name']
        )
        db['log_nr'] = db['Sample_Name'].isin(
            logs_df.query("Type == 'log' and Organelle == 'nr'")['Sample_Name']
        )

        # Add True if if log contains error
        err_pt = logs_df.query("Type == 'err' and Organelle == 'pt' and filesize > 0")
        err_nr = logs_df.query("Type == 'err' and Organelle == 'nr' and filesize > 0")
        db['error_pt'] = db['Sample_Name'].isin(err_pt['Sample_Name'])
        db['error_nr'] = db['Sample_Name'].isin(err_nr['Sample_Name'])

    # Show number of log files found
    print(db['log_pt'].sum(), '/', len(db), 'pt processed')
    print(db['log_nr'].sum(), '/', len(db), 'nr processed')
    # Show number of log files with error
    print(db['error_pt'].sum(), '/', len(db), 'error during pt recovery')
    print(db['error_nr'].sum(), '/', len(db), 'error during nr recovery')
    return db


def get_input_files_for_missing_recoveries(db, DataSource, rem_search):
    # TODO: use function for each data type instead of repeating code
    if rem_search == 'fasta':
        todo_pt = db[(db.fasta_pt==False)][['Sample_Name','R1_path','R2_path']]
        todo_nr = db[(db.fasta_nr==False)][['Sample_Name','R1_path','R2_path']]
    elif rem_search == 'log':
        todo_pt = db[(db.log_pt==False)][['Sample_Name','R1_path','R2_path']]
        todo_nr = db[(db.log_nr==False)][['Sample_Name','R1_path','R2_path']]
    if todo_pt.shape[0]>0:
        print('\n',todo_pt.shape[0],DataSource,'samples listed for pt recovery')
    if todo_nr.shape[0]>0:
        print('\n',todo_nr.shape[0],DataSource,'samples listed for nr recovery')
    return todo_pt, todo_nr


def check_if_fastq_files_exists(todo_pt, todo_nr):
    """
    Check existence and size of R1/R2 FASTQ files, and remove empty ones from
    tables.
    """
    def check_fastq_table(df):
        """
        Add existence and size columns, filter out missing or empty files.
        """
        if df.empty:
            return df
        df = df.copy()
        df['R1_path'] = df['R1_path'].astype(str)
        df['R2_path'] = df['R2_path'].astype(str)
        df['R1_exist'] = df['R1_path'].apply(os.path.exists)
        df['R2_exist'] = df['R2_path'].apply(lambda x: os.path.exists(x) if pd.notna(x) else False)
        df['R1_size'] = df['R1_path'].apply(lambda x: os.path.getsize(x) if os.path.exists(x) else 0)
        df['R2_size'] = df['R2_path'].apply(lambda x: os.path.getsize(x) if os.path.exists(x) else 0)

        # Drop rows where R1 is missing or empty
        df = df[(df['R1_exist']) & (df['R1_size'] > 0)]

        # Keep either paired-end (R1 & R2 exist) or valid single-end (R2 missing)
        df = df[(df['R2_exist']) | (df['R2_path'].isna())]

        # Identify problematic rows
        invalid = df[
            (~df['R1_exist']) | (df['R1_size'] == 0) |
            ((df['R2_exist']) & (df['R2_size'] == 0))
        ]

        # Keep only valid entries
        valid = df[
            (df['R1_exist']) & (df['R1_size'] > 0)
        ]

        return invalid, valid.sort_values(by='R1_size', ascending=False).reset_index(drop=True)

    todo_pt_invalid, todo_pt = check_fastq_table(todo_pt)
    todo_nr_invalid, todo_nr = check_fastq_table(todo_nr)

    todo_pt_invalid.to_csv("todo_pt_invalid.csv", index=False)
    todo_nr_invalid.to_csv("todo_nr_invalid.csv", index=False)
    print(f"Saved CSVs with {len(todo_pt_invalid)} invalid fastq metadata.")
    return todo_pt, todo_nr


def save_recovery_pipeline_input_accessions_files(DataSource, todo_pt, todo_nr):
    if todo_pt.shape[0]>0:
        #print(todo_pt.shape[0],'paired-end fastq files found')
        print(todo_pt.shape[0],'paired-end or single-end fastq files found')
        todo_pt[['Sample_Name','R1_path','R2_path']].to_csv(DataSource + '/remaining_pt.txt',index=False,header=None)
    else:
        print('no fastq file found or no sample to process, remaining list not written')
    if todo_nr.shape[0]>0:
        #print(todo_nr.shape[0],'paired-end fastq files found')
        print(todo_nr.shape[0],'paired-end or single-end fastq files found')
        todo_nr[['Sample_Name','R1_path','R2_path']].to_csv(DataSource + '/remaining_nr.txt',index=False,header=None)
    else:
        print('no fastq file found or no sample to process, remaining list not written')

# if todo_pt.shape[0]>0:
#     todo_pt['R1_exist'] = todo_pt.apply(lambda row: os.path.exists(row['R1_path']),axis=1)
#     todo_pt['R2_exist'] = todo_pt.apply(lambda row: os.path.exists(row['R2_path']),axis=1)
# if todo_nr.shape[0]>0:
#     todo_nr['R1_exist'] = todo_nr.apply(lambda row: os.path.exists(row['R1_path']),axis=1)
#     todo_nr['R2_exist'] = todo_nr.apply(lambda row: os.path.exists(row['R2_path']),axis=1)

# if todo_pt.shape[0]>0:
#     todo_pt = todo_pt[(todo_pt.R1_exist) & (todo_pt.R2_exist)]
#     print(todo_pt.shape[0],'paired-end fastq files found')
#     todo_pt[['Sample_Name','R1_path','R2_path']].to_csv(DataSource + '/remaining_pt.txt',index=False,header=None)

# if todo_nr.shape[0]>0:
#     print('\n',todo_nr.shape[0],DataSource,'samples listed for nr recovery')
#     todo_nr = todo_nr[(todo_nr.R1_exist) & (todo_nr.R2_exist)]
#     print(todo_nr.shape[0],'paired-end fastq files found')
#     todo_nr[['Sample_Name','R1_path','R2_path']].to_csv(DataSource + '/remaining_nr.txt',index=False,header=None)

if __name__ == "__main__":
    main()
