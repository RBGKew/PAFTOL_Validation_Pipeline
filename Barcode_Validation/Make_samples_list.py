#!/usr/bin/env python
# coding: utf-8

##################################
# Author: Kevin Leempoel

# Copyright © 2020 The Board of Trustees of the Royal Botanic Gardens, Kew
##################################

# In[1]:


import pandas as pd
import argparse; import os


# In[2]:


parser = argparse.ArgumentParser()
parser.add_argument("--db"); parser.add_argument("--DataSource")
opts = parser.parse_args()
db_export_file = opts.db;  DataSource = opts.DataSource


# In[14]:


# Notebook only
# db_export_file = '../PAFTOL_DB/2021-07-05_paftol_export.csv'
# DataSource = 'OneKP'


# In[21]:


# Load data and keep entries for DataSource
db = pd.read_csv(db_export_file)
# Paul B changed: db.DataSource.replace({'Annotated genome':'AG','Unannotated genome':'UG'},inplace=True)
# NB - Paul B - for Release 4.0 doing AG and UG barcoding together; 'Data provider' can be done under PAFTOL data source
#               Also 'Assembled_transcriptome' could be done in the same way here
db.DataSource.replace({'Annotated genome':'genome','Unannotated genome':'genome','Data provider':'PAFTOL', 'Assembled transcriptome':'genome' },inplace=True)
#db = db[db.DataSource==DataSource].astype({'idSequence':'int','idPaftol':'int'})
#Paul B. - removed idPaftol - I don't think it is required - but could have changed it to idSpecimen
db = db[db.DataSource==DataSource].astype({'idSequence':'int'})
print(db.shape[0],DataSource,'samples')
# Paul B - removed check for fastq file name in PAFTOL db
# if db.R1FastqFile.isna().sum()>0:
#     print(db.R1FastqFile.isna().sum(),'samples have no R1FastqFile and are removed from further analysis')
#     db = db[db.R1FastqFile.notnull()] # Will not run samples that have no fastq files. Note: some are single end


# In[23]:


# Make Sample column
# Paul B changed:
if DataSource in ['OneKP','SRA','genome']:
    db['Sample'] = db['ExternalSequenceID']
elif DataSource in ['PAFTOL']:
    db['Sample'] = db['idSequence'].astype('str').apply(lambda x: 'PAFTOL_' + x.zfill(6))
elif DataSource in ['GAP']:
    db['Sample'] = db['idSequence'].astype('str').apply(lambda x: 'GAP_' + x.zfill(6))
else:
    print('could not find Datasource',DataSource)


# In[34]:


# Write samples table
print('\nWrite samples table',DataSource + '/' + DataSource + '_samples.csv')
#samples_df = db[['Sample','idSequencing', 'idPaftol', 'Family', 'Genus', 'Species']]    .rename(columns={'Family':'family','Genus':'genus','Species':'species'})
# Paul B. - removed 'Species' field (I don't think the species column is used anywhere); also removed idPaftol:
#           To get species  from TaxonName field, will have to split field and remove the 1st (genus) field - is an optional change I think
samples_df = db[['Sample','idSequence', 'Family', 'Genus']].rename(columns={'Family':'family','Genus':'genus'})
samples_df.to_csv(DataSource + '/' + DataSource + '_samples.csv',index=False)
print('First line:\n',samples_df[:1].to_string(index=False))


# In[48]:


# List existing validation cards and output list of samples to blast
samples_done = [filename.replace('BV_','').replace('.csv','') for filename in os.listdir(DataSource + '/Barcode_Validation/')]
print('\nfound',len(samples_done),'validation cards')
samples_todo = db[db.Sample.isin(samples_done)==False]
print(samples_todo.shape[0],'samples to blast, ',db[db.Sample.isin(samples_done)].shape[0],'samples done')


# In[46]:


samples_todo.Sample.to_csv(DataSource + '/Samples_to_barcode.txt',index=False,header=False)

