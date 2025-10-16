.PHONY: help install test lint format clean run-example train-adapter serve

help:
	@echo "RMN LoRA System - Available Commands"
	@echo ""
	@echo "  install          Install dependencies"
	@echo "  test             Run tests"
	@echo "  lint             Run linting"
	@echo "  format           Format code"
	@echo "  clean            Clean generated files"
	@echo "  run-example      Run example workflow"
	@echo "  train-adapter    Train a LoRA adapter"
	@echo "  serve            Start multi-tenant runtime server"
	@echo ""

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/ examples/
	ruff check --fix src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

run-example:
	python examples/example_workflow.py

train-adapter:
	@echo "Training adapter..."
	@echo "Usage: make train-adapter ADAPTER_TYPE=task ADAPTER_NAME=budgeting"
	python -m src.training.train_lora \
		--base-model meta-llama/Llama-3.1-8B-Instruct \
		--dataset data/training/$(ADAPTER_NAME)_sft.jsonl \
		--adapter-type $(ADAPTER_TYPE) \
		--adapter-name $(ADAPTER_NAME) \
		--output-dir models/adapters

serve:
	python -m src.runtime.multi_tenant \
		--base-model meta-llama/Llama-3.1-8B-Instruct \
		--adapters-dir models/adapters \
		--host 0.0.0.0 \
		--port 8000

# Data harmonization
harmonize:
	python -m src.agents.data_harmonizer \
		--retailer-mapping config/mappings/$(RETAILER).yaml \
		--input data/raw/$(RETAILER)_export.parquet \
		--output data/harmonized/$(RETAILER)_rmis.parquet

# Budget optimization
optimize-budget:
	python -m src.agents.budget_optimizer \
		--method convex \
		--input $(INPUT) \
		--output $(OUTPUT)

# Create synthetic training data
create-dataset:
	python -m src.training.dataset_builder \
		--type synthetic \
		--example-type $(EXAMPLE_TYPE) \
		--num-examples $(NUM_EXAMPLES) \
		--output data/training/$(EXAMPLE_TYPE)_synthetic.jsonl

# Setup directories
setup:
	mkdir -p data/raw data/harmonized data/training
	mkdir -p models/base models/adapters
	mkdir -p logs
	mkdir -p config/mappings config/policies
	cp config/config.example.yaml config/config.yaml
	@echo "Setup complete! Edit config/config.yaml with your settings."
