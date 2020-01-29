# This section creates the alignment file.
# Use the following commands to open Chinese and English docs side-by-side:

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

# NOTE: The results are placed in ../processed_data/preprocess/manual_align/alignment/align.txt
