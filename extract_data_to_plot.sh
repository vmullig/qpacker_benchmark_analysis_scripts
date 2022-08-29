echo "Solution_space_size Toulbar_time QPacker_exptime Rosetta_exptime QPacker_best_matches_Toulbar Rosetta_best_matches_Toulbar" > summary.txt
echo "Solution_space_size Toulbar_time QPacker_exptime Rosetta_exptime QPacker_best_matches_Toulbar Rosetta_best_matches_Toulbar" > summary_lowestE.txt
echo "Solution_space_size Toulbar_time QPacker_exptime Rosetta_exptime QPacker_best_matches_Toulbar Rosetta_best_matches_Toulbar" > summary_not_lowestE.txt
for f in `find . -name analysis.log`
do
    solsize=`grep "Solution space size" $f | awk '{print $4}'`
    test "$solsize" == "" && continue
    ttime=`grep "Toulbar2 time" $f | awk '{print $4}'`
    test "$ttime" == "" && continue
    qtime=`grep "QPacker expectation time to find best solution" $f | awk '{print $9}'`
    test "$qtime" == "" && continue
    rtime=`grep "Rosetta expectation time to find best solution" $f | awk '{print $9}'`
    test "$rtime" == "" && continue
    qbestislowest=`grep "QPacker best is Toulbar2 lowest energy" $f | awk '{print $7}'`
    rbestislowest=`grep "Rosetta best is Toulbar2 lowest energy" $f | awk '{print $7}'`
    echo "$solsize $ttime $qtime $rtime $qbestislowest $rbestislowest" >> summary.txt
    test "$qbestislowest" == "TRUE" && echo "$solsize $ttime $qtime $rtime $qbestislowest $rbestislowest" >> summary_lowestE.txt || echo "$solsize $ttime $qtime $rtime $qbestislowest $rbestislowest" >> summary_not_lowestE.txt
    echo "Completed $f."
done
