# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

### Changed

- Upgrade development packages to latest versions [#285](https://github.com/building-envelope-data/api/pull/285)
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

## [v1.0.0] - 2022-03-02

### Added

- Document previously undocumented database GraphQL schema [#101](https://github.com/building-envelope-data/api/pull/101)
- Add more tooling for GraphQL schema, queries, and mutations [#104](https://github.com/building-envelope-data/api/pull/104)
- Add query examples for `data`, `allData`, and `hasData` [#105](https://github.com/building-envelope-data/api/pull/105)
- Add section to publication to be able to refer to just one part of a publication [#155](https://github.com/building-envelope-data/api/pull/155)
- Add two examples of methods for daylighting and glare simulations [#179](https://github.com/building-envelope-data/api/pull/179)
- Add version to JSON Schema `$id`s [#188](https://github.com/building-envelope-data/api/pull/188)
- Add examples photovoltaicWithOptical [#207](https://github.com/building-envelope-data/api/pull/207), semitransparentBuildingIntegratedPhotovoltaicThermal [#209](https://github.com/building-envelope-data/api/pull/209), from ES-SDA [#213](https://github.com/building-envelope-data/api/pull/213) and dataFormatPdf [#226](https://github.com/building-envelope-data/api/pull/226)
- Add the key `roughness` [#205](https://github.com/building-envelope-data/api/pull/205)
- Add the position of coatings to components [#223](https://github.com/building-envelope-data/api/pull/223)
- Add `currentVoltage` characteristics for modules [#224](https://github.com/building-envelope-data/api/pull/224)
- Add release actions [#281](https://github.com/building-envelope-data/api/pull/281)

### Changed

- Improve propositions used in GraphQL queries to search for data [#102](https://github.com/building-envelope-data/api/pull/102)
- Further align database GraphQL schema and JSON schema [#103](https://github.com/building-envelope-data/api/pull/103)
- Flatten data HTTP resource trees to make them queryable with one query without having to know the trees depth [#108](https://github.com/building-envelope-data/api/pull/108)
- Only use `additionalItems` for tuple validation and **not** for list validation, use `uniqueItems` for lists of enumerated items, use `const` for one-valued enums, and don't have special this-property-has-no-value values for optional properties [#110](https://github.com/building-envelope-data/api/pull/110)
- Improve titles and descriptions of identifiers, name `uniqueId` of decentral identifiers `value`, and make identifiers be issued by databases instead of institutions [#107](https://github.com/building-envelope-data/api/pull/107)
- Clean-up the stakeholder JSON schema, in particular, how stakeholders are referenced in specific roles [#111](https://github.com/building-envelope-data/api/pull/111)
- Associate contact information and GnuPG keys with a person's and institution's affiliations [#112](https://github.com/building-envelope-data/api/pull/112)
- Check and correct usages of `oneOf`, `anyOf`, and `allOf` [#113](https://github.com/building-envelope-data/api/pull/113)
- Use specific instead of general and (almost) meaningless number definitions [#114](https://github.com/building-envelope-data/api/pull/114)
- Improve titles and descriptions in the JSON Schema for optical data [#115](https://github.com/building-envelope-data/api/pull/115)
- Improve documentation of approvals in the database GraphQL schema [#117](https://github.com/building-envelope-data/api/pull/117)
- Clean-up Dockerfile, in particular, remove notes regarding Python [#121](https://github.com/building-envelope-data/api/pull/121)
- Correct minor errors in database GraphQL API [#173](https://github.com/building-envelope-data/api/pull/173)
- Name `dataId` `uuid`, remove `validity` from `*Data` and `DataApproval`, use parent identifier instead of child identifiers to describe tree structure, do not require response approvals to be created on the fly [#180](https://github.com/building-envelope-data/api/pull/180)
- Update GraphqL schema of metabase to match the current deployed version [#280](https://github.com/building-envelope-data/api/pull/280)
- Rename organization to `building-envelope-data` and API repository to `api` [#277](https://github.com/building-envelope-data/api/pull/277)
- Use acronyms to identify standardizers [#154](https://github.com/building-envelope-data/api/pull/154)
- Use JSON Schema Draft 2019-09 and upgrade tooling [#181](https://github.com/building-envelope-data/api/pull/181)
- Restructure `numbersWithUncertainty` to make the data less verbose[#195](https://github.com/building-envelope-data/api/pull/195),[#216](https://github.com/building-envelope-data/api/pull/216)
- Improve the structure of geometry.json [#205](https://github.com/building-envelope-data/api/pull/205)
- Improve the structure of calorimetricData.json [#209](https://github.com/building-envelope-data/api/pull/209)]
- Correct the requirements of `emergenceDirection`[#213](https://github.com/building-envelope-data/api/pull/213)
- Offer detailed definition of calorimetric fluxes [#222](https://github.com/building-envelope-data/api/pull/222)
- Add categories to `material`, `layer` and `unit` from EN 12216 [#223](https://github.com/building-envelope-data/api/pull/223) and from EN 13024-1, EN 14179, EN 1863, DIN 18008-5 [#224](https://github.com/building-envelope-data/api/pull/224)
- Add more mirrored values to `apis` [#238](https://github.com/building-envelope-data/api/pull/238)
- Add spectrum `ultraviolet` for integral values and improve the optical examples [#247](https://github.com/building-envelope-data/api/pull/247)
- Change propositions for lists and make parameter `where` optional [#260](https://github.com/building-envelope-data/api/pull/260)

### Removed

- Remove intermediate representation of optical data [#152](https://github.com/building-envelope-data/api/pull/152)
- Remove custom directions from optical data [#153](https://github.com/building-envelope-data/api/pull/153)
- Remove `validity` everywhere except of `method` which can depend for example on a standard [#219](https://github.com/building-envelope-data/api/pull/219)

### Fixed

- Fix the three phase method test by using enumerated standardizers instead of identifiers [#192](https://github.com/building-envelope-data/api/pull/192)

## [v0.1.0] - 2020-08-31

First major-version-zero release
[0.1.0](https://semver.org/#how-should-i-deal-with-revisions-in-the-0yz-initial-development-phase).

Note that according to
[Semantic Versioning Specification, Item 4](https://semver.org/#spec-item-4),

> Major version zero (0.y.z) is for initial development. Anything MAY change at
> any time. The public API SHOULD NOT be considered stable.

[unreleased]: https://github.com/building-envelope-data/api/compare/v1.0.0...HEAD
[v1.0.0]: https://github.com/building-envelope-data/api/compare/v0.1.0...v1.0.0
[v0.1.0]: https://github.com/building-envelope-data/api/releases/tag/v0.1.0
