FROM bgruening/galaxy-stable

COPY gstf-tools.yml $GALAXY_ROOT/tools.yaml

RUN install-tools $GALAXY_ROOT/tools.yaml && \
    /tool_deps/_conda/bin/conda clean --tarballs


ADD library_data.yml $GALAXY_ROOT/library_data.yml



# Install the workflow
RUN mkdir -p $GALAXY_HOME/workflows
ADD workflow/gstf.ga $GALAXY_HOME/workflows/
RUN startup_lite && \
    galaxy-wait && \
    workflow-install --workflow_path $GALAXY_HOME/workflows/ -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD && \
    setup-data-libraries -i $GALAXY_ROOT/library_data.yml -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD

# Container Style for Sniplay/Southgreen
