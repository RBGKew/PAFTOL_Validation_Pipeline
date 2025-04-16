#!/bin/bash
# Paul B. removed: module load python/3

# Only arguments needed are DataSource and paftol_export
# e.g: ./GetOrg_Pipeline.sh 2021-07-27_paftol_export.csv "PAFTOL"

### Paul B. modified usage to:
### Working dir: paftol/Organelles[_PAFTOL2.0]
### ./GetOrg_Pipeline.sh <paftol_export_file>  <datasource> <path_to_all_fastq_files> <sample_list>
### Example: ./GetOrg_Pipeline.sh 2021-07-27_paftol_export.csv  PAFTOL  \
###          /mnt/shared/projects/rbgk/projects/paftol/AllData_symlinks_PAFTOL2.0  sample_list.csv
### Format for <sample_list>: idSequence,R1_fastq_file_name,R2_fastq_file_name
###
### Note:
### 1.There is now only one sample list controlling which "pt" and "nr" runs are done - hope that's OK
### 2.The <paftol_export_file> is only used by GetOrg_prep.py - but leaving for now

paftol_export=$1	# Paul B.: required by GetOrg_prep.py only
DataSource=$2
fastqFilePath=$3	# Paul B. added: replaces 'Data' folder in GetOrg_array.sh lines ~37 and ~42
sampleList=$4		# Paul B. added: for manually creating list of samples to run and their fastq file names 		
rem_search="fasta" # log or fasta
slurmThrottle=5


## Make lists of remaining  samples that have no organelles recovered
### Paul B. - can remove the next 3 lines for tests and prpare the remaining_*.txt fime manually 
# Paul B. removed: rm -f $DataSource/remaining_pt.txt
# Paul B. removed: rm -f $DataSource/remaining_nr.txt;
# Paul B. removed: python GetOrg_prep.py --db $paftol_export --DataSource $DataSource --rem_search $rem_search


## Go to dir and create working directories
mkdir -p $DataSource	# Paul B. added
cd $DataSource
mkdir -p GetOrg; mkdir -p logs; mkdir -p fasta_pt; mkdir -p fasta_nr; mkdir -p Archives;


### Paul B. removed copying of fastq files - will use files/symlinks from the existing areas
## Copy .fastq.gz files in currrent Data directory
# mkdir -p Data;
# while read iline; do
# 	file_path_R1="$(cut -d',' -f2 <<<"$iline")"
# 	file_R1=`basename "$file_path_R1"`; file_R1=${file_R1/.gz/}
# 	echo $file_R1
# 	cp -n $file_path_R1 Data/$file_R1.gz

# 	file_path_R2="$(cut -d',' -f3 <<<"$iline")"
# 	if [ ! -z "$file_path_R2" ]; then
# 		file_R2=`basename "$file_path_R2"`; file_R2=${file_R2/.gz/}
# 		echo $file_R2
# 		cp -n $file_path_R2 Data/$file_R2.gz
# 	else
# 		echo "No R2"
# 	fi
# done < remaining_pt.txt

# while read iline; do
# 	file_path_R1="$(cut -d',' -f2 <<<"$iline")"
# 	file_R1=`basename "$file_path_R1"`; file_R1=${file_R1/.gz/}
# 	echo $file_R1
# 	cp -n $file_path_R1 Data/$file_R1.gz

# 	file_path_R2="$(cut -d',' -f3 <<<"$iline")"
# 	if [ ! -z "$file_path_R2" ]; then
# 		file_R2=`basename "$file_path_R2"`; file_R2=${file_R2/.gz/}
# 		echo $file_R2
# 		cp -n $file_path_R2 Data/$file_R2.gz
# 	else
# 		echo "No R2"
# 	fi
# done < remaining_nr.txt


## Launch remaining pt
a=($(wc $sampleList)); Ns_pt=${a[0]}; echo $Ns_pt
if (( $Ns_pt > 0 )); then
	### Paul B changed: sbatch --array=1-${Ns_pt}%$slurmThrottle ../GetOrg_array.sh remaining_pt.txt "pt"
	sbatch --array=1-${Ns_pt}%$slurmThrottle ../GetOrg_array.sh ../${sampleList} "pt"
fi

## Launch remaining nr
a=($(wc $sampleList)); Ns_nr=${a[0]}; echo $Ns_nr
if (( $Ns_nr > 0 )); then
	### Paul B changed: sbatch --array=1-${Ns_nr}%$slurmThrottle ../GetOrg_array.sh remaining_nr.txt "nr"
	sbatch --array=1-${Ns_nr}%$slurmThrottle ../GetOrg_array.sh ../${sampleList} "nr"
fi
