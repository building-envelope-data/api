# Building Envelopes Data

[JSON Schema](https://json-schema.org)
schemas for building envelopes data. Schemas are located in the directory
`./schemas`, test JSON files that are supposed to be valid or invalid in the
directories `./tests/valid` and `./tests/invalid`, and examples in the
directory `./examples`.

With
[GNU Bash](https://www.gnu.org/software/bash/),
[GNU Make](https://www.gnu.org/software/make/),
and the command-line interface for
[Another JSON Schema Validator (AJV)](https://github.com/ajv-validator/ajv),
namely
[`ajv-cli`](https://github.com/ajv-validator/ajv-cli),
installed, within the Bash shell, the GNU Make target
* `help` lists available targets,
* `compile` validates the schemas against the JSON Schema meta-schemas,
* `test` validates the tests against the schemas,
* `example` validates the examples against the schemas, and
* `dos2unix` converts Windows-style to UNIX-style line endings.
