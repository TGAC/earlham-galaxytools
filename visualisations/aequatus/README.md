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
