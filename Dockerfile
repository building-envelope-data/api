# syntax=docker/dockerfile:1.6
# The above line fixes the Dockerfile frontend used by BuildKit. For details
# see https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md
# Available versions are listed on https://hub.docker.com/r/docker/dockerfile

# Use Node on Debian as base image, see
# https://hub.docker.com/_/node
FROM node:22.11-bookworm-slim

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
  userdel --remove node && \
  groupadd \
    --gid ${GID} \
    us && \
  useradd \
    --no-log-init \
    --create-home \
    --shell /bin/bash \
    --uid ${UID} \
    --gid us \
    me

#-------------------------------#
# Make `bash` the default shell #
#-------------------------------#
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
  # Remove unused packages and configuration files, erase archive files, and remove lists of packages
  apt-get autoremove --assume-yes --purge && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

#----------------------------------#
# Install system development tools #
#----------------------------------#
# * `jq` to slice, filter, map, and transform JSON data, see
#   https://stedolan.github.io/jq/
# * GNU Make to run often needed commands, see
#   https://www.gnu.org/software/make
# * Neovim to edit text files and to show the difference between files, see
#   https://neovim.io/
# * Node package manager to install Node development tools, see
#   https://www.npmjs.com
ENV NPM_VERSION=10.9.1
RUN \
  # Retrieve new lists of packages
  apt-get update && \
  # Install system development tools
  apt-get install --assume-yes --no-install-recommends \
    jq \
    make \
    neovim \
    npm \
    plantuml && \
  # Upgrade Node package manager
  npm install --global npm@${NPM_VERSION} && \
  # Remove unused packages and configuration files, erase archive files, and remove lists of packages
  apt-get autoremove --assume-yes --purge && \
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

#---------------------------#
# Install development tools #
#---------------------------#
# * GraphQL Inspector to serve, diff, introspect, coverage-check GraphQL
#   schemas, and to validate GraphQL fragments and operations against schemas,
#   see https://graphql-inspector.com
# * Another JSON Schema Validator (AJV) command-line interface to validate
#   schemas and files, see https://github.com/ajv-validator/ajv-cli
# * format-graphql to sort definitions and fields in GraphQL schemas, see
#   https://github.com/gajus/format-graphql
# * graphql-schema-linter to validate GraphQL schemas, see
#   https://github.com/cjoudrey/graphql-schema-linter
# * Prettier to format JSON and GraphQL code, see https://prettier.io
COPY --chown=me:us \
  package.json ./
COPY --chown=me:us \
  package-lock.json ./
RUN \
  # Install Node development tools specified in ./package.json with the exact
  # version from ./package-lock.json, see https://docs.npmjs.com/cli/ci.html
  npm ci --no-optional && \
  npm cache clean --force

#---------------------------#
# Prepare volumes and binds #
#---------------------------#
# Create empty directories /home/me/.vscode-server/*` for user `me` and group
# `us` to make the respective mounted volumes be owned by the user `me` and the
# group `us`. For an explanation for the Visual Studio Code Server directories
# see https://code.visualstudio.com/docs/remote/containers-advanced#_avoiding-extension-reinstalls-on-container-rebuild
RUN \
  mkdir --parents \
    /home/me/.vscode-server/extensions \
    /home/me/.vscode-server-insiders/extensions

#-------------------------------------------#
# Set-up for containers based on this image #
#-------------------------------------------#
# Create mount points to mount the project and the installed Node development
# tools.
VOLUME /app/
VOLUME /app/node_modules
VOLUME /home/me/.vscode-server/extensions
VOLUME /home/me/.vscode-server-insiders/extensions

# Run commands within the process supervisor and init system `dumb-init`
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
# Make `bash` the default command, see
# https://github.com/Yelp/dumb-init#using-a-shell-for-pre-start-hooks
CMD ["bash"]
