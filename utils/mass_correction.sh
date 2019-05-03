#!/bin/bash

APP='cp_scor'
SENSOR='4003'

EXE1="/Users/Home/Applications/hexplot/bin/HexPlot"
EXE2="/Users/Home/Cloud/Cernbox/hgcSensorTesting/hgcSensorTesting/Software/utilities/correct_cv.py"
DIR="/Users/Home/Cloud/Cernbox/hgcSensorTesting/hgcSensorTesting/Results/HPK_6in_135ch_${SENSOR}"
GEO="/Users/Home/Applications/hexplot/geo/hex_positions_HPK_128ch_6inch.txt"


# Full CV
python ${EXE2} -i ${DIR}/HPK_6in_135ch_${SENSOR}_CV.txt \
		--ocf ${DIR}/HPK_6in_135ch_Open_CV.txt \
		--scf ${DIR}/HPK_6in_135ch_Short_CV.txt \
		--cor 1 --inv 0 --freq 10000

# ${EXE1} -i ${DIR}/HPK_6in_135ch_${SENSOR}_CV_corrected.txt \
# 		-o ${DIR}/HPK_6in_135ch_${SENSOR}_CV_corrected.pdf \
# 		-g ${GEO} --select 300 --CV --colorpalette 113 -z 40:46


# Frequencies
# for FREQ in {1,5,10,20,50,100,1000}
# do
# 	python ${EXE2} -i ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV.txt \
# 			--ocf ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_Open_${FREQ}kHz_CV.txt \
# 			--scf ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_Short_${FREQ}kHz_CV.txt \
# 			--cor 1 --inv 1 --freq ${FREQ}000
#  	mv ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV_corrected.txt \
# 	   ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV_corrected_${APP}.txt
#
# 	${EXE1} -i ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV_corrected_${APP}.txt \
# 			-o ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV_corrected_${APP}.pdf \
# 			-g ${GEO} --select 400 --CV --colorpalette 113 -z 40:46
#
# 	${EXE1} -i ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV_corrected_${APP}.txt \
# 			-o ${DIR}/HPK_6in_135ch_${SENSOR}_${FREQ}kHz/HPK_6in_135ch_${SENSOR}_${FREQ}kHz_CV_corrected_zones_${APP}.pdf \
# 	 		-g ${GEO} --select 400 --CV --colorpalette 113 -p FLAT --sco greyout -z 40:46\
# 			--sc 10,19,20,28,30,31,40,41,42:13,22,23,24,34,35,36,37,46,47,48:87,97,98,100,110,111,121:91,92,93,94,103,104,105,114,115,116,124 \
# 			--scn "60 um:80 um:20 um:40 um"
# done

#--sc 10,18,19,20,28,29,30,31,40,41,42:13,22,23,24,34,35,36,37,46,47,48:87,88,97,98,99,100,110,111,112,121:91,92,93,94,103,104,105,114,115,116,124 \
