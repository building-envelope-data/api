# We use Debian as base image for the reasons given on
# https://pythonspeed.com/articles/base-image-python-docker-images/
# see https://www.debian.org
FROM debian:10.5-slim

##################
# As user `root` #
##################

# When you are on a Linux machine and when you run `docker build`, then set the
# `--build-arg`s `GID` and `UID` to your user id and its primary group id. This
# makes it seamless to use and generate files from within the shell of
# a running docker container based on this image and access those files later
# on the host.
ARG UID=1000
ARG GID=1000

#-------------------------------------------#
# Create non-root user `me` and group `us` #
#-------------------------------------------#
# which are used to run commands in later for security reasons,
# see https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b
RUN \
  addgroup --system --gid ${GID} us && \
  adduser --system --uid ${UID} --ingroup us me

#-------------------------------#
# Make `bash` the default shell #
#-------------------------------#
# In particular, `ln ... bash /bin/sh` makes Python's `subprocess` module use
# `bash` by default. If we want to make sure that `bash` is always used
# regardless of the default shell, we can pass `executable="/bin/bash"` to
# Python's `subprocess#run` function.
RUN \
  ln --symbolic --force \
    bash /bin/sh && \
  sed --in-place --expression \
    "s#bin/dash#bin/bash#" \
    /etc/passwd

#---------------------#
# Install `dumb-init` #
#---------------------#
# a minimal init system for Linux containers, see https://github.com/Yelp/dumb-init
RUN \
  # Retrieve new lists of packages
  apt-get update && \
  # Install `dumb-init`
  apt-get install --assume-yes --no-install-recommends \
    dumb-init && \
  # Remove unused packages, erase archive files, and remove lists of packages
  apt-get autoremove --assume-yes && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

#---------------------------#
# Install development tools #
#---------------------------#
# * GNU Make to run often needed commands, see
#   https://www.gnu.org/software/make
# * Node package manager to install Node development tools, see
#   https://www.npmjs.com
# * Another JSON Schema Validator (AJV) command-line interface to validate
#   schemas and files, see https://github.com/ajv-validator/ajv-cli
RUN \
  # Retrieve new lists of packages
  apt-get update && \
  # Install system development tools
  apt-get install --assume-yes --no-install-recommends \
    make \
    npm && \
  # Upgrade Node package manager to version 6.14.7
  npm install npm@6.14.7 -g && \
  # Install Node development tools
  npm install --global ajv-cli@3.2.1 && \
  npm install --global graphql-schema-linter && \
  npm install --global prettier@2.0.5 && \
  # Remove unused packages, erase archive files, and remove lists of packages
  apt-get autoremove --assume-yes && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

#-------------------------#
# Set-up `/app` directory #
#-------------------------#
# Make the `/app` directory link to the `/home/me/app` directory and make both
# be owned by the user `me` and the group `us`.
RUN \
  mkdir /home/me/app && \
  chown me:us /home/me/app && \
  ln --symbolic /home/me/app /app && \
  chown me:us --no-dereference /app

################
# As user `me` #
################
# Switch to the user `me`
USER me
ENV USER=me
# Make `/app` the default directory
WORKDIR /app

#-------------------------------------------#
# Set-up for containers based on this image #
#-------------------------------------------#
# Create mount points to mount the project and the installed Python
# dependencies.
VOLUME /app/

# Run commands within the process supervisor and init system `dumb-init`
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
# Make `bash` the default command
CMD ["bash"]
