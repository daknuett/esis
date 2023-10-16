05 Checkpoint Loading
*********************

Illustrates basic usage transferring data via checkpoints.

Run 

.. code:: sh

    cd A_train
    esis setup setup.sh sbatch_template.sh train_operator.py generate_parameters.py
    cd B_test
    esis setup setup.sh sbatch_template.sh test_operator.py generate_parameters.py
    esis require ../A_train/wf.esis2.json trained_weights

    esis dependency
    while [[ $(squeue -o %j | grep "05_B_") != "" ]]; do squeue; sleep 1; done

    wd=$(esis list | grep wrkdir)

    ls $wd/cwd/error.0.csv
    ls $wd/cwd/error.1.csv
