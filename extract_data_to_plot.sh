echo "Solution_space_size Toulbar_time QPackerAdv_exptime QPacker2000Q_exptime Rosetta_exptime QPackerAdv_best_matches_Toulbar QPacker2000Q_best_matches_Toulbar Rosetta_best_matches_Toulbar" > summary.txt
echo "Solution_space_size Toulbar_time QPackerAdv_exptime QPacker2000Q_exptime Rosetta_exptime QPackerAdv_best_matches_Toulbar QPacker2000Q_best_matches_Toulbar Rosetta_best_matches_Toulbar" > summary_lowestE.txt
echo "Solution_space_size Toulbar_time QPackerAdv_exptime QPacker2000Q_exptime Rosetta_exptime QPackerAdv_best_matches_Toulbar QPacker2000Q_best_matches_Toulbar Rosetta_best_matches_Toulbar" > summary_not_lowestE.txt
for f in `find . -name analysis.log`
do
    solsize=`grep "Solution space size" $f | awk '{print $4}'`
    test "$solsize" == "" && continue

    ttime=`grep "Toulbar2 time" $f | awk '{print $4}'`
    test "$ttime" == "" && ttime="N/A"

    qtime=`grep "QPacker expectation time to find best solution" $f | awk '{print $9}'`
    test "$qtime" == "" && qtime="N/A"

    q2000time=`grep "QPacker 2000Q expectation time to find best solution" $f | awk '{print $10}'`
    test "$q2000time" == "" && q2000time="N/A"

    rtime=`grep "Rosetta expectation time to find best solution" $f | awk '{print $9}'`
    test "$rtime" == "" && rtime="N/A"

    qbestislowest=`grep "QPacker best is Toulbar2 lowest energy" $f | awk '{print $7}'`
    test "$qbestislowest" == "" && qbestislowest="N/A"

    q2000bestislowest=`grep "QPacker 2000Q best is Toulbar2 lowest energy" $f | awk '{print $8}'`
    test "$q2000bestislowest" == "" && q2000bestislowest="N/A"

    rbestislowest=`grep "Rosetta best is Toulbar2 lowest energy" $f | awk '{print $7}'`
    test "$rbestislowest" == "" && rbestislowest="N/A"

    D_numrotamers=`grep "Geometric average number of rotamers per position, <D>:" $f | awk '{print $9}'`
    test "$D_numrotamers" == "" && continue

    N_numposns=`grep "Number of packable positions, N:" $f | awk '{print $6}'`
    test "$N_numposns" == "" && continue

    echo "$solsize $ttime $qtime $q2000time $rtime $qbestislowest $q2000bestislowest $rbestislowest $D_numrotamers $N_numposns" >> summary.txt
    test "$qbestislowest" == "TRUE" && echo "$solsize $ttime $qtime $q2000time $rtime $qbestislowest $q2000bestislowest $rbestislowest $D_numrotamers $N_numposns" >> summary_lowestE.txt || echo "$solsize $ttime $qtime $q2000time $rtime $qbestislowest $q2000bestislowest $rbestislowest" >> summary_not_lowestE.txt
    echo "Completed $f."
done
