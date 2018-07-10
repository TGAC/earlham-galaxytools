Install the Aequatus visualisation on a Galaxy instance
=======================================================

1) Galaxy needs to be correctly configured to serve visualisation plugins, see e.g. https://galaxyproject.org/admin/config/nginxProxy/ if your server is behind a nginx proxy

2) If you haven't done that already, clone this Git repository somewhere on the Galaxy instance:

   ```
   git clone --recursive https://github.com/TGAC/earlham-galaxytools
   ```

   Instead, if you have already cloned the repository before, update it with:

   ```
   git pull
   git submodule update --init
   ```

3) Create a symbolic link to `earlham-galaxytools/visualisations/aequatus/` inside Galaxy's `config/plugins/visualizations/` directory, e.g.:

   ```
   cd GALAXY_DIR/config/plugins/visualizations/
   ln -s EARLHAM-GALAXYTOOLS_DIR/visualisations/aequatus/
   ```

Authors:
--------

<a href="http://github.com/anilthanki"> Anil Thanki</a>, <a href="http://github.com/nsoranzo"> Nicola Soranzo </a>, <a href="http://github.com/froggleston"> Rob Davey</a>


Citation:
---------
If you are using Aequatus for any kind of research purpose, Please cite us:

Thanki AS, Soranzo S, Haerty W. Herrero J, Davey RP. Aequatus: An open-source homology browser. bioRxiv 055632; doi: https://doi.org/10.1101/055632

[issues]:https://github.com/TGAC/earlham-galaxytools/issues

