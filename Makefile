# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

# Taken from https://www.client9.com/self-documenting-makefiles/
help : ## Print this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
		printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
.PHONY : help
.DEFAULT_GOAL := help

schema_file_paths = $(shell find ./schemas/ -name "*.json")
schema_file_references = $(addprefix -r ,${schema_file_paths})

compile : ## Compile schemas
	for schema_file_path in ${schema_file_paths} ; do \
		ajv compile \
			-s $${schema_file_path} \
			${schema_file_references} ; \
	done
.PHONY : compile

test : ## Validate test files
	echo "=============================================" && \
	echo "Testing supposed to be valid tests" && \
	echo "= = = = = = = = = = = = = = = = = = = = = = =" && \
	for schema_name in $(shell ls --indicator-style=none ./tests/valid/) ; do \
		echo "---------------------------------------------" && \
		echo "Testing schema ./schemas/$${schema_name}.json" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		for test_file_path in $$(find ./tests/valid/$${schema_name} -name "*.json") ; do \
			ajv validate \
				-s ./schemas/$${schema_name}.json \
				-d $${test_file_path} \
				${schema_file_references} ; \
		done ; \
	done && \
	echo "=============================================" && \
	echo "Testing supposed to be INvalid tests" && \
	echo "= = = = = = = = = = = = = = = = = = = = = = =" && \
	for schema_name in $(shell ls --indicator-style=none ./tests/invalid/) ; do \
		echo "---------------------------------------------" && \
		echo "Testing schema ./schemas/$${schema_name}.json" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		for test_file_path in $$(find ./tests/invalid/$${schema_name} -name "*.json") ; do \
			ajv validate \
				-s ./schemas/$${schema_name}.json \
				-d $${test_file_path} \
				${schema_file_references} ; \
		done ; \
	done
.PHONY : test

example : ## Validate example files
	for schema_name in $(shell ls --indicator-style=none ./examples/) ; do \
		echo "---------------------------------------------" && \
		echo "Validating schema ./schemas/$${schema_name}.json" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		for example_file in $$(find ./examples/$${schema_name} -name "*.json") ; do \
			ajv validate \
				-s ./schemas/$${schema_name}.json \
				-d $${example_file} \
				${schema_file_references} ; \
		done ; \
	done
.PHONY : example

dos2unix : ## Strip the byte-order mark, also known as, BOM, and remove carriage returns
	find \
		. \
		\( -name "*.json" \) \
		-type f \
		-exec sed -i -e "$(shell printf '1s/^\357\273\277//')" -e "s/\r//" {} +
.PHONY : dos2unix
