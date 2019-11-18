# Align NEJM articles manually to create a gold-standard.
# Randomly select 3 articles:
# These are articles are in /mnt/scratch/boxiang/projects/\
# med_translation/processed_data/preprocess/sentences/

# Use the following commands to open Chinese and English docs side-by-side:
cd ../processed_data/preprocess/sentences/

awk '{print NR,$0}' 鼻咽癌的吉西他滨联合顺铂诱导化疗.zh | vim -
awk '{print NR,$0}' 鼻咽癌的吉西他滨联合顺铂诱导化疗.en | vim -

awk '{print NR,$0}' 饮水可对饮用含糖饮料产生多大程度的对抗作用.zh | vim -
awk '{print NR,$0}' 饮水可对饮用含糖饮料产生多大程度的对抗作用.en | vim -

awk '{print NR,$0}' 帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌.zh | vim -
awk '{print NR,$0}' 帕妥珠单抗和曲妥珠单抗辅助治疗早期HER2阳性乳腺癌.en | vim -

# The results are placed in ../processed_data/preprocess/alignment/