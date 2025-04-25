#!/bin/bash

#SBATCH --job-name="GetOrg"
#SBATCH --export=ALL
#SBATCH --cpus-per-task=4
#SBATCH --partition=long,himem	# Paul B. changed from all; NB - himem (gruffalo), hmem (KewHPC)
#SBATCH --mem=80000
#SBATCH --ntasks=1
ncpu=4

# Paul B. removed: module load python/3
# Paul B. removed: module load blast bowtie2 spades
# Paul B. removed: module load getorganelle


sample_file=$1
org=$2
fastqFilePath=$3 	# Paul B. added: full path to files, replaces the 'Data' location
adapterFasta=$4 	# Paul B. added: for adding the adaptor file, as required (might not be supplied)	

iline=$(sed -n "$SLURM_ARRAY_TASK_ID"p $sample_file)
echo $iline
sample="$(cut -d',' -f1 <<<"$iline")"
echo $sample
file_path_R1="$(cut -d',' -f2 <<<"$iline")"
file_R1=`basename "$file_path_R1"`; file_R1=${file_R1/.gz/}
echo $file_R1
file_path_R2="$(cut -d',' -f3 <<<"$iline")"

### Paul B. checking path + filenames:
echo "R1 full file path: " $fastqFilePath/$file_path_R1
echo "R2 full file path: " $fastqFilePath/$file_path_R2

### Paul B. changed: if [ ! -z "$file_path_R2" ]; then - changed to -s to test whether R2 file exists, if not data is assumed to be single end.
###                  (applies to small amount of SRA data only to date) 
if [ -s "$fastqFilePath/$file_path_R2" ]; then
	file_R2=`basename "$file_path_R2"`; file_R2=${file_R2/.gz/}
	echo "Pair-end Mode" # Paul B. added
	echo $file_R2

	### Paul B. - added command to run read trimming but only if adaptor file is added:
	read1File='' # for use in GetOrganelle command
	read2File=''
	if [[ -s "${adapterFasta}" ]]; then
		echo "Trimming PE fastq files..."
		java -jar $TRIMMOMATIC PE \
		-threads $ncpu \
		-trimlog ${sample}_R1_R2_trimmomatic.log \
		$fastqFilePath/$file_path_R1 \
		$fastqFilePath/$file_path_R2 \
		${sample}_R1_trimmomatic.fastq.gz \
		${sample}_R1_trimmomatic_unpaired.fastq.gz \
		${sample}_R2_trimmomatic.fastq.gz \
		${sample}_R2_trimmomatic_unpaired.fastq.gz \
		ILLUMINACLIP:${adapterFasta}:2:30:10:2:true \
		> ${sample}_trimmomatic.log 2>&1
		### Paul B. - also testing without quality trimming (recommended by GetOrganelle) - removed:
		#LEADING:10 \
		#TRAILING:10 \
		#SLIDINGWINDOW:4:20 \
		#MINLEN:40 
		read1File=${sample}_R1_trimmomatic.fastq.gz
		read2File=${sample}_R2_trimmomatic.fastq.gz
		unmappedFastqFiles="-u ${sample}_R1_trimmomatic_unpaired.fastq.gz  ${sample}_R2_trimmomatic_unpaired.fastq.gz" # Ok if blank when no trimming is done
		echo "Trimmed files:"
		ls -alrt $read1File
		ls -alrt $read2File
		echo $unmappedFastqFiles
	else
		read1File=$fastqFilePath/$file_path_R1
		read2File=$fastqFilePath/$file_path_R2
	fi

	
	if [ $org == pt ] 
	then
		### Paul B. - added '--overwrite 'otherwise get organelle will not run if folder already exists
		### Paul B. - replaced Data/ with $fastqFilePath in all 6 places below to make the file location more flexible 
		### Paul B. changed: get_organelle_from_reads.py --overwrite -1 Data/$file_R1.gz -2 Data/$file_R2.gz -o GetOrg/"$sample"_pt \
		### Paul B deleted '--overwrite' option in 4 places below. No longer available in GetOrganelle v1.7.7.1, -o option overwrites instead
		### Paul B. changed: get_organelle_from_reads.py -1 $fastqFilePath/$file_path_R1 -2 $fastqFilePath/$file_path_R2 -o GetOrg/"$sample"_pt \
		get_organelle_from_reads.py -1 $read1File -2 $read2File $unmappedFastqFiles -o GetOrg/"$sample"_pt \
		--max-reads 536870912 -R 20 -k 21,45,65,85,105 -t $ncpu -F embplant_pt --zip-files > \
		logs/log_${sample}_pt.log 2> logs/log_${sample}_pt.err
	elif [ $org == nr ]
	then
		### Paul B. changed: get_organelle_from_reads.py --overwrite -1 Data/$file_R1.gz -2 Data/$file_R2.gz -o GetOrg/"$sample"_nr \
		### Paul B. changed: get_organelle_from_reads.py -1 $fastqFilePath/$file_path_R1 -2 $fastqFilePath/$file_path_R2 -o GetOrg/"$sample"_nr \
		get_organelle_from_reads.py -1 $read1File -2 $read2File $unmappedFastqFiles  -o GetOrg/"$sample"_nr \
		--max-reads 536870912 -R 10 -k 35,85,115 -t $ncpu -F embplant_nr --zip-files > \
		logs/log_${sample}_nr.log 2> logs/log_${sample}_nr.err
	fi
	# Delete the trimmed fastq.gz files only (NOT the original fastq files!):
	if [[ -s ${sample}_R1_trimmomatic.fastq.gz ]]; then rm ${sample}_R1_trimmomatic.fastq.gz ${sample}_R2_trimmomatic.fastq.gz; fi
	if [[ -s ${sample}_R1_trimmomatic_unpaired.fastq.gz ]]; then rm ${sample}_R1_trimmomatic_unpaired.fastq.gz ${sample}_R2_trimmomatic_unpaired.fastq.gz; fi
	if [[ -s ${sample}_R1_R2_trimmomatic.log ]]; then rm ${sample}_R1_R2_trimmomatic.log;fi
else
	echo "Single-end Mode"

	### Paul B. - added command to run read trimming but only if adaptor file is added:
	echo "Trimming SE fastq file..."
	read1File='' # for use in GetOrganelle command
	if [[ -s "${adapterFasta}" ]]; then
		java -jar $TRIMMOMATIC SE \
		-threads $ncpu \
		-trimlog ${sample}_R1_trimmomatic.log \
		$fastqFilePath/$file_path_R1 \
		${sample}_R1_trimmomatic.fastq.gz \
		ILLUMINACLIP:${adapterFasta}:2:30:10:2:true \
		> ${sample}_trimmomatic.log 2>&1
		### Paul B. - also testing without quality trimming (recommended by GetOrganelle) - removed:
		#LEADING:10 \
		#TRAILING:10 \
		#SLIDINGWINDOW:4:20 \
		#MINLEN:40 
		read1File=${sample}_R1_trimmomatic.fastq.gz
	else
		read1File=$fastqFilePath/$file_path_R1
	fi


	if [ $org == pt ] 
	then
		### Paul B. - added '--overwrite 'otherwise get organelle will not run if folder already exists  
		### Paul B changed: get_organelle_from_reads.py --overwrite -u Data/$file_R1.gz -o GetOrg/"$sample"_pt \
		### Paul B. changed: get_organelle_from_reads.py -u $fastqFilePath/$file_path_R1 -o GetOrg/"$sample"_pt \
		get_organelle_from_reads.py -u $read1File -o GetOrg/"$sample"_pt \
		--max-reads 536870912 -R 20 -k 21,45,65,85,105 -t $ncpu -F embplant_pt --zip-files > \
		logs/log_${sample}_pt.log 2> logs/log_${sample}_pt.err
	elif [ $org == nr ]
	then
		### Paul B. changed: get_organelle_from_reads.py --overwrite -u Data/$file_R1.gz -o GetOrg/"$sample"_nr \
		### Paul B. changed: get_organelle_from_reads.py -u $fastqFilePath/$file_path_R1 -o GetOrg/"$sample"_nr \
		get_organelle_from_reads.py -u $read1File -o GetOrg/"$sample"_nr \
		--max-reads 536870912 -R 10 -k 35,85,115 -t $ncpu -F embplant_nr --zip-files > \
		logs/log_${sample}_nr.log 2> logs/log_${sample}_nr.err
	fi
	# Delete the trimmed fastq.gz files only (NOT the original fastq files!):
	if [[ -s ${sample}_R1_trimmomatic.fastq.gz ]]; then rm ${sample}_R1_trimmomatic.fastq.gz; fi
	if [[ -s ${sample}_R1_R2_trimmomatic.log ]]; then rm ${sample}_R1_R2_trimmomatic.log; fi
fi

python ../GetOrg_Clean.py --path GetOrg/"$sample"_"$org"/



