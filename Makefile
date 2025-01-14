CC = gcc

ARCH = $(shell uname)_$(shell uname -m)

PYTHON = python3
SCRIPT_FILE = tty_html/main.py
VERSION = $(shell $(PYTHON) $(SCRIPT_FILE) -V)

C_SRC_OUT = tty_html.c
EXE_OUT = tty-html_v$(VERSION)_$(ARCH)
PYTHON_C_INCLUDES = $(shell python3-config --includes)
PYTHON_CC_FLAGS = $(shell python3-config --ldflags --embed)


transpile: ## Transpile script to c
	@$(PYTHON) -m cython $(SCRIPT_FILE) --embed -o $(C_SRC_OUT)

compile: ## Compile c script to binary
	$(CC) -Os $(PYTHON_C_INCLUDES) $(C_SRC_OUT) $(PYTHON_CC_FLAGS) -o "$(EXE_OUT)"

help:	## Show all Makefile targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

exec-file:
	@echo -n $(EXE_OUT)

pip-install: ## Install using pip
	@$(PYTHON) -m pip install .

pip-build:	## Build wheels
	@$(PYTHON) -m build -o pip-build .

publish: pip-build ## Publish wheels
	@$(PYTHON) -m twine upload pip-build/*

setup-pip-build-env: ## Install
	@$(PYTHON) -m pip install --upgrade build twine setuptools
