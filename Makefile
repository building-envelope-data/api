# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

# Taken from https://www.client9.com/self-documenting-makefiles/
help : ## Print this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
		printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
.PHONY : help
.DEFAULT_GOAL := help

dbe_referenced_schemas = \
	./schemas/calorimetric.json \
	./schemas/calorimetricData.json \
	./schemas/common.json \
	./schemas/component.json \
	./schemas/gaps.json \
	./schemas/geometry.json \
	./schemas/hygrothermal.json \
	./schemas/hygrothermalData.json \
	./schemas/identifier.json \
	./schemas/layer.json \
	./schemas/material.json \
	./schemas/method.json \
	./schemas/number.json \
	./schemas/optical.json \
	./schemas/opticalData.json \
	./schemas/photovoltaic.json \
	./schemas/photovoltaicData.json \
	./schemas/stakeholder.json \
	./schemas/string.json \
	./schemas/unit.json

dsb_referenced_schemas = \
	./schemas/building.json \
	./schemas/dbe.json \
	${dbe_referenced_schemas}

compile : compile-dbe compile-dsb ## Compile the schemas DBE and DSB
.PHONY : compile

compile-dbe : ## Compile the schema DBE
	ajv compile \
		-s ./schemas/dbe.json \
		$(addprefix -r,${dbe_referenced_schemas})
.PHONY : validate-dbe

compile-dsb : ## Compile the schema DSB
	ajv compile \
		-s ./schemas/dsb.json \
		$(addprefix -r,${dsb_referenced_schemas})
.PHONY : validate-dsb

test : test-dbe test-dsb ## Validate test files of the DBE and DSB schemas
.PHONY : test

test-dbe : DIRECTORY = ./tests/dbe/
test-dbe : SCHEMA = ./schemas/dbe.json
test-dbe : REFERENCED_SCHEMAS = ${dbe_referenced_schemas}
test-dbe : parameterized-test-or-example ## Validate test files of the DBE schemas
.PHONY : test-dbe

test-dsb : DIRECTORY = ./tests/dsb/
test-dsb : SCHEMA = ./schemas/dsb.json
test-dsb : REFERENCED_SCHEMAS = ${dsb_referenced_schemas}
test-dsb : parameterized-test-or-example ## Validate test files of the DSB schemas
.PHONY : test-dsb

example : example-dbe example-dsb ## Validate example files of the DBE and DSB schemas
.PHONY : example

example-dbe : DIRECTORY = ./examples/dbe/
example-dbe : SCHEMA = ./schemas/dbe.json
example-dbe : REFERENCED_SCHEMAS = ${dbe_referenced_schemas}
example-dbe : parameterized-test-or-example ## Validate example files of the DBE schemas
.PHONY : example-dbe

example-dsb : DIRECTORY = ./examples/dsb/
example-dsb : SCHEMA = ./schemas/dsb.json
example-dsb : REFERENCED_SCHEMAS = ${dsb_referenced_schemas}
example-dsb : parameterized-test-or-example ## Validate example files of the DSB schemas
.PHONY : example-dsb

parameterized-test-or-example :
	for test_file in $(shell find ${DIRECTORY} -name '*.json') ; do \
		ajv validate \
			-s ${SCHEMA} \
			-d $${test_file} \
			$(addprefix -r,${REFERENCED_SCHEMAS}) ; \
	done
.PHONY : parameterized-test-or-example
