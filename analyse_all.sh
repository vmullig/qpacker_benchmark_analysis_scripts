rm joblist.txt
for f in `ls -1 | grep "response_" | grep -v "Mohit" | sed 's/response_//g'`
do
	echo ${f}
	cd response_${f}

	RFILE="../../../rosetta_benchmark_redo/problem_${f}/rosetta_packer_summary.txt"
	TWOTHOUSANDQPATH="../../../from_Mohit_2000Q/2000Q_data/qpacker_problem_description_${f}_short"
	if test -d $TWOTHOUSANDQPATH
	then
		echo "Found 2000Q data in $TWOTHOUSANDQPATH"
	else
		echo "No 2000Q data found in $TWOTHOUSANDQPATH.  Skipping 2000Q analysis."
		TWOTHOUSANDQPATH="NONE"
	fi

	if test -f $RFILE
	then
		TFILE="../../../../rosetta_comparison/qpacker_problem_description_${f}/toulbar2_solution.txt"
		if test -f $TFILE
		then
			echo "$TFILE EXISTS"
			echo "cd response_${f} && python3 ../analysis/get_all_slns.py ../../../../problems/qpacker_problem_description_${f}_full.txt ./ $TWOTHOUSANDQPATH $TFILE $RFILE >analysis.log && cd .. && echo \"COMPLETED JOB ${f}.\"" >> ../joblist.txt
		else
			#echo "$TFILE DNE"
			TFILE="../../../../rosetta_other_problems/qpacker_problem_description_${f}/toulbar2_solution.txt"
			if test -f $TFILE
			then
				echo "$TFILE EXISTS"
			echo "cd response_${f} && python3 ../analysis/get_all_slns.py ../../../../problems/qpacker_problem_description_${f}_full.txt ./ $TWOTHOUSANDQPATH $TFILE $RFILE >analysis.log && cd .. && echo \"COMPLETED JOB ${f}.\"" >> ../joblist.txt
			else
				echo "ERROR ERROR ERROR!  $TFILE DOES NOT EXIST!  Skipping and continuing."
			fi
		fi
	else
		echo "ERROR ERROR ERROR!  $RFILE DOES NOT EXIST!  Skipping and continuing."
	fi

	cd ..
done

# Run the jobs on all cores:
cat joblist.txt | parallel -j 32
