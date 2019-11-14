owd=../data/wmt19_biomed_modified/

# Create a copy of align_validation_zh_en.txt
# for downstream modifications.
cp ../data/{wmt19_biomed,wmt19_biomed_modified}
mv $owd/align_validation_zh_en{.txt,.orig.txt}
join -1 1 -2 2 -t $'\t' \
-o 1.1 2.1 1.2 1.3 \
$owd/align_validation_zh_en.orig.txt \
<(sort -k2 $owd/mapdocs_zh_en.txt) \
| sort -V -k2 > $owd/align_validation_zh_en.txt
rm $owd/align_validation_zh_en.orig.txt


# The following manual modifications were made
# to improve the accuracy of alignment.
# doc1 (omitted <=> 10, NO_ALIGNMENT): changed to OK
# doc2 (2 <=> 3,4, TARGET_GREATER_SOURCE):  changed to 2,3 <=> 3,4
# doc2 (3 <=> omitted, NO_ALIGNMENT): same as above
# doc3 (3 <=> 5, TARGET_GREATER_SOURCE): changed to 3 <=> 5,6
# doc3 (4 <=> 6,7, SOURCE_GREATER_TARGET): changed to 4 <=> 7 
# doc5 (9 <=> 11,12, NO_ALIGNMENT): changed to OK
# doc6: removed, sentences not found. 
# doc7: removed, sentences not found. 
# doc8 (2 <=> 4,5,	TARGET_GREATER_SOURCE): changed to 2 <=> 4
# doc8	(3 <=> 6,7, SOURCE_GREATER_TARGET): changed to 3 <=> 5,6,7
# doc9 (1 <=> 1, SOURCE_GREATER_TARGET): removed 摘要 from source side.
# doc11 (1 <=> 1, SOURCE_GREATER_TARGET): removed 目的：
# doc12: removed, sentence not found.
# doc15: removed, sentence not found.
# doc16 (3 <=> 3,4,5, TARGET_GREATER_SOURCE): 3 <=> 3,4
# doc16 (4 <=> 6, SOURCE_GREATER_TARGET): 4 <=> 5,6
# doc18: removed, sentences not found.
# doc20 (4 <=> 5, SOURCE_GREATER_TARGET): changed to OK
# doc22, 23, 24, 27, 29: removed, sentences not found.
# doc30 (4 <=> 4, SOURCE_GREATER_TARGET): 4 <=> 4, 5
# doc34: removed, sentence not found.
# doc35 (1 <=> 1): removed 目的：
# doc35	(omitted <=> 3, NO_ALIGNMENT): changed to OK
# doc35 (4 <=> 5, SOURCE_GREATER_TARGET): 4 <=> 5,6
# doc35 (5 <=> 6,7,8, TARGET_GREATER_SOURCE): 5 <=> 7,8
# doc36	(1 <=> 1,2, TARGET_GREATER_SOURCE): changed to OK
# doc37: removed, sentences not found.
# doc38 (1 <=> 1): removed 目的：
# doc44,46: removed, sentences not found.
# doc47, 3 <=> 4,5,6,7, OVERLAP and doc47. 4 <=> 8, NO_ALIGNMENT: combined into 3,4 <=> 4,5,6,7,8.
# doc48 (3 <=> 3,4,5,6, SOURCE_GREATER_TARGET): 3 <=> 3,4,5,6,7 
# doc48 (omitted <=> 7): see above
# doc49 (1 <=> 1): removed 目的：
# dpc53: removed, sentences not found.
# doc55: removed, sentences not found.
# doc57: removed, sentences not found.
# doc58	(8 <=> 11, SOURCE_GREATER_TARGET): changed to OK
# doc60 (8 <=> 9, SOURCE_GREATER_TARGET): changed to OK
# doc61: removed, sentences not found.
# doc67, 68, 69, 78, 80: removed, sentences not found. 
# doc82 (3 <=> 5, SOURCE_GREATER_TARGET): changed to OK
# doc83, 85: removed, sentences not found
# doc90 (2 <=> 2, SOURCE_GREATER_TARGET): changed to TARGET_GREATER_SOURCE
# doc93 (1 <=> 2, SOURCE_GREATER_TARGET) and doc93 (omitted <=> 1, NO_ALIGNMENT): combined


# Extract sentences from medline_zh2en_{zh,en}.txt
# for evaluation.
awk 'BEGIN {FS = "\t"}; {print $3}' $owd/medline_zh2en_zh.txt \
	> $owd/medline_zh2en_zh.textonly.txt
awk 'BEGIN {FS = "\t"}; {print $3}' $owd/medline_zh2en_en.txt \
	> $owd/medline_zh2en_en.textonly.txt