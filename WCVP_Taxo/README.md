# wcvp_taxo
wcvp_taxo is a python3 script for matching and resolving scientific names against the WCVP database (https://wcvp.science.kew.org/)

## Input
### A. Input files
The script requires two input tables: The WCVP database and a file with species names to match on WCVP
1. **WCVP database**: must be downloaded from http://sftp.kew.org/pub/data-repositories/WCVP/. It will be filtered and save by the script in pickle format. If you whish to update the WCVP database, delete the .pkl file.
2. **Sample file**: This spreadsheet must be in **.csv** format and contain at least one column with the scientific names you wish to match in WCVP. By default the script will look for a column named **scientific_name** or **sci_name**. Otherwise it will look for a column called **Species**. If the species name is spread in two columns **(Genus, Species)**, the script with recognize it as well.

### B. Parameters
These parameters are optional and can be accessed with python wcvp_taxo.py -h
- **-oc, --only_changes**: Output file only contains IDs for which the WCVP taxonomy is different than provided (species, genus or family if provided)
- **-os, --simple_output**: Output file is simplified to a list of columns provided by the user (e.g. `['DataSource','Project']`) + the following 5 columns: `ID, kew-id, Ini_sci_name, sci_name, Duplicate_type`
- **-g, --resolve_genus**: Find taxa for scientific names written in `genus sp`. format
- **-v, --verbose**: verbose output in console
- **-s, --similar_tax_search**: Find most similar taxa for misspelled taxa. <br>
    Options are: 
	- **similarity**: Search for similar scientific name in WCVP (slow)
    - **similarity_genus**: Search for similar scientific name in WCVP assuming genus is correct (fast)
	- **request_kewmatch**: Search for similar scientific name using kewmatch (online) (do not use if you have a lot of queries)
- **-d, --duplicate_action**. Action to take when multiple wcvp entries exist for the provided scientific_name. <br>
    Options are: 
	- **rank**: (Default) reduce duplicates by prioritizing accepted > unplaced > synonym > homotypic_synonym  taxonomic status (keep first entry). 
	- **divert**: divert duplicates to `_duplicates.csv`
	- **divert_taxonOK**: divert duplicates to `_duplicates.csv`, unless all matching entries have the same taxon name in WCVP (keep first entry)
	- **divert_speciesOK**: divert duplicates to `_duplicates.csv`, unless all matching entries have the same species name in WCVP (keep first entry)
	- **divert_genusOK**: divert duplicates to `_duplicates.csv`, unless all matching entries have the same genus name in WCVP (keep first entry and rename as genus sp.)

## Example
```console
python wcvp_taxo.py wcvp_export.txt sample_file.csv
python wcvp_taxo.py wcvp_export.txt sample_file.csv -g -s similarity_genus -d divert
python wcvp_taxo.py wcvp_export.txt sample_file.csv --only_changes -s similarity -os ['ExternalSequenceID', 'DataSource', ''Ini_Genus','Ini_Species'] -s similarity -d rank
```

## Output
For the example above, the script will output the following tables:
* **sample_file_wcvp.csv**: Samples for which the scientific name are resolved.
* **sample_file_duplicates.csv**: Samples for which the scientific name matched multiple WCVP entries.
* **sample_file_unresolved.csv**: Samples for which the scientific name did not match any WCVP entries.


## Pipeline
### Pre-processing
* Load wcvp database. If only text file exist, saving as .pkl.
* Find column containing scientific names. scientific_name or sci_name (default), Species or Genus + Species otherwise.
* Search for column with unique IDs. First column in table will be selected. Creates column with unique IDs if it doesn't exist. Will not pick sci_name or Species as ID.

### Initial checks
* Check if Ini_Sci_name are written as Genus sp.
* Check if Ini_Sci_name exist in WCVP
* Optional. Find similar names if not in WCVP
* Check if Ini_Sci_name have duplicate entries
* Proceed to matching for valid scientific names

### Matching & Resolving
1. Find accepted and unplaced matches.
2. Resolves synonyms and homotypic synonyms. 
3. Resolve duplicates.
4. Output tables

## Dependencies
pandas, tqdm<br>
for similarity: difflib, requests, ast<br>
numpy, os, argparse, sys
