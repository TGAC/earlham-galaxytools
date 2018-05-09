Installation
------------

After installing the ``export_to_cluster`` tool, you need to setup an environment variable to specify the directory where users are expected to save their files. One way to do that is:

1) create a directory called ``EXPORT_DIR_PREFIX`` in your tool dependencies directory (which by default is ``database/dependencies/``, but can be changed in your Galaxy config file)
2) in this directory, create a file called ``env.sh`` with a content similar to the following template::

       EXPORT_DIR_PREFIX=/PATH/WHERE/TO/SAVE/FILES; export EXPORT_DIR_PREFIX

3) create a symlink called ``default`` inside the ``EXPORT_DIR_PREFIX`` directory pointing to the same directory, e.g.::

       $ cd TOOL_DEPENDENCIES_DIR/EXPORT_DIR_PREFIX/
       $ ln -s . default

Alternatively, you could define the ``EXPORT_DIR_PREFIX`` environment variable in your ``config/job_conf.xml`` file for the destination where the ``export_to_cluster`` tool is going to run (for an example, see ``_JAVA_OPTIONS`` in ``config/job_conf.xml.sample_advanced``), but this would define the environment variable also for all the other tools that use that destination (normally not a problem, but worth to mention).

