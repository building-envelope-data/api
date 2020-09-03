# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

name = building_envelopes_data
tag = latest

# Taken from https://www.client9.com/self-documenting-makefiles/
help : ## Print this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
		printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
.PHONY : help
.DEFAULT_GOAL := help

# --------------------- #
# Interface with Docker #
# --------------------- #

name : ## Print value of variable `name`
	@echo ${name}
.PHONY : name

tag : ## Print value of variable `tag`
	@echo ${tag}
.PHONY : tag

build : ## Build image with name `${name}` and tag '${tag}', for example, `make build`
	docker build \
		--tag ${name}:${tag} \
		--build-arg UID=$(shell id --user) \
		--build-arg GID=$(shell id --group) \
		.
.PHONY : build

remove : ## Remove image with name `${name}` and tag '${tag}'
	docker rmi ${name}:${tag}
.PHONY : remove

shell : build ## Enter shell in fresh container for image with name `${name}` and tag '${tag}'
	docker run \
		--interactive \
		--tty \
		--user $(shell id --user):$(shell id --group) \
		--mount type=bind,source="$(shell pwd)",destination=/app \
		--mount type=volume,source=${name}_node_modules,destination=/app/node_modules \
		${name}:${tag} \
		bash -c "make install-tools && exec bash"
.PHONY : shell

# ------------------------------------------------ #
# Tasks to run, for example, in a Docker container #
# ------------------------------------------------ #

schema_file_paths = $(shell find ./schemas/ -name "*.json")
schema_file_references = $(addprefix -r ,${schema_file_paths})

compile : ## Compile schemas
	-for schema_file_path in ./apis/*.graphql ; do \
		npx --no-install graphql-schema-linter $${schema_file_path} ; \
	done
	-for schema_file_path in ${schema_file_paths} ; do \
		npx --no-install ajv compile \
			-s $${schema_file_path} \
			${schema_file_references} ; \
	done
.PHONY : compile

test : ## Validate test files
	-echo "=============================================" && \
	echo "Testing supposed to be valid tests" && \
	echo "= = = = = = = = = = = = = = = = = = = = = = =" && \
	for schema_name in $(shell ls --indicator-style=none ./tests/valid/) ; do \
		echo "---------------------------------------------" && \
		echo "Testing schema ./schemas/$${schema_name}.json" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		for test_file_path in $$(find ./tests/valid/$${schema_name} -name "*.json") ; do \
			npx --no-install ajv validate \
				-s ./schemas/$${schema_name}.json \
				-d $${test_file_path} \
				${schema_file_references} ; \
		done ; \
	done
	-echo "=============================================" && \
	echo "Testing supposed to be INvalid tests" && \
	echo "= = = = = = = = = = = = = = = = = = = = = = =" && \
	for schema_name in $(shell ls --indicator-style=none ./tests/invalid/) ; do \
		echo "---------------------------------------------" && \
		echo "Testing schema ./schemas/$${schema_name}.json" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		for test_file_path in $$(find ./tests/invalid/$${schema_name} -name "*.json") ; do \
			! npx --no-install ajv validate \
				-s ./schemas/$${schema_name}.json \
				-d $${test_file_path} \
				${schema_file_references} ; \
		done ; \
	done
.PHONY : test

# If `ajv-cli` supported fragments to refer to definitions inside schema files,
# then we could use the following to test definitions in isolation:
# test : ## Validate test files
# 	echo "=============================================" && \
# 	echo "Testing supposed to be valid tests" && \
# 	echo "= = = = = = = = = = = = = = = = = = = = = = =" && \
# 	for truncated_test_directory_path in $(shell find ./tests/valid -mindepth 1 -type d -printf '%P ') ; do \
# 		schema_file_path_with_fragment=./schemas/$$(echo $${truncated_test_directory_path} | sed -e 's_\([^/]\+\)_$$defs/\1_g' -e 's_$$defs/\([^/]\+\)\/_\1.json#/_') && \
# 		echo "---------------------------------------------" && \
# 		echo "Testing schema ./schemas/$${schema_name}.json" && \
# 		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
# 		for test_file_path in $$(find ./tests/valid/$${truncated_test_directory_path} -name "*.json") ; do \
# 			ajv validate \
# 				-s $${schema_file_path_with_fragment} \
# 				-d $${test_file_path} \
# 				${schema_file_references} ; \
# 		done ; \
# 	done && \
# 	echo "=============================================" && \
# 	echo "Testing supposed to be INvalid tests" && \
# 	echo "= = = = = = = = = = = = = = = = = = = = = = =" && \
# 	for truncated_test_directory_path in $(shell find ./tests/valid -mindepth 1 -type d -printf '%P ') ; do \
# 		schema_file_path_with_fragment=./schemas/$$(echo $${truncated_test_directory_path} | sed -e 's_\([^/]\+\)_$$defs/\1_g' -e 's_$$defs/\([^/]\+\)\/_\1.json#/_') && \
# 		echo "---------------------------------------------" && \
# 		echo "Testing schema ./schemas/$${schema_name}.json" && \
# 		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
# 		for test_file_path in $$(find ./tests/invalid/$${truncated_test_directory_path} -name "*.json") ; do \
# 			! ajv validate \
# 				-s $${schema_file_path_with_fragment} \
# 				-d $${test_file_path} \
# 				${schema_file_references} ; \
# 		done ; \
# 	done
# .PHONY : test

example : ## Validate example files
	-for schema_name in $(shell ls --indicator-style=none ./queries/) ; do \
		echo "---------------------------------------------" && \
		echo "Queries against schema ./apis/$${schema_name}.graphql" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		npx --no-install eslint \
			 --ext graphql \
			./queries/$${schema_name}/**.graphql ; \
	done
	-for schema_name in $(shell ls --indicator-style=none ./examples/) ; do \
		echo "---------------------------------------------" && \
		echo "Examples for schema ./schemas/$${schema_name}.json" && \
		echo "- - - - - - - - - - - - - - - - - - - - - - -" && \
		for example_file in $$(find ./examples/$${schema_name} -name "*.json") ; do \
			npx --no-install ajv validate \
				-s ./schemas/$${schema_name}.json \
				-d $${example_file} \
				${schema_file_references} ; \
		done ; \
	done
.PHONY : example

format : ## Format files with [Prettier](https://prettier.io)
	npx --no-install prettier --write .
.PHONY : format

dos2unix : ## Strip the byte-order mark, also known as, BOM, and remove carriage returns
	find \
		. \
		\( -name "*.json" \) \
		-type f \
		-exec sed -i -e "$(shell printf '1s/^\357\273\277//')" -e "s/\r//" {} +
.PHONY : dos2unix

install-tools : ## Install development tools if necessary
	if [ \
			"$$(npm install --no-optional --dry-run --json | jq "(.added + .removed + .updated + .moved + .failed) | length")" \
			-ne 0 \
		 ]; then \
		npm ci --no-optional ; \
	fi
.PHONY : install-tools

update-tools : ## Update development tools to the latest compatible minor versions
	npm install --no-optional
.PHONY : update-tools
