# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

name = building_envelopes_data
tag = latest

DATABASE_PORT = 4000
METABASE_PORT = 4001

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

run : build ## Run command `${COMMAND}` in fresh container for image with name `${name}` and tag '${tag}', for example, `make COMMAND="ls -al" run (note that Node development tools are installed to or updated in the Docker volume `${name}_node_modules` when necessary --- stop and remove containers using the volume and remove the volume by running `make remove-containers remove-volumes`)`
	docker run \
		--interactive \
		--tty \
		--user $(shell id --user):$(shell id --group) \
		--mount type=bind,source="$(shell pwd)",destination=/app \
		--mount type=volume,source=${name}_node_modules,destination=/app/node_modules \
		${OPTIONS} \
		${name}:${tag} \
		bash -c "make install-tools && (exec ${COMMAND})"
.PHONY : run

shell : COMMAND = bash
shell : run ## Enter `bash` shell in fresh container for image with name `${name}` and tag '${tag}'
.PHONY : shell

remove-containers : containers = $(shell docker ps --all --quiet --filter ancestor=building_envelopes_data)
remove-containers : ## Stop and remove containers for image with name `${name}`
	if [ "$(strip ${containers})" = '' ] ; then \
		echo 'There are no containers for image with name `${name}`' ; \
	else \
		echo 'About to stop and remove containers with identifier(s) `${containers}`' && \
		docker container stop ${containers} && \
		docker container rm ${containers} ; \
	fi
.PHONY : remove-containers

remove-volumes : ## Remove volumes created on the fly and used by running `make run` and `make shell` (note that all containers using the volume must be removed first, for example by running `make remove-containers`)
	docker volume rm ${name}_node_modules
.PHONY : remove-volumes

serve : COMMAND = \
					npx --no-install graphql-inspector serve ./apis/database.graphql --port 4000 & \
					npx --no-install graphql-inspector serve ./apis/metabase.graphql --port 4001 & \
					bash
serve : OPTIONS = \
					--publish ${DATABASE_PORT}:4000 \
					--publish ${METABASE_PORT}:4001
serve : run ## Serve GraphQL schemas with fake data on ports `${DATABASE_PORT}` and `${METABASE_PORT}` with defaults 4000 and 4001, for example, `make serve` or `make DATABASE_PORT=8000 METABASE_PORT=8001 serve` (afterwards, open the GraphiQL IDE, a graphical interactive in-browser GraphQL IDE, in your web browser on localhost with the respective port)
.PHONY : serve

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
# test :
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
		for query_file in $$(find ./queries/$${schema_name} -name "*.graphql") ; do \
			echo "$${query_file}" && \
			npx --no-install graphql-inspector validate \
				$${query_file} \
				./apis/$${schema_name}.graphql ; \
		done ; \
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

format : ## Format files with Prettier
	npx --no-install prettier --write .
.PHONY : format

introspect : ## Introspect GraphQL schemas writing results to ./apis/*.graphql.schema.json
	for schema_file in ./apis/*.graphql ; do \
		npx --no-install graphql-inspector introspect \
			$${schema_file} \
			--write $${schema_file}.schema.json ; \
	done
.PHONY : introspect

dos2unix : ## Strip the byte-order mark, also known as, BOM, and remove carriage returns
	find \
		. \
		\( -name "*.json" -o -name "*.graphql" \) \
		-type f \
		-exec sed -i -e "$(shell printf '1s/^\357\273\277//')" -e "s/\r//" {} +
.PHONY : dos2unix

# For the dry run in the condition we should use `npm ci` However, that command
# does not support dry runs.
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
