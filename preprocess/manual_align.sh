# Align NEJM articles manually to create a gold-standard.
# Randomly select 3 articles:
# These are articles are in /mnt/scratch/boxiang/projects/\
# med_translation/processed_data/preprocess/sentences/



# This section creates the alignment file.
# Use the following commands to open Chinese and English docs side-by-side:
# The following files are copied from ../processed_data/preprocess/archive/sentences/


cp 

sent_dir=../processed_data/preprocess/manual_align/input/

awk '{print NR,$0}' $sent_dir/doc1.zh | vim -
awk '{print NR,$0}' $sent_dir/doc1.en | vim -

awk '{print NR,$0}' $sent_dir/doc2.zh | vim -
awk '{print NR,$0}' $sent_dir/doc2.en | vim -

awk '{print NR,$0}' $sent_dir/doc3.zh | vim -
awk '{print NR,$0}' $sent_dir/doc3.en | vim -

awk '{print NR,$0}' $sent_dir/doc4.zh | vim -
awk '{print NR,$0}' $sent_dir/doc4.en | vim -

awk '{print NR,$0}' $sent_dir/doc5.zh | vim -
awk '{print NR,$0}' $sent_dir/doc5.en | vim -

awk '{print NR,$0}' $sent_dir/doc6.zh | vim -
awk '{print NR,$0}' $sent_dir/doc6.en | vim -

awk '{print NR,$0}' $sent_dir/doc7.zh | vim -
awk '{print NR,$0}' $sent_dir/doc7.en | vim -

awk '{print NR,$0}' $sent_dir/doc8.zh | vim -
awk '{print NR,$0}' $sent_dir/doc8.en | vim -

awk '{print NR,$0}' $sent_dir/doc9.zh | vim -
awk '{print NR,$0}' $sent_dir/doc9.en | vim -

awk '{print NR,$0}' $sent_dir/doc10.zh | vim -
awk '{print NR,$0}' $sent_dir/doc10.en | vim -

awk '{print NR,$0}' $sent_dir/doc11.zh | vim -
awk '{print NR,$0}' $sent_dir/doc11.en | vim -

awk '{print NR,$0}' $sent_dir/doc12.zh | vim -
awk '{print NR,$0}' $sent_dir/doc12.en | vim -

# NOTE: The results are placed in ../processed_data/preprocess/manual_align/alignment/align_validation_zh_en.txt


# This section creates two files
# nejm_valid.en and nejm_valid.zh
out_dir="/mnt/scratch/boxiang/projects/med_translation/\
processed_data/preprocess/manual_align/"

articles=(鼻咽癌的吉西他滨联合顺铂诱导化疗 \
	饮水可对饮用含糖饮料产生多大程度的对抗作用 \
	帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌 \
	转移性去势抵抗性前列腺癌的恩杂鲁胺耐药 \
	婴儿B群链球菌疾病预防指南更新 \
	黑种人理发店可帮助顾客降血压 \
	内科患者应用阿哌沙班和依诺肝素预防血栓形成的比较 \
	尼拉帕尼用于铂类敏感型复发性卵巢癌的维持治疗 \
	膀胱切除术的最佳手术方法：开放式手术与机器人辅助手术的比较 \
	1型糖尿病患者胰岛素治疗中加用sotagliflozin的效果 \
	HIV相关癌症和疾病 \
	2017年慢性阻塞性肺疾病诊断和治疗的GOLD指南)

[[ -f $out_dir/nejm_valid.zh ]] && rm $out_dir/nejm_valid.zh
[[ -f $out_dir/nejm_valid.en ]] && rm $out_dir/nejm_valid.en

[[ -f $out_dir/nejm_valid.tok.zh ]] && rm $out_dir/nejm_valid.tok.zh
[[ -f $out_dir/nejm_valid.tok.en ]] && rm $out_dir/nejm_valid.tok.en

count=0
for article in ${articles[@]}; do
	count=$(($count+1))
	
	for lang in zh en; do
		awk 'BEGIN {OFS="\t"}{print "doc"n,NR,$0}' n=$count \
		$sent_dir/$article.$lang.tok >> $out_dir/nejm_valid.tok.$lang

		awk 'BEGIN {OFS="\t"}{print "doc"n,NR,$0}' n=$count \
		$sent_dir/$article.$lang >> $out_dir/nejm_valid.$lang

	done
done


# The next step is to modify the manual align file
# 1. add doc# at the beginning of each line
# 2. add OK at the end of each line
# 3. add <=> between English and Chinese line numbers
# 4. append lines to $out_dir/align_validation_zh_en.txt


# Create validation set:
python3 utils/gen_para_corp.py \
	--align_fn ../processed_data/preprocess/manual_align/align_validation_zh_en.txt \
	--zh_fn ../processed_data/preprocess/manual_align/nejm_valid.tok.zh \
	--en_fn ../processed_data/preprocess/manual_align/nejm_valid.tok.en \
	--out_fn ../processed_data/preprocess/manual_align/nejm_valid.parallel.tok

python3 utils/gen_para_corp.py \
	--align_fn ../processed_data/preprocess/manual_align/align_validation_zh_en.txt \
	--zh_fn ../processed_data/preprocess/manual_align/nejm_valid.zh \
	--en_fn ../processed_data/preprocess/manual_align/nejm_valid.en \
	--out_fn ../processed_data/preprocess/manual_align/nejm_valid.parallel
