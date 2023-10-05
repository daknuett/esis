ESIS Example
************

This is a very boilerplate example on how ESIS works.
It requires sbatch. You might want to adapt ``sbatch_template.sh`` to 
your cluster.


- To set up the example, run the script ``setup_example.sh``.
    - This will generate a bunch of input files.
    - The files will be put into ``data/``.
- After the setup is done, run ``esis setup setup.sh sbatch_template.sh extract_mass.py generate_parameters.py``.
- Then run ``esis run``
