ESIS -- Easy SLURM Isolated Scanner
***********************************

.. image:: https://zenodo.org/badge/696340026.svg
   :target: https://zenodo.org/badge/latestdoi/696340026

.. image:: https://github.com/daknuett/esis/actions/workflows/test_all.yml/badge.svg

.. image:: https://www.nfdi.de/wp-content/uploads/2021/12/PUNCH4NFDI-Logo_RGB.png 
   :target: https://www.nfdi.de/punch4nfdi/
   :width: 80px

.. contents::

For the Inpatient
=================

- Run a workflow:

    .. code-block:: sh

       esis run

- See the internal documentation:

    .. code-block:: sh

       esis doc

- Always useful:

    .. code-block:: sh

       esis --help


Introduction
============

ESIS is an attempt to provide a way to organize workflows for SLURM clusters.
This is a difficult task due to several reasons, including:

- Individual workflows / workflow steps may be resource intensive (orders of
  several TiB memory, orders of days runtime).
- Individual workflows / workflow steps may take a long time to develop.
- Input and output data may be large (orders of Terabytes).
- Resource allocation may take time (orders of days to weeks).
- Prevalence of exotic hardware.

ESIS therefore adapts a *do as little as possible* strategy. This is, of
course, not always entirely possible. One example is the handling of
dependencies.

Note that ESIS is **not** a full fledged workflow manager which handles 
communication between workflow steps or sets up the environment. 


Getting Started
===============

ESIS is based around four user-provided files:

``setup script``
    This script will prepare the working directory for the execution
    of the main process. Notably, if the main process is re-run,
    for instance when checkpointing is used, this script will not be re-run.

``sbatch template``
    This is a sbatch script template. All the SLURM specific settings are provided 
    in this template. ESIS then fills out the remaining information automatically:

        - ``WORKERSCRIPT`` is the script name that should be run. Notably, this will
          usually be ``../<worker script>``.
        - ``TASKARRAYDEFINITION`` is the SLURM array definition used to scan
          through parameters in parallel.
        - ``ESIS_PRIVATE`` should be a comment that will be used to handle
          dependencies. See `Handling Dependencies`_

``worker script``
    The script that will do the main task. It should use the ``SLURM_ARRAY_TASK_ID``
    to access parameters as such:

    .. code-block:: python

            taskid = int(os.environ["SLURM_ARRAY_TASK_ID"])
            with open(f"../parameters/parameters.{taskid}.json", "r") as fin:
                parameters = json.load(fin)

``parameter generator``
    This script will generate all parameters that should be used by the
    ``worker script``. It must print a single integer to ``stdout`` that is the
    number of generated parameter files. Parameter files are written as
    ``./parameters.<n>.json``.
    It may use the environment variable ``ESIS2_REQUIREMENTS`` to obtain paths
    to required workflow runs:

    .. code-block:: python
        
        requirements = json.loads(os.environ["ESIS2_REQUIREMENTS"])
        # {requirementname: path}

    The ``path`` is the path of the corresponding workflow working directory.
    See `Handling Dependencies`_.

``parameter includes``
    These are optional files that will be copied into the working directories.
    Usually used to share parameters among different workflows.
    The parameter generator should access it as such:
    
    .. code-block:: python

            with open("../includes/include_parameters.json") as fin:
                shared_parameters = json.load(fin)

How ESIS Works
--------------

To run the worker script, ESIS first makes a snapshot of 
the files mentioned above. It does so as follows:

- Create a new working directory (``wrkdir.*``). The name is computed from the
  files named above and the dependencies.
- Copy the worker script, parameter generator, and the includes.
- Run the parameter generator in ``wrkdir/parameters``.
- Generate the sbatch script ``sbatch.sh`` from the sbatch script template.
- Run the setup script.
- Go to ``wrkdir/cwd`` and ``sbatch ../sbatch.sh``.

For more information on how one can automatically handle dependent workflows,
see `Handling Dependencies`_.


Installing
==========

To install ESIS, clone the repository and install it using ``pip``:

.. code-block:: sh

    git clone https://github.com/daknuett/esis
    cd esis
    python3 -m pip install .

Alternatively, build a distribution and install the distribution:

.. code-block:: sh

   python3 -m build .

   cp dist/esis*.whl /path/to/whereever

   python3 -m pip install /path/to/whereever/esis*.whl

Using ESIS
==========

Setting up a Workflow
---------------------

Setting up a workflow is as simple as running 

.. code-block:: sh

   esis setup <setup script> <parameter generator> <sbatch template> <worker script> [<includes>]

This will generate the file ``wf.esis.json`` that contains everything that
``esis run`` will require. 

To set up dependencies, i.e., the current workflow requires the output of
a previous workflow, use 

.. code-block:: sh

   esis require <requirement workflow file> <requirement name>

The requirement name will be the key in ``ESIS2_REQUIREMENTS``.
See `Handling Dependencies`_.


Handling Dependencies
---------------------

Dependencies are, particularly in a high performance computing context, hard to
handle. ESIS therefore avoids getting too deep into handling dependencies.
Initially it was planned that the only handling of dependencies that ESIS
provides is telling the user that a required workflow run is *missing*.

Currently, ESIS handles dependencies as such: 

- Users can specify workflow files (usually called ``wf.esis.json``) that must
  have an up-to-date run.
- ESIS then provides the up-to-date working directory as ``requirementname:
  path`` JSON encoded dictionary to the parameter generator.
- The user is responsible for handling how workflows obtain data from other
  workflows.

To see how to notify ESIS of required workflows, see `Setting up a Workflow`_.
When invoking ``esis run`` the missing dependencies will be treated as a fatal
error. Then, the user should run the missing workflows explicitly.
Alternatively, it is possible to run a workflow and all its missing
dependencies automatically. This is done by invoking ``esis dependency``. 

Automatically running dependent workflows using ``esis dependency`` works as such:

- A graph of all workflows that are required to run the desired workflow is
  created. This includes all dependencies of dependencies.
- Weights are assigned to the workflows.
- The workflows are run according to their weights. Dependent workflows are run
  after their dependencies using ``SBATCH --dependency``. 

For this to work, a line containing ``#ESIS_PRIVATE`` is required 
in the block of sbatch settings.

.. code-block:: sh

   #SBATCH TASKARRAYDEFINITION
   #ESIS_PRIVATE

Extended features, like checkpointing are currently unsupported, see `Todos`_.

Todos
=====

- Implement freezing of dependencies.
- Implement export of workflow results.
- Implement ``libesis`` to handle checkpointing and exporting of workflow results.
