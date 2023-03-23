.PHONY: model

# check for git submodules
ifneq ($(findstring -, $(shell git submodule status)),)
$(info INFO: Initializing submodules)
$(shell git submodule update --init)
endif
ifneq ($(findstring +, $(shell git submodule status)),)
$(info INFO: New updates in submodules, reinitializing...)
$(shell git submodule update --init)
endif

setup:
	poetry install
	poetry run pip install tensorflow==2.11.0 --force-reinstall
	mkdir temp_model

# If the first argument is "run"
ifeq (run,$(firstword $(MAKECMDGOALS)))
  MODE := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(MODE):;@:)
endif
run:
	poetry run python -B ./GUI.py $(MODE)

train1:
	git pull origin main
	poetry run python -B ./train_bp_minimax.py

train2:
	git pull origin main
	poetry run python -B ./train_ga_minimax.py

train3:
	git pull origin main
	poetry run python -B ./train_ga_self.py

save:
	poetry run python -B ./save.py