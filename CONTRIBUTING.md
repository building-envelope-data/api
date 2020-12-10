# How to contribute

To contribute to this API specification, you can ask a question, report a bug and suggest an enhancement.

## Table of content

[Ask a question](#ask-a-question)

[Report a bug](#report-a-bug)

[Suggest an enhancement](#suggest-an-enhancement)

[Test your contribution](#test-your-contribution)

## Ask a question

If you have a question, please read [README.md](https://github.com/ise621/building-envelope-data/blob/develop/README.md) and search our [wiki](https://github.com/ise621/building-envelope-data/wiki) and the [existing issues](https://github.com/ise621/building-envelope-data/issues) for the answer.

If you don't find the answer there, please raise a [new issue](https://github.com/ise621/building-envelope-data/issues/new) and add the tag `question`.

## Report a bug

If you find a technical mistake, please [raise an issue](https://github.com/ise621/building-envelope-data/issues/new), add the tag `bug` and describe the problem clearly.

Please fork the repository and show us how you would remove the bug. Please [test your solution](#test-your-contribution) and create a [GitHub Pull Request](https://github.com/ise621/building-envelope-data/compare) to propose your solution and describe the problem and the solution clearly. Please refer to the issue which is solved by your solution.

In this way, you contribute to a fast release of improved versions.

## Suggest an enhancement

If you want to suggest an enhancement, please [raise an issue](https://github.com/ise621/building-envelope-data/issues/new) and add the tag `enhancement`.

When you receive positive feedback, please fork the repository and show us how you would remove the bug. Please [test your solution](#test-your-contribution) and create a [GitHub Pull Request](https://github.com/ise621/building-envelope-data/compare) to propose your solution and describe the problem and the solution clearly. Please refer to the issue which is solved by your solution.

In this way, you contribute to a fast release of extended versions.

## Test your contribution

Please format and test your branch before commits.

Format your branch with [Prettier](https://prettier.io). If you use docker, run `make shell` to drop into a shell within a fresh Docker container. You can then run `make format` to format the code.

Verify that your commits pass the following tests:

- [ ] Run `make compile` to verify that all schemas are valid against the specification of GraphQL and JSON Schema.
- [ ] Run `make example` to verify that all examples are valid against the schemas.
- [ ] Run `make test` to verify that all tests from the folder `/valid/` are valid and all tests from the folder `/invalid/` are invalid against the schemas.
