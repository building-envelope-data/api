# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Document previously undocumented database GraphQL schema [#101](https://github.com/ise621/building-envelope-data/pull/101)
- Add more tooling for GraphQL schema, queries, and mutations [#104](https://github.com/ise621/building-envelope-data/pull/104)
- Add query examples for `data`, `allData`, and `hasData` [#105](https://github.com/ise621/building-envelope-data/pull/105)
- Add section to publication to be able to refer to just one part of a publication [#155](https://github.com/ise621/building-envelope-data/pull/155)
- Add two examples of methods for daylighting and glare simulations [#179](https://github.com/ise621/building-envelope-data/pull/179)
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

- Improve propositions used in GraphQL queries to search for data [#102](https://github.com/ise621/building-envelope-data/pull/102)
- Further align database GraphQL schema and JSON schema [#103](https://github.com/ise621/building-envelope-data/pull/103)
- Flatten data HTTP resource trees to make them queryable with one query without having to know the trees depth [#108](https://github.com/ise621/building-envelope-data/pull/108)
- Only us `additionalItems` for tuple validation and **not** for list validation, use `uniqueItems` for lists of enumerated items, use `const` for one-valued enums, and don't have special this-property-has-no-value values for optional properties [#110](https://github.com/ise621/building-envelope-data/pull/110)
- Improve titles and descriptions of identifiers, name `uniqueId` of decentral identifiers `value`, and make identifiers be issued by databases instead of institutions [#107](https://github.com/ise621/building-envelope-data/pull/107)
- Clean-up the stakeholder JSON schema, in particular, how stakeholders are referenced in specific roles [#111](https://github.com/ise621/building-envelope-data/pull/111)
- Associate contact information and GnuPG keys with a person's and institution's affiliations [#112](https://github.com/ise621/building-envelope-data/pull/112)
- Check and correct usages of `oneOf`, `anyOf`, and `allOf` [#113](https://github.com/ise621/building-envelope-data/pull/113)
- Use specific instead of general and (almost) meaningless number definitions [#114](https://github.com/ise621/building-envelope-data/pull/114)
- Improve titles and descriptions in the JSON Schema for optical data [#115](https://github.com/ise621/building-envelope-data/pull/115)
- Improve documentation of approvals in the database GraphQL schema [#117](https://github.com/ise621/building-envelope-data/pull/117)
- Clean-up Dockerfile, in particular, remove notes regarding Python [#121](https://github.com/ise621/building-envelope-data/pull/121)
- Correct minor errors in database GraphQL API [#173](https://github.com/ise621/building-envelope-data/pull/173)
- Name `dataId` `uuid`, remove `validity` from `*Data` and `DataApproval`, use parent identifier instead of child identifiers to describe tree structure, do not require response approvals to be created on the fly [#180](https://github.com/ise621/building-envelope-data/pull/180)
-
-
-
- Use acronyms to identify standardizers [#154](https://github.com/ise621/building-envelope-data/pull/154)
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

- Remove intermediate representation of optical data [#152](https://github.com/ise621/building-envelope-data/pull/152)
- Remove custom directions from optical data [#153](https://github.com/ise621/building-envelope-data/pull/153)
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
