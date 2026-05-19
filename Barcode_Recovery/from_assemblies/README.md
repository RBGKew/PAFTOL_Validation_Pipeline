# Organelle recovery from assemblies

This document summarizes the steps for the recovery of plastidial and ribosomal
sequences from genomic assemblies using Captus, with a focus on the preparation
of a custom target sequences file for ribosomal recovery. This strategy was
used prior to the data release 4.0 of the Kew Tree of Life. 

## 1. Plastid recovery

Use Captus extract with flag `--PTD_refs` with the Captus' plastid target file.

## 2. Nuclear ribosomes recovery

Use Captus extract with flag `--dna_refs` and a custom target file with the
coding and non-coding nuclear ribosomal sequences selected (18s and ITS2).

### Design of the nuclear ribosome target file

**Aim**: to preserve sequence diversity, avoiding redundancy and
overrepresentation.

**Input**: sequence data from NCBI and BOLD downloaded and filtered to
construct the barcode database that will be used downstream to assess the
family identity
(see https://github.com/RBGKew/PAFTOL_Validation_Pipeline/tree/barcode-db-review/Barcode_Databases)

- BOLD_ITS2.fasta
- NCBI_18s.fasta

**Rationale**: the barcode databases are large to be used as a sequence
recovery target file. To avoid having redundant sequences that would slow down
the recovery, cluster similar sequences for each marker sequence and then
combine them in a single file. 

**Tool**: VSEARCH (`conda install vsearch`):

- https://github.com/torognes/vsearch
- https://pubmed.ncbi.nlm.nih.gov/27781170


#### 1. Input fasta pre-edits

- Remove spaces before ";"
- Substitute other spaces by "\_" (e.g.:Genus_species).
- Rename: 18S_ribosomal_RNA with: rrn18 (the two names appeared in the same fasta).
- Eliminate ";" at the end of line.
- Add sequence name (used "gene" for consistency) to the ITS2 file:
`sed 's/^\([^;]*\);/\1;gene=ITS2;/' BOLD_ITS2.fasta > BOLD_ITS2_edited.fasta`

#### 2. Remove redundant sequences by clustering at different identity percentages

##### 2.1. Deduplication

Aim: to eliminate exact sequence duplicates.

```
vsearch --derep_fulllength <marker>.fasta \
--output <marker>_derep.fasta \
--sizeout \
--minuniquesize 1
```

##### 2.2. Clustering

Aim: to keep one representative sequence of a group of sequences within a
percentage of identity.

```
vsearch --cluster_fast <marker>_derep.fasta
--id 0.98
--centroids <marker>_98_centroids.fasta
```

##### 2.3. Clustering assessment

- Count number of sequences after each clustering (`grep -c "^>" <marker>.fasta`)
- Count family representation after each clustering:
```
grep '^>' <marker>.fasta | sed -n 's/.*f=\([^, ]*\).*/\1/p' | sort | uniq -c |
sort -nr > <marker>_fams.txt
```

**Clustering results**

| Marker | Step                          | # Sequences | # Families |
| ------ | ----------------------------- | ----------: | ---------- |
| ITS2   | Initial                       | 42,994      | 238        |
| ITS2   | Deduplication (100% identity) | 36,457      | 238        |
| ITS2   | Cluster at 98%                | 20,590      | 235        |
| ITS2   | Cluster at 97%                | 17,199      | 235        |
| 18S    | Initial                       | 4,981       | 382        |
| 18S    | Deduplication (100% identity) | 4,008       | 381        |
| 18S    | Cluster at 99%                | 1,527       | 341        |
| ITS2 97% + 18S 99%| Combine            | 18,726      | 378        |

#### 3. Edit target file headers

The headers must have the format:

\<Identifier\>-\<gene name\> \<other data\>

Actions:

- Delete "type=gene," and "type=rRNA,"
- Replace ",f=" by " f="
- Replace ";gene=" by "-"

### Recover sequences with Captus

Follow the same protocol as per the nuclear gene set recovery, but with
the options for plastid or miscellaneous DNA instead of coding nuclear DNA.

Note: see PhylogenomicsPipelines. Add flag to recover plastids or miscelaneous DNA.
