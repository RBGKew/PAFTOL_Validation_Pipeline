#!/bin/bash

#SBATCH --job-name="GetOrg"
#SBATCH --export=ALL
#SBATCH --cpus-per-task=4
#SBATCH --partition=long	# Paul B. changed from all
#SBATCH --mem=80000
#SBATCH --ntasks=1
ncpu=4

# Paul B. removed: module load python/3
# Paul B. removed: module load blast bowtie2 spades
# Paul B. removed: module load getorganelle


sample_file=$1
org=$2
fastqFilePath=$3 # Paul B. added: full path to files, replaces the 'Data' location

iline=$(sed -n "$SLURM_ARRAY_TASK_ID"p $sample_file)
echo $iline
sample="$(cut -d',' -f1 <<<"$iline")"
echo $sample
file_path_R1="$(cut -d',' -f2 <<<"$iline")"
file_R1=`basename "$file_path_R1"`; file_R1=${file_R1/.gz/}
echo $file_R1


file_path_R2="$(cut -d',' -f3 <<<"$iline")"

### Paul B. changed: if [ ! -z "$file_path_R2" ]; then - changed to -s to test whether R2 file exists, if not data is assumed to be single end.
###                  (applies to small amount of SRA data only to date) 
if [ -s "$file_path_R2" ]; then
	file_R2=`basename "$file_path_R2"`; file_R2=${file_R2/.gz/}
	echo $file_R2
	
	if [ $org == pt ] 
	then
		### Paul B. - added '--overwrite 'otherwise get organelle will not run if folder already exists
		### Paul B. - replaced Data/ with $fastqFilePath in all 6 places below to make the file location more flexible 
		### Paul B. changed: get_organelle_from_reads.py --overwrite -1 Data/$file_R1.gz -2 Data/$file_R2.gz -o GetOrg/"$sample"_pt \
		get_organelle_from_reads.py --overwrite -1 $fastqFilePath/$file_R1.gz -2 $fastqFilePath/$file_R2.gz -o GetOrg/"$sample"_pt \
		--max-reads 536870912 -R 20 -k 21,45,65,85,105 -t $ncpu -F embplant_pt --zip-files > \
		logs/log_${sample}_pt.log 2> logs/log_${sample}_pt.err
	elif [ $org == nr ]
	then
		### Paul B. changed: get_organelle_from_reads.py --overwrite -1 Data/$file_R1.gz -2 Data/$file_R2.gz -o GetOrg/"$sample"_nr \
		get_organelle_from_reads.py --overwrite -1 $fastqFilePath/$file_R1.gz -2 $fastqFilePath/$file_R2.gz -o GetOrg/"$sample"_nr \
		--max-reads 536870912 -R 10 -k 35,85,115 -t $ncpu -F embplant_nr --zip-files > \
		logs/log_${sample}_nr.log 2> logs/log_${sample}_nr.err
	fi
	
else
	echo "Single-end Mode"
	
	if [ $org == pt ] 
	then
		# Paul B. - added '--overwrite 'otherwise get organelle will not run if folder already exists  
		get_organelle_from_reads.py --overwrite -u Data/$file_R1.gz -o GetOrg/"$sample"_pt \
		--max-reads 536870912 -R 20 -k 21,45,65,85,105 -t $ncpu -F embplant_pt --zip-files > \
		logs/log_${sample}_pt.log 2> logs/log_${sample}_pt.err
	elif [ $org == nr ]
	then
		get_organelle_from_reads.py --overwrite -u Data/$file_R1.gz -o GetOrg/"$sample"_nr \
		--max-reads 536870912 -R 10 -k 35,85,115 -t $ncpu -F embplant_nr --zip-files > \
		logs/log_${sample}_nr.log 2> logs/log_${sample}_nr.err
	fi
fi

python ../GetOrg_Clean.py --path GetOrg/"$sample"_"$org"/



