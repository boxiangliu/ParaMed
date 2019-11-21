# Align NEJM articles manually to create a gold-standard.
# Randomly select 3 articles:
# These are articles are in /mnt/scratch/boxiang/projects/\
# med_translation/processed_data/preprocess/sentences/



# This section creates the alignment file.
# Use the following commands to open Chinese and English docs side-by-side:
sent_dir="/mnt/scratch/boxiang/projects\
/med_translation/processed_data/preprocess/sentences/"

awk '{print NR,$0}' $sent_dir/鼻咽癌的吉西他滨联合顺铂诱导化疗.zh | vim -
awk '{print NR,$0}' $sent_dir/鼻咽癌的吉西他滨联合顺铂诱导化疗.en | vim -

awk '{print NR,$0}' $sent_dir/饮水可对饮用含糖饮料产生多大程度的对抗作用.zh | vim -
awk '{print NR,$0}' $sent_dir/饮水可对饮用含糖饮料产生多大程度的对抗作用.en | vim -

awk '{print NR,$0}' $sent_dir/帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌.zh | vim -
awk '{print NR,$0}' $sent_dir/帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌.en | vim -

# NOTE: The results are placed in ../processed_data/preprocess/alignment/


# This section creates two files
# nejm_valid.en and nejm_valid.zh
out_dir="/mnt/scratch/boxiang/projects/med_translation/\
processed_data/preprocess/alignment/"

articles=(鼻咽癌的吉西他滨联合顺铂诱导化疗 \
	饮水可对饮用含糖饮料产生多大程度的对抗作用 \
	帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌)

[[ -f $out_dir/nejm_valid.zh ]] && rm $out_dir/nejm_valid.zh
[[ -f $out_dir/nejm_valid.en ]] && rm $out_dir/nejm_valid.en

count=0
for article in ${articles[@]}; do
	count=$(($count+1))
	
	for lang in zh en; do
		awk 'BEGIN {OFS="\t"}{print "doc"n,NR,$0}' n=$count \
		$sent_dir/$article.$lang.tok >> $out_dir/nejm_valid.$lang
	done
done
