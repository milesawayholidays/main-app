ENV_FILE := .env
PYTHON := python3
VENV_DIR := venv
ACTIVATE := . $(VENV_DIR)/bin/activate
DATA_DIR := data
TEST_DIR := test
AIRPORTS_URL := https://davidmegginson.github.io/ourairports-data/airports.csv
DOCKERPROJECT := alertsmilesaway/main-app

.PHONY: help download-data create-logs setup_venv activate_venv install-locally local-setup run run-a install-deploy deploy-setup deploy docker-image run-docker stop-docker test-clear test test-verbose clean

# General Commands

help:
	@echo "Makefile for FlightAlertsGroup"
	@echo "Available commands:"
	@echo "  make download-data       - Download airports data"
	@echo "  make create-logs         - Create logs directory"
	@echo "  make setup_venv          - Set up Python virtual environment"
	@echo "  make install-locally     - Install local dependencies"
	@echo "  make local-setup         - Set up local environment and run main script"
	@echo "  make run                 - Run the main script with setup"
	@echo "  make run-a               - Run the main script without setup"
	@echo "  make install-deploy      - Install dependencies for deployment"
	@echo "  make deploy-setup        - Prepare for deployment"
	@echo "  make deploy              - Deploy the application"
	@echo "  make docker-image        - Build Docker image"
	@echo "  make run-docker          - Run Docker container"
	@echo "  make stop-docker         - Stop Docker container"
	@echo "  make test                - Run tests"
	@echo "  make test-all            - Run all tests with summary"
	@echo "  make test-verbose        - Run tests with verbose output"
	@echo "  make test-coverage       - Run tests with coverage analysis"
	@echo "  make clean               - Clean up generated files"

download-data:
	@echo "Creating data directory..."
	mkdir -p $(DATA_DIR)
	@echo "Downloading airports.csv from OurAirports..."
	curl -o $(DATA_DIR)/airports.csv $(AIRPORTS_URL)
	@echo "Data downloaded to $(DATA_DIR)/airports.csv"

create-logs:
	@echo "Creating logs directory..."
	mkdir -p logs
	@echo "Logs directory created."

# Local Development Commands

setup_venv:
	$(PYTHON) -m venv $(VENV_DIR)


install-locally:
	@$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt

local-setup: setup_venv download-data create-logs install-locally

run: local-setup
	$(PYTHON) src/main.py

run-a: 
	$(PYTHON) src/main.py

# Deployment Commands

install-deploy:
	@echo "Installing dependencies for deployment..."
	$(PYTHON) -m pip install --upgrade pip && $(PYTHON) -m pip install -r requirements.txt

deploy-setup: download-data create-logs install-deploy

deploy: deploy-setup
	@set -e
	@echo "Running FlightAlertsGroup..."
	$(PYTHON) src/main.py

# Docker Commands

docker-image: 
	@echo "Building Docker image for FlightAlertsGroup..."
	docker build -t $(DOCKERPROJECT):latest .
	@echo "Docker image built successfully."

run-docker: docker-image
	@echo "Running Docker container for FlightAlertsGroup..."
	docker run -d -p 4000:4000 --env-file .env --name flight_alerts_group $(DOCKERPROJECT):latest
	@echo "Docker container is running."

stop-docker:
	@echo "Stopping Docker container..."
	docker stop flight_alerts_group || true
	@echo "Docker container stopped."


# Test Commands

test-clear:
	@echo "🧹 Clearing Test Results..."
	find $(TEST_DIR) -name "output_*" -type f -delete
	@echo "✅ Test output files cleared"

test: test-clear 
	@echo "🧪 Running FlightAlertsGroup Tests..."
	$(ACTIVATE) && $(PYTHON) -m unittest discover -s test

test-verbose: test-clear
	@echo "🔍 Running Tests with Verbose Output..."
	$(ACTIVATE) && $(PYTHON) -m unittest discover -s test -v

 

# Clean Commands

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache *.pyc logs/
	rm -rf htmlcov/ .coverage
	rm -f $(DATA_DIR)/airports.csv
	rm -rf $(TEST_RESULTS_DIR)/ 