doc = '''
ESIS2 Workflow Manager
**********************

This is an extensible minimal-replaceable workflow manager. 
It is meant to do two main things:
    - isolate your runs from the source directory
    - keep a little track of your dependencies

While doing so, it avoids being a requirement. I.e., its entire behaviour can 
be replaced by a few shell commands. Most notably, a workflow run, once set up,
does not require the workflow manager at all.

To keep these requirements, ESIS2 works as such:
    - an individual workflow consists of 4 files:
        - setup script (this is run to set up the working directory)
        - a sbatch template that will be turned into a sbatch script
        - a worker script that will be run by the sbatch script
        - a parameter generator script:
            - it generates parameter files for the worker script to read 
            - every slurm task in the array gets its own parameter file 
            - it prints the number of parameter files to stdout 
            - the parameter files will be in ``<workdir>/parameters``
        - optionally, a number of extra files that will be included 
          these are for sharing configuration data between individual workflows
            - they will be copied to ``<workdir>/includes``
            - the parameter generator should read them and use them to 
              generate the parameters
    - to run the workflow, ESIS2 will go to ``<workdir>/cwd`` and execute 
      ``sbatch ../sbatch.sh``
    - if the workflow requires other workflows, that can be added by running 
      ``esis require``
    - the ``<workdir>``s of the requirements will be passed to the generator 
      as a JSON encoded environment variable.

Requirements
============

- once a requirement has been added, esis will check if it has to be re-run 
  before the current workflow can be run 
- when using ``esis freeze-requirement`` the requirement can be frozen to one 
  specific hash
- the workdirs of the requirements will be passed to the generator scripts as 
  ``ESIS2_REQUIREMENTS`` environment variable
- currently unsupported are:
    - automatic running of required workflows (unless using ``esis dependency``)

Tips and Tricks
===============

- If you want to run dependencies automatically, add a line ``#ESIS_PRIVATE``
  in the block of your sbatch setting::

      #SBATCH -M whatever
      #SBATCH --time: 1:00:00
      #ESIS_PRIVATE

- For optimal behaviour, add the following line of code, that will tell ESIS,
  that the code completed successfully::

      with open("../__esis__/completed.state", "w") as status_file:
          status_file.write("1")

'''


dt_format_hr = "%d.%m.%Y-%H:%M:%S"
df_format_m = "%d%m%Y%H%M%S%f"

