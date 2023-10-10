03 Checkpointing
****************

Illustrates basic usage of checkpointing.

Run 

.. code:: sh

   esis setup setup.sh sbatch_template.sh check_results.py generate_parameters.py
   esis run
   wd=$(esis list | grep wrkdir)
   cd $wd
   while [[ $(squeue -o %j | grep "03_de") != "" ]]; do squeue; sleep 1; done

   python ../check_results.py
