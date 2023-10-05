02 Dependencies
***************

This example illustrates the use of dependent workflows.
It uses the same methods as 01 simple run, but has two workflows,
where the second depends on the first.

To run the example:

.. code-block:: sh

   cd A_prepare_data/
   esis setup setup.sh sbatch_template.sh produce_data.py generate_parameters.py
   cd ..
   
   cd B_analyze_data/
   esis setup setup.sh sbatch_template.sh extract_data.py generate_parameters.py
   esis require ../A_prepare_data/wf.esis.json

   esis dependency

