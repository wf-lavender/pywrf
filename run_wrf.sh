WPS_DIR=$1
WRF_RUN_DIR=$2
date=$3
max_dom=$4
WRF_OUT_DIR=/data/wangf/wrfout_raw/${date}/
GSI_RUN_ROOT=/home/wangf/comGSIv3.5_EnKFv1.1/run/
GSI_RUN_DIR=${GSI_RUN_ROOT}/test/testarw/

echo enter WRF run dir: $WRF_RUN_DIR
cd $WRF_RUN_DIR

rm met_em*

ln -s ${WPS_DIR}/met_em* ${WRF_RUN_DIR}/

echo "**************************************************"
echo initialize model...
echo "**************************************************"
./real.exe

echo "**************************************************"
echo run GSI...
echo "**************************************************"
cd $GSI_RUN_ROOT

echo write station data to prepbufr... 
/home/wangf/local/bin/python /home/wangf/bufr_io/convert_bufr.py $date

rm -r $GSI_RUN_DIR
for dom in `seq 1 $max_dom`
do
  ./run_gsi_regional.ksh $date $dom
  mv ${GSI_RUN_DIR}/wrf_inout ${WRF_RUN_DIR}/wrfinput_d0${dom}
done

echo "**************************************************"
echo run WRF...
echo "**************************************************"
cd $WRF_RUN_DIR
mpirun -np 16 ./wrf.exe
if [ ! -d $WRF_OUT_DIR ]; then
    mkdir -p $WRF_OUT_DIR
fi
mv ${WRF_RUN_DIR}/wrfout* $WRF_OUT_DIR/

