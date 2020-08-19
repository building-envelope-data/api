# Building Envelopes Data

[JSON Schema](https://json-schema.org)
schemas for building envelopes data. Schemas are located in the directory
`./schemas`, test JSON files that are supposed to be valid or invalid in the
directories `./tests/valid` and `./tests/invalid`, and examples in the
directory `./examples`.

## On your Linux machine

1. Open your
   [favorite shell](https://www.redhat.com/sysadmin/favorite-shell),
   for example, good old
   [Bourne Again SHell, aka, `bash`](https://www.gnu.org/software/bash/),
   the somewhat newer
   [Z shell, aka, `zsh`](https://www.zsh.org/),
   or shiny new
   [`fish`](https://fishshell.com/).
2. Install [Git](https://git-scm.com/) by running
   ```shell
   sudo apt install git-all
   ```
   on
   [Debian](https://www.debian.org/)-based
   distributions like
   [Ubuntu](https://ubuntu.com/),
   or
   ```shell
   sudo dnf install git
   ```
   on
   [Fedora](https://getfedora.org/)
   and closely-related
   [RPM-Package-Manager](https://rpm.org/)-based
   distributions like
   [CentOS](https://www.centos.org/).
   For further information see
   [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
3. Clone the source code by running
   ```shell
   git clone git@github.com:ise621/building-envelope-data.git
   ```
   and navigate into the new directory `building-envelope-data` by running
   ```shell
   cd building-envelope-data
   ```

### With Docker

4. Install
   [Docker Desktop](https://www.docker.com/products/docker-desktop),
   and
   [GNU Make](https://www.gnu.org/software/make/).
5. List all GNU Make targets by running
   ```shell
   make help
   ```
   The targets `name`, `tag`,
   `build`, `remove`, and `shell` can be used to interface with Docker. The
   other ones can be used within `bash` inside a Docker container:
   - `compile` validates the schemas against the JSON Schema meta-schemas,
   - `test` validates the tests against the schemas,
   - `example` validates the examples against the schemas, and
   - `dos2unix` converts Windows-style to UNIX-style line endings.
6. Drop into `bash` with the working directory `/app`, which
   is mounted to the host's working directory, inside a fresh Docker container
   based on Debian Linux everything installed by running
   ```shell
   make shell
   ```
   If necessary, the Docker image is (re)built automatically, which takes
   a while the first time.
7. Do something with the project like validating the schemas by running
   ```shell
   make compile
   ```
   validating the tests by running
   ```shell
   make test
   ```
   and validating the examples by running
   ```shell
   make example
   ```
8. Drop out of the container by running
   ```shell
   exit
   ```
   or pressing `Ctrl-D`.

### Without Docker

4. Install
   [GNU Bash](https://www.gnu.org/software/bash/),
   [GNU Make](https://www.gnu.org/software/make/),
   and the command-line interface for
   [Another JSON Schema Validator (AJV)](https://github.com/ajv-validator/ajv),
   namely
   [`ajv-cli`](https://github.com/ajv-validator/ajv-cli).
5. Drop into `bash`.
6. Do something with the project as elaborated above.

Note that another
[POSIX-compatible shell](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18)
than GNU Bash should also do. See also the
[POSIX specification](https://pubs.opengroup.org/onlinepubs/9699919799/)
and the
[POSIX FAQ](http://www.opengroup.org/austin/papers/posix_faq.html).

Also note that GNU Make takes the shell from the variable `SHELL` or, if not
set, the program `/bin/sh`. See
[Choosing the Shell](https://www.gnu.org/software/make/manual/html_node/Choosing-the-Shell.html)
