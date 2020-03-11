# Use Bifixer to remove duplicated sentences from 
# alignment by Moore's algorithm.

in_dir=../processed_data/clean/concat/
out_dir=../processed_data/clean/clean/

ssh asimovbld-1
docker run -it -d -v /mnt/scratch/boxiang/projects/med_translation/processed_data/clean/concat:/var/input/ paracrawl/bitextor
docker exec -it 57cff38ed689 "/bin/bash"

bifixer=/opt/bitextor/bifixer/bifixer/bifixer.py
input=/var/input/all.align.txt
output=/var/input/all.bifixer.txt
srclang=zh
tgtlang=en

pip3 install unidecode
pip3 install xxhash
python3.6 $bifixer \
--scol 3 \
--tcol 4 \
--aggressive_dedup \
$input $output $srclang $tgtlang

# Exit docker container:
exit
mv $in_dir/all.bifixer.txt $out_dir/all.bifixer.txt

# Remove duplicated sentences
python3 clean/rm_dup.py \
$out_dir/all.bifixer.txt \
$out_dir/all.rm_dup.txt

# Remove the hash and the score columns:
mv $out_dir/all.rm_dup.txt temp
cut -f1-4 temp > $out_dir/all.rm_dup.txt
rm temp