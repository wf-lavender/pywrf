date=$1
WPS_DIR=$2
run_geo=$3

cd $WPS_DIR

echo clean old data
rm FILE\:*
rm GRIBFILE*
rm met_em*

echo **************************************************
echo run WPS
echo **************************************************

if [ $run_geo == "True" ]; then
  echo run geogrid.exe...
  ./geogrid.exe
fi

echo "./link_grib.csh /data/wangf/gfs_forecast/${date}/gfs*" 
./link_grib.csh /data/wangf/gfs_forecast/${date}/gfs* 
if [ ! -e Vtable ]; then
  echo ln -s ungrib/Variable_Tables/Vtable.GFS Vtable
  ln -s ungrib/Variable_Tables/Vtable.GFS Vtable
fi

echo run ungirb.exe

./ungrib.exe

echo run metgrid.exe
./metgrid.exe


