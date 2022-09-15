for f in `ls -1 | grep "response\_" | grep -v "Mohit" | sed 's/response_//g'`
do
	echo $f
	cd response\_$f

	RFILE="../../../rosetta_benchmark_redo/problem_$f/rosetta_packer_summary.txt"
	if test -f $RFILE
	then
		TFILE="../../../../rosetta_comparison/qpacker_problem_description_$f/toulbar2_solution.txt"
		if test -f $TFILE
		then
			echo "$TFILE EXISTS"
			python3 ../analysis/get_all_slns.py ../../../../problems/qpacker_problem_description_$f\_full.txt ./ $TFILE $RFILE >analysis.log
		else
			#echo "$TFILE DNE"
			TFILE="../../../../rosetta_other_problems/qpacker_problem_description_$f/toulbar2_solution.txt"
			if test -f $TFILE
			then
				echo "$TFILE EXISTS"
				python3 ../analysis/get_all_slns.py ../../../../problems/qpacker_problem_description_$f\_full.txt ./ $TFILE $RFILE >analysis.log
			else
				echo "ERROR ERROR ERROR!  $TFILE DOES NOT EXIST!  Skipping and continuing."
			fi
		fi
	else
		echo "ERROR ERROR ERROR!  $RFILE DOES NOT EXIST!  Skipping and continuing."
	fi

	cd ..
done
