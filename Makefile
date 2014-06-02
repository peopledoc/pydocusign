.PHONY: all help translate test clean update compass collect rebuild

all:
	@echo "Hello $(LOGNAME), nothing to do by default"
	@echo "Try 'make help'"


#: help - Display callable targets.
help:
	@egrep "^#: " [Mm]akefile


#: develop - Develop the Python project
develop:
	python setup.py develop


#: install - Install current project
install:
	python setup.py install


#: release - release the project on pypi
release:
	pip install zest.releaser
	fullrelease