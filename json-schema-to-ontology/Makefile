# Concise introduction to GNU Make:
# https://swcarpentry.github.io/make-novice/reference.html

name = json_schema_to_ontology
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

shell :
	docker run \
		--interactive \
		--tty \
		--user $(shell id --user):$(shell id --group) \
		--mount type=bind,source="$(shell pwd)",destination=/app \
		--mount type=volume,source=${name}_pip,destination=/home/me/.local \
		${name}:${tag} \
		bash
.PHONY : shell

# ------------------------------------------------ #
# Tasks to run, for example, in a Docker container #
# ------------------------------------------------ #

tests : doctests ## Run non-slow tests and doctests, for example, from a shell in a Docker container
	python -m pytest tests
.PHONY : tests

doctests: ## Run doctests
	python -m pytest \
		--doctest-modules \
		--doctest-continue-on-failure \
		--assert=plain \
		-vvv \
		*.py
.PHONY : doctests

types : ## Type check the code
	mypy --strict *.py
.PHONY : types

lint : ## Lint the code
	pylint *.py
.PHONY : lint

dead : ## Find dead code
	vulture *.py
.PHONY : dead

format: ## Format the code
	black --target-version py37 .
.PHONY : format

docs: ## Generate documentation
	sphinx-apidoc -f -o docs/source .
	sphinx-build -b html docs docs/html
.PHONY : docs
