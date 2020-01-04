# Clean aligned sentences:

in_dir=/mnt/scratch/boxiang/projects/med_translation/\
processed_data/clean/

[[ ! -f $in_dir ]] && mkdir -p $in_dir

# Link train and valid files to a folder:
ln /mnt/scratch/boxiang/projects/med_translation/\
processed_data/alignment/moore/align/nejm.{en,zh} $in_dir

ln /mnt/scratch/boxiang/projects/med_translation/\
processed_data/preprocess/alignment/\
nejm_valid.parallel.tok.{zh,en} $in_dir

# Paste Chinese and English texts:
printf "train\t%s\n" {1..123086} > /tmp/nejm.train.index
paste /tmp/nejm.train.index $in_dir/nejm.{zh,en} > $in_dir/nejm.train

printf "valid\t%s\n" {1..998} > /tmp/nejm.valid.index
paste /tmp/nejm.valid.index $in_dir/nejm_valid.parallel.tok.{zh,en} > $in_dir/nejm.valid

cat $in_dir/nejm.train $in_dir/nejm.valid > $in_dir/nejm.all

# Log into docker image:
ssh asimovbld-1
docker run -it -d -v $in_dir:/var/input/ paracrawl/bitextor
docker exec -it 7f979ef28b82 "/bin/bash"

bifixer=/opt/bitextor/bifixer/bifixer/bifixer.py
scol=3
tcol=4
input=/var/input/nejm.all
output=/var/input/nejm.bifixer.all
srclang=zh
tgtlang=en

python3.6 $bifixer \
--scol $scol \
--tcol $tcol \
--aggressive_dedup \
$input $output $srclang $tgtlang

# Exit docker container:
python clean/rm_dup.py \
$in_dir/nejm.bifixer.all \
$in_dir/nejm.rm_dup.all


# Split the file into training and test
grep "^train" $in_dir/nejm.rm_dup.all | cut -f3-3 > $in_dir/nejm.train.zh
grep "^train" $in_dir/nejm.rm_dup.all | cut -f4-4 > $in_dir/nejm.train.en
grep "^valid" $in_dir/nejm.rm_dup.all | cut -f3-3 > $in_dir/nejm.valid.zh
grep "^valid" $in_dir/nejm.rm_dup.all | cut -f4-4 > $in_dir/nejm.valid.en