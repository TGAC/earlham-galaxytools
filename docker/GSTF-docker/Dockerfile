FROM bgruening/galaxy-stable

ADD library_data.yml $GALAXY_ROOT/library_data.yml

# Install the workflow
RUN mkdir -p $GALAXY_HOME/workflows

# Copy workflow
ADD workflow/gstf.ga $GALAXY_HOME/workflows/

# Generate list of tools required by the workflow
RUN workflow-to-tools -w $GALAXY_HOME/workflows/gstf.ga -o $GALAXY_ROOT/gstf-tools.yml -l "GSTF workflow tools"

# Start Galaxy instance, install tools, workflow and set up data libraries
RUN startup_lite && \
    galaxy-wait && \
    shed-tools install -g http://localhost:8080 -a $GALAXY_DEFAULT_ADMIN_KEY -t $GALAXY_ROOT/gstf-tools.yml && \
    workflow-install --workflow_path $GALAXY_HOME/workflows/ -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD && \
    setup-data-libraries -i $GALAXY_ROOT/library_data.yml -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD

