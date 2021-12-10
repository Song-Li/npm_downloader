NUM_Thread=32
for V in $(seq 1 $NUM_Thread);
do 
  screen -S runscreen_$V -dm python package_downloader.py -c $NUM_Thread -i $V -r names.json -s ./success.cur
done
