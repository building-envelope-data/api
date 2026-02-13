# We use Debian as base image for the reasons given on
# https://pythonspeed.com/articles/base-image-python-docker-images/
# see https://www.debian.org
FROM debian:10.2-slim

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

#---------------------------------------------------------#
# Set locale to `en_US` and character encoding to `UTF-8` #
#---------------------------------------------------------#
# Inspired by https://stackoverflow.com/questions/28405902/how-to-set-the-locale-inside-a-debian-ubuntu-docker-container/38553499#38553499
# and https://daten-und-bass.io/blog/fixing-missing-locale-setting-in-ubuntu-docker-image/
RUN \
  # Retrieve new lists of packages
  apt-get update && \
  # Install `locales`
  DEBIAN_FRONTEND=noninteractive \
    apt-get install --assume-yes --no-install-recommends \
      locales && \
  # Set locale to `en_US.UTF-8`
  sed --in-place --expression \
    's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' \
    /etc/locale.gen && \
  dpkg-reconfigure --frontend=noninteractive \
    locales && \
  update-locale LANG=en_US.UTF-8 && \
  # Remove unused packages, erase archive files, and remove lists of packages
  apt-get autoremove --assume-yes && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*
# Set environment variable `LANG`
ENV LANG en_US.UTF-8

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

#----------------------------------------------#
# Install run-time system dependencies and pip #
#----------------------------------------------#
# * Python is an interpreted, high-level, general-purpose programming language,
#   see https://www.python.org
# * pip is a Python package installer, see https://pip.pypa.io/en/stable/
RUN \
  # Retrieve new lists of packages
  apt-get update && \
  # Install Fener's run-time system dependencies and pip
  apt-get install --assume-yes --no-install-recommends \
    python3 \
    python3-pip && \
  # Make the commands `python` and `pip` refer to `*3`
  ln --symbolic \
    /usr/bin/python3 /usr/bin/python && \
  ln --symbolic \
    pip3 /usr/bin/pip && \
  # Remove unused packages, erase archive files, and remove lists of packages
  apt-get autoremove --assume-yes && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

#--------------------------------------------#
# Install build Python packages dependencies #
#--------------------------------------------#
RUN \
  pip install --no-cache-dir \
    setuptools

#---------------------------#
# Install development tools #
#---------------------------#
# In particular,
# * GNU Make to run often needed commands, see https://www.gnu.org/software/make
# * Black as Python code formatter, see https://github.com/psf/black
# * Mypy as static type checker for Python, see http://mypy-lang.org
# * Pylint as bug and quality checker for Python, see https://www.pylint.org
# * pytest as automated-testing framework, see https://docs.pytest.org
# * Vulture to find dead Python code, see https://github.com/jendrikseipp/vulture
RUN \
  # Retrieve new lists of packages
  apt-get update && \
  # Install system development tools
  apt-get install --assume-yes --no-install-recommends \
    make && \
  # Install development tools
  pip install --no-cache-dir \
    autoflake \
    black \
    flake8 \
    mypy \
    pycodestyle \
    pyflakes \
    pylint \
    pytest \
    sphinx \
    vulture && \
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

#-----------------------------#
# Install Python dependencies #
#-----------------------------#
# See `packages.pip`
COPY --chown=me:us \
  ./requirements.txt .
ENV PATH /home/me/.local/bin:$PATH
RUN \
  pip install \
    --user \
    --no-cache-dir \
    -r ./requirements.txt

#-------------------------------------------#
# Set-up for containers based on this image #
#-------------------------------------------#
# Create mount points
VOLUME /app/
# VOLUME /home/me/.local

# Run commands within the process supervisor and init system `dumb-init`
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
# Make `bash` the default command
CMD ["bash"]
