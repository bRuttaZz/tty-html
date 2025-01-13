CC = gcc

PYTHON = /usr/bin/python3

SCRIPT_FILES = tty_html/main.py
C_SRC_OUT = tty_html.c
EXE_OUT = tty-html.run
PYTHON_C_INCLUDES = $(shell python3-config --includes)
PYTHON_CC_FLAGS = $(shell python3-config --ldflags --embed)


transpile: ## Transpile script to c
	@$(PYTHON) -m cython $(SCRIPT_FILES) --embed -o $(C_SRC_OUT)

compile: ## Compile c script to binary
	$(CC) -Os $(C_SRC_OUT) -o $(EXE_OUT) $(PYTHON_COMPILE_FLAGS) $(PYTHON_C_INCLUDES) $(PYTHON_CC_FLAGS)

help:	## Show all Makefile targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

pip-install: ## Install using pip
	@$(PYTHON) -m pip install .

pip-build:	## Build wheels
	@$(PYTHON) -m build -o pip-build .

publish: pip-build ## Publish wheels
	@$(PYTHON) -m twine upload dist/*
