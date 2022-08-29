echo "Solution_space_size QPacker_exptime Toulbar_time" > summary.txt
echo "Solution_space_size QPacker_exptime Toulbar_time" > summary_lowestE.txt
echo "Solution_space_size QPacker_exptime Toulbar_time" > summary_not_lowestE.txt
for f in `find . -name analysis.log`
do
    solsize=`grep "Solution space size" $f | awk '{print $4}'`
    test "$solsize" == "" && continue
    ttime=`grep "Toulbar2 time" $f | awk '{print $4}'`
    test "$ttime" == "" && continue
    qtime=`grep "QPacker expectation time to find best solution" $f | awk '{print $9}'`
    test "$qtime" == "" && continue
    bestislowest=`grep "QPacker best is Toulbar2 lowest energy" $f | awk '{print $7}'`
    echo "$solsize $ttime $qtime $bestislowest" >> summary.txt
    test "$bestislowest" == "TRUE" && echo "$solsize $ttime $qtime $bestislowest" >> summary_lowestE.txt || echo "$solsize $ttime $qtime $bestislowest" >> summary_not_lowestE.txt
    echo "Completed $f."
done
