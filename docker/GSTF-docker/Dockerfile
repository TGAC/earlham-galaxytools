FROM bgruening/galaxy-stable

ADD library_data.yml $GALAXY_ROOT/library_data.yml

# Install the workflow
RUN mkdir -p $GALAXY_HOME/workflows

# Copy workflow
ADD workflow/gstf.ga $GALAXY_HOME/workflows/

# Gerante list of tools required for the workflow
RUN workflow-to-tools -w $GALAXY_HOME/workflows/gstf.ga -o gstf-tools.yml -l "GSTF workflow tools"

# Install tools from the list
RUN install-tools $GALAXY_ROOT/gstf-tools.yml && \
    /tool_deps/_conda/bin/conda clean --tarballs

# Start Galaxy instance, install workflow and set up data libraries
RUN startup_lite && \
    galaxy-wait && \
    workflow-install --workflow_path $GALAXY_HOME/workflows/ -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD && \
    setup-data-libraries -i $GALAXY_ROOT/library_data.yml -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD

