06 Freezing Dependencies
************************

This example demonstrates freezing dependencies. It is the same as example 02
but the code of A_prepare_data is changed after running and the original result
is used in the second step.

To run the example:

.. code-block:: sh

   cd A_prepare_data/
   esis setup setup.sh sbatch_template.sh produce_data.py generate_parameters.py
   esis run 
   dependency_hash=$(ls | grep wrkdir | cut -c 8- | tail -1)
   echo "# trivial change" >> setup.sh
   cd ..
   
   cd B_analyze_data/
   esis setup setup.sh sbatch_template.sh extract_mass.py generate_parameters.py
   esis require ../A_prepare_data/wf.esis2.json data_generation
   esis freeze-requirement data_generation $dependency_hash

   esis run

