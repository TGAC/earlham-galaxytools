FROM bgruening/galaxy-stable

MAINTAINER Anil Thanki, Anil.Thanki@earlham.ac.uk

ENV GALAXY_CONFIG_BRAND="GeneSeqToFamily workflow"

# Adds list of tools not part of workflow
COPY tools.yml $GALAXY_ROOT/tools.yml

# Add data library
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
    shed-tools install -g http://localhost:8080 -a $GALAXY_DEFAULT_ADMIN_KEY -t $GALAXY_ROOT/tools.yml && \
    workflow-install --workflow_path $GALAXY_HOME/workflows/ -g http://localhost:8080 -a $GALAXY_DEFAULT_ADMIN_KEY && \
    setup-data-libraries -i $GALAXY_ROOT/library_data.yml -g http://localhost:8080 -a $GALAXY_DEFAULT_ADMIN_KEY

