# buildingenvelopedata.org API specification

This specification of an Application Programming Interface (API) is designed to facilitate the exchange of data about building envelopes. Several [databases](https://github.com/building-envelope-data/database) use the same API specification to offer data about components. A [metabase](https://github.com/building-envelope-data/metabase) manages for example the identifiers of components and institutions which must be the same for all databases.

This API specification consists of [GraphQL](https://graphql.org) schemas to specify a GraphQL endpoint and [JSON Schemas](https://json-schema.org) to specify the format of the responses. GraphQL schemas are in the directory `./apis`. There is a [visualization of the GraphQL schema of the metabase](https://graphql-kit.com/graphql-voyager/?url=https://www.buildingenvelopedata.org/graphql/) and [of the database](https://graphql-kit.com/graphql-voyager/?url=https://www.solarbuildingenvelopes.com/graphql/). Example GraphQL queries and mutations are in the directory `./requests`. You can try the queries of the [tutorial](https://github.com/building-envelope-data/api/blob/develop/requests/metabase/tutorial.graphql) at the [GraphQL endpoint of the metabase](https://www.buildingenvelopedata.org/graphql/).

GraphQL queries deal with metadata about data sets. They are used to find suitable data sets. The response to a GraphQL query is in JSON. For example, [optical.json](https://github.com/building-envelope-data/api/blob/develop/schemas/optical.json) defines the metadata about an optical data set. It can include a URL as `locator` to download the pure data.

The format [BED-JSON](https://github.com/building-envelope-data/api/blob/develop/schemas/data.json) is used for the pure data. [solarTransmittanceReflectance.json](https://github.com/building-envelope-data/api/blob/develop/tests/valid/opticalData/solarTransmittanceReflectance.json) is an example of a pure data set. It must be valid against the JSON Schema [opticalData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/opticalData.json).

JSON schemas are in the directory `./schemas` and realistic example JSON files in the directory `./examples`. The directory `./tests/valid` provides test JSON files that must be valid and the directory `./tests/invalid` JSON files that must be invalid against the schema with the same name as the folder. There is a [schematic drawing of an optical data point](docs/diagrams/out/opticalData/opticalDataPointSchematicDrawing/opticalDataPointSchematicDrawing.png) and more [visualizations of optical examples](docs/diagrams/out/opticalData). There is also a [schematic drawing of a calorimetric data set](docs/diagrams/out/calorimetricData/calorimetricDataSchematicDrawing/calorimetricDataSchematicDrawing.png) and more [visualizations of calorimetric examples](docs/diagrams/out/calorimetricData).

The following introduction explains the structure for new users and the section "On your Linux machine" explains how you can work with the API specification.

[![Watch the video introduction](https://img.youtube.com/vi/QsulJnpvuh0/maxresdefault.jpg)](https://www.youtube.com/watch?v=QsulJnpvuh0)

## Table of Contents

[I don't want to read this whole thing, I just have a question!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)

[Introduction](#introduction)

- [With optical data as example](#with-optical-data-as-example)
- [In general for all domains](#in-general-for-all-domains)
- [Combining the GraphQL responses with the datasets](#combining-the-graphql-responses-with-the-datasets)
- [How was the data created?](#how-was-the-data-created)

[How to use this repository](#how-to-use-this-repository)

- [For beginners](#for-beginners)
- [In your web browser](#in-your-web-browser)
- [On your Linux machine](#on-your-linux-machine)

[Code of Conduct](#code-of-conduct)

[Implementation of the API specification](#implementation-of-the-api-specification)

[How to contribute](#how-to-contribute)

## I don't want to read this whole thing, I just have a question!

If you have a question, please read this [README.md](https://github.com/building-envelope-data/api/blob/develop/README.md) and search this repository with its [wiki](https://github.com/building-envelope-data/api/wiki), [discussions](https://github.com/building-envelope-data/api/discussions), [Questions and Answers](https://github.com/building-envelope-data/api/discussions/categories/q-a) and [existing issues](https://github.com/building-envelope-data/api/issues) for the answer.

If you don't find the answer there and if your question is related to the code, please raise a [new issue](https://github.com/building-envelope-data/api/issues/new) and add the tag `question`.

## Introduction

There are many domains of data such as optical, calorimetric, geometric, hygrothermal, life cycle and more. This introduction begins with optical data to illustrate the structure.

### With optical data as example

[solarTransmittanceReflectance.json](https://github.com/building-envelope-data/api/blob/develop/tests/valid/opticalData/solarTransmittanceReflectance.json) is a simple example how the nearnormal-hemispherical solar transmittance and reflectance can be exchanged. [infraredDataPointForDiagram.json](https://github.com/building-envelope-data/api/blob/develop/tests/valid/opticalData/infraredDataPointForDiagram.json) is an example for infrared values. [colorVisibleTransmittanceReflectance.json](https://github.com/building-envelope-data/api/blob/develop/tests/valid/opticalData/colorVisibleTransmittanceReflectance.json) is an example for visible optical properties. All three are examples of optical properties integrated over a range of wavelengths.

[spectrallyResolvedDataPointsForDiagram.json](https://github.com/building-envelope-data/api/blob/develop/tests/valid/opticalData/spectrallyResolvedDataPointsForDiagram.json) is an example of spectrally resolved optical data. To keep it simple, it includes only the values for three wavelenghts. [igsdbExampleClearlite-4_250903.json](https://github.com/building-envelope-data/api/blob/develop/examples/opticalData/igsdbExampleClearlite-4_250903.json) is a realistic optical data set which includes spectrally-resolved data as well as integral data.

These optical datasets must all be valid against the JSON Schema [opticalData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/opticalData.json). [opticalData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/opticalData.json) defines each key and is therefore the best source to learn more about the details of optical datasets.

In order to find such optical data sets, it's best to start with the GraphQL endpoint https://www.buildingenvelopedata.org/graphql/ as the entrance to the product data network. You can enter there for example the following query:

```
query {
  databases {
    edges {
      node {
        name
        allOpticalData(first: 3) {
          edges {
            node {
              componentId
              resourceTree {
                root {
                  value {
                    locator
                  }
                }
              }
            }
          }
          totalCount
          pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
          }
        }
      }
    }
  }
}
```

The field `locator` returns a URL which you can use to download the optical data set. The query is for all optical data of the product data network. You can use [pagination](https://graphql.org/learn/pagination/) to download all optical datasets. This example shows you that first GraphQL is used to search for the data sets before JSON data sets are downloaded. You find more query examples in [tutorial.graphql](https://github.com/building-envelope-data/api/blob/develop/requests/metabase/tutorial.graphql). Whenever you have questions regarding these queries, you find all details about them in the [GraphQL specification](https://github.com/building-envelope-data/api/blob/develop/apis/metabase.graphql).

### In general for all domains

For other domains hygrothermal, geometric, calorimetric and lifeCycle, it is helpful to understand the structure of this repository. For each domain, there is a JSON Schema like [hygrothermalData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/hygrothermalData.json), [geometricData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/geometricData.json), ... in the folder `./schemas`. The folder `./examples` provides realistic examples. Each example must be valid against the JSON Schema with the name of the subfolder. For example, the JSON files of `./examples/calorimetricData` must be valid against the JSON Schema [calorimetricData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/calorimetricData.json). The JSON Schema contains all information which you need to understand the content of the JSON files.

The folder `./tests/valid` contains JSON files which test specifically what their name indicates. Each test must be valid against the JSON Schema with the name of the subfolder. For example, the JSON files of `./tests/valid/hygrothermalData` must be valid against the JSON Schema [hygrothermalData.json](https://github.com/building-envelope-data/api/blob/develop/schemas/hygrothermalData.json). The folder `./tests/invalid` contains JSON files which must be invalid against the JSON Schema with the name of the subfolder.

The tests and examples help to understand the exchange of product data. They are also important for the development of this specification to ensure that a new feature does not compromise the existing features.

### Combining the GraphQL responses with the datasets

Usually, GraphQL is used to to query for datasets and then the dataset are downloaded as a JSON file. However, the response of a GraphQL query is valid JSON. Therefore, the GraphQL responses can be combined with the datasets to one large JSON file.

For example, [semitransparentBuildingIntegratedPhotovoltaicThermal.json](https://github.com/building-envelope-data/api/blob/develop/examples/component/severalDomains/semitransparentBuildingIntegratedPhotovoltaicThermal.json) must be valid against the JSON Schema [component.json](https://github.com/building-envelope-data/api/blob/develop/schemas/component.json). It contains the [central identifier](https://github.com/building-envelope-data/api/blob/5f56f029c97366ab42154527d03a76408eb2ae6c/examples/component/severalDomains/semitransparentBuildingIntegratedPhotovoltaicThermal.json#L2) of the component which is create when the component is registered in the metabase buildingenvelopedata.org. Each dataset of each domain has its own [decentral identifier](https://github.com/building-envelope-data/api/blob/5f56f029c97366ab42154527d03a76408eb2ae6c/examples/component/severalDomains/semitransparentBuildingIntegratedPhotovoltaicThermal.json#L6-L9) which is managed by the product database(s) which contain the datasets.

### How was the data created?

It is possible to define the method which was used to create a dataset. The methods must be registered in the metabase buildingenvelopedata.org . Each method receives its unique central identifier.

The test [integralAccordingToStandard.json](https://github.com/building-envelope-data/api/blob/develop/tests/valid/component/optical/integralAccordingToStandard.json) is an example of an optical dataset which was created according to [a standard](https://github.com/building-envelope-data/api/blob/5f56f029c97366ab42154527d03a76408eb2ae6c/tests/valid/component/optical/integralAccordingToStandard.json#L14-L20). The dataset which was used as the source of the calculation is defined in the [lines 25-31](https://github.com/building-envelope-data/api/blob/5f56f029c97366ab42154527d03a76408eb2ae6c/tests/valid/component/optical/integralAccordingToStandard.json#L25-L31). It would be possible to define [arguments](https://github.com/building-envelope-data/api/blob/5f56f029c97366ab42154527d03a76408eb2ae6c/tests/valid/component/optical/integralAccordingToStandard.json#L23) of the calculation method.

## How to use this repository

### For beginners

With you web browser, you can search our [wiki](https://github.com/building-envelope-data/api/wiki), the [issues](https://github.com/building-envelope-data/api/issues) and [pull requests](https://github.com/building-envelope-data/api/pulls) and contribute to them.

### In your web browser

In order to browse the code conveniently with [Codespaces](https://docs.github.com/en/codespaces/overview), open [building-envelope-data/api](https://github.com/building-envelope-data/api) in your favorite web browser, click on the button "Code" in the top-right corner, select the tab "Codespaces", and on the first usage click on `+` to create a new codespace and on subsequent usages click on the name of an existing codespace.

If you are developing this repository further, you can follow the description [With Docker](#with-docker). For example, you can test and format your contributions with

```
cp ./.env.sample ./.env
make shell
make compile
make examples
make test
make format
```

### On your Linux machine

In order to use our development tooling, for example, to format code and to run tests, follow the instructions below.

1. Open your
   [favorite shell](https://www.redhat.com/sysadmin/favorite-shell),
   for example, good old
   [Bourne Again SHell, aka, `bash`](https://www.gnu.org/software/bash/),
   the somewhat newer
   [Z shell, aka, `zsh`](https://www.zsh.org/),
   or shiny new
   [`fish`](https://fishshell.com/).
1. Install [Git](https://git-scm.com/) by running
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
1. Clone the source code by running
   ```shell
   git clone git@github.com:building-envelope-data/api.git
   ```
   and navigate into the new directory `building-envelope-data` by running
   ```shell
   cd building-envelope-data
   ```
1. Prepare your environment by running
   ```shell
   cp ./.env.sample ./.env
   ```
   and adjusting the copied environment to your needs.

#### With Docker

5. Install
   [Docker Desktop](https://www.docker.com/products/docker-desktop),
   and
   [GNU Make](https://www.gnu.org/software/make/).
1. List all GNU Make targets by running
   ```shell
   make help
   ```
   The targets `name`, `tag`, `build`, `remove`, `run`, `shell`,
   `remove-containers`, `remove-volumes`, and `serve` can be used to interface
   with Docker. The other ones can be used within `bash` inside a Docker
   container:
   - `compile` validates the JSON schemas against the
     [JSON Schema meta-schemas](https://json-schema.org/specification-links.html#draft-7)
     and the GraphQL schemas against the
     [GrahpQL specification](http://spec.graphql.org/June2018/),
   - `test` validates the tests against the schemas,
   - `examples` validates the examples against the schemas,
   - `format` formats source files,
   - `introspect` introspects the GraphQL schemas,
   - `dos2unix` converts Windows-style to UNIX-style line endings,
   - `install-tools` installs development tools from the lock file, and
   - `update-tools` updates development tools to the latest compatible minor
     versions.
1. Drop into `bash` with the working directory `/app`, which
   is mounted to the host's working directory, inside a fresh Docker container
   based on Debian Linux everything installed by running
   ```shell
   make shell
   ```
   If necessary, the Docker image is (re)built automatically, which takes
   a while the first time.
1. Do something with the project like validating the schemas by running
   ```shell
   make compile
   ```
1. Drop out of the container by running
   ```shell
   exit
   ```
   or pressing `Ctrl-D`.

#### Without Docker

5. Install
   [GNU Bash](https://www.gnu.org/software/bash/),
   [GNU Make](https://www.gnu.org/software/make/),
   and
   [npm](https://www.npmjs.com).
1. Install the development tools in `package.json` by running
   ```
   make install-tools
   ```
   which in particular installs the command-line interface for
   [Another JSON Schema Validator (AJV)](https://github.com/ajv-validator/ajv),
   namely
   [`ajv-cli`](https://github.com/ajv-validator/ajv-cli)
   as Node package to be executed through
   [`npx`](https://github.com/npm/npx),
   for example,
   ```
   npx ajv --help
   ```
1. Drop into `bash`.
1. Do something with the project as elaborated above.

Note that another
[POSIX-compatible shell](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18)
than GNU Bash should also do. See also the
[POSIX specification](https://pubs.opengroup.org/onlinepubs/9699919799/)
and the
[POSIX FAQ](http://www.opengroup.org/austin/papers/posix_faq.html).

Also note that GNU Make takes the shell from the variable `SHELL` or, if not
set, the program `/bin/sh`. See
[Choosing the Shell](https://www.gnu.org/software/make/manual/html_node/Choosing-the-Shell.html)

## Code of Conduct

Our [Code of Conduct](https://github.com/building-envelope-data/api/blob/develop/CODE_OF_CONDUCT.md) is the guideline of our collaboration.

## Implementation of the API specification

A database which implements this API specification is presented by https://github.com/building-envelope-data/database . A metadatabase wich implements this API specification is presented by https://www.buildingenvelopedata.org/ (front end) https://www.buildingenvelopedata.org/graphql/ (back end) and https://github.com/building-envelope-data/metabase (source code). The metadatabase manages for example the identifiers for components and institutions which must be the same for all databases. The databases manage the data sets of the components.

## How to contribute

If you are interested to contribute by questions, reporting bugs or suggesting enhancements, please see [CONTRIBUTING.md](https://github.com/building-envelope-data/api/blob/develop/CONTRIBUTING.md) for further details.
