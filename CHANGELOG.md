# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Document previously undocumented database GraphQL schema #101
- Add more tooling for GraphQL schema, queries, and mutations #104
- Add query examples for `data`, `allData`, and `hasData` #105
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

### Changed

- Improve propositions used in GraphQL queries to search for data #102
- Further align database GraphQL schema and JSON schema #103
- Flatten data HTTP resource trees to make them queryable with one query without having to know the trees depth #108
- Only us `additionalItems` for tuple validation and __not__ for list validation, use `uniqueItems` for lists of enumerated items, use `const` for one-valued enums, and don't have special this-property-has-no-value values for optional properties #110
- Improve titles and descriptions of identifiers, name `uniqueId` of decentral identifiers `value`, and make identifiers be issued by databases instead of institutions #107
- Clean-up the stakeholder JSON schema, in particular, how stakeholders are referenced in specific roles #111
-
-
-
-
-
-
-
-
-
-
-
-
-
-

### Deprecated

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

### Removed

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

### Fixed

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

### Security

-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-

## [0.1.0] - 2020-08-31

First major-version-zero release
[0.1.0](https://semver.org/#how-should-i-deal-with-revisions-in-the-0yz-initial-development-phase).

Note that according to
[Semantic Versioning Specification, Item 4](https://semver.org/#spec-item-4),

> Major version zero (0.y.z) is for initial development. Anything MAY change at
> any time. The public API SHOULD NOT be considered stable.

[unreleased]: https://github.com/ise621/building-envelope-data/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ise621/building-envelope-data/releases/tag/v0.1.0
