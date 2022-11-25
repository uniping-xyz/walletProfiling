.PHONY: clean clean-test clean-pyc clean-build docs help config build build-client build-server run
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

VERSION_MAJOR := 1
VERSION_MINOR := 0
VERSION_PATCH := 0
CURRENT_DATE := `date +'%Y-%m-%d %H:%M:%S %Z'`



BACKEND_DIR := $(CURDIR)
PYTHON_PATH := $(BACKEND_DIR)

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)




prod-dist: build ## Generate distribution
	@git submodule update --recursive --remote
	@cd frontend && npm run build
	@cp -r frontend/build nginx

	@docker-compose -f docker-compose.yml build --compress --parallel 
	# @docker save nginx-image-prod | gzip > nginx-image-prod.tgz
	# @docker save sanic-server-image-prod | gzip > sanic-server-image-prod.tgz
	# @docker save mongo-image-prod | gzip > mongo-image-prod.tgz



devnet-up: build ## Generate distribution
	@docker-compose build --no-cache
	@docker-compose -f docker-compose.yml -f docker-compose.devnet.yml up --remove-orphans --force-recreate

devnet-run: build ## Generate distribution
	@docker-compose -f docker-compose.yml -f docker-compose.devnet.yml up

devnet-stop: build ## Generate distribution
	@docker-compose -f docker-compose.yml -f docker-compose.devnet.yml down


mainnet-up: build ## Generate distribution
	@docker-compose build --no-cache
	@docker-compose  -f docker-compose.yml -f docker-compose.mainnet.yml up --remove-orphans --force-recreate

mainnet-run: build ## Generate distribution
	@docker-compose  -f docker-compose.yml -f docker-compose.mainnet.yml up -d

mainnet-stop: build ## Generate distribution
	@docker-compose  -f docker-compose.yml -f docker-compose.mainnet.yml stop




dev-dist-compress: build ## Generate distribution
	@docker save mongodb-server | gzip > images/mongodb-server.tgz
	@docker save app-server | gzip > images/app-server.tgz



upload-dev-images:
	@aws s3 cp images/app-server.tgz s3://$(BUCKET_NAME)/dev/beta/compressed-images/ 
	@aws s3 cp images/mongodb-server.tgz s3://$(BUCKET_NAME)/dev/beta/compressed-images/



archive: ## Archive for distribution
	@tar cvzf $(DIST_TAR) LICENSE bin scripts templates contracts keystore nginx server.ini docker-compose.yml
	@ls -al $(DIST_TAR)

run: ## Run server
	@PYTHONPATH=$(PYTHON_PATH) python app.py

wsgi: ## Run WSGI server
	@PYTHONPATH=$(PYTHON_PATH) gunicorn -w 4 -b 0.0.0.0:5000 -k gevent wsgi:app

clean: ## Clean all build, tests and Python artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .pytest_cache

test: ## Run tests
	PYTHONPATH=$(PYTHON_PATH) pytest -s $(BACKEND_DIR)

config: ## Generate server.ini
	@PYTHONPATH=$(PYTHON_PATH) python config.py $(CURDIR)
	@echo "$(CURDIR)/server.ini generated successfully."


version: ## Generate version.py
	@printf "VERSION_MAJOR = $(VERSION_MAJOR)\nVERSION_MINOR = $(VERSION_MINOR)\nVERSION_PATCH = $(VERSION_PATCH)\n\nVERSION = $(VERSION_MAJOR).$(VERSION_MINOR).$(VERSION_PATCH)\nBUILD_TIME = '$(CURRENT_DATE)'\n" > version.py
	@echo "version.py generated successfully."
