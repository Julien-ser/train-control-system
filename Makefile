.PHONY: help build run test clean deploy docker-build docker-run docker-test docker-push

help: ## Show this help message
	@echo 'Train Control System - Deployment Commands'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Local development commands
build: ## Build the Python package
	@echo "Building package..."
	pip install -e .

run: ## Run the basic simulation
	@echo "Running simulation..."
	python examples/basic_simulation.py

test: ## Run all tests
	@echo "Running tests..."
	pytest tests/ -v

clean: ## Clean build artifacts and cache
	@echo "Cleaning..."
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache logs/*.log
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Docker commands
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t train-control-system:latest .

docker-run: ## Run simulation in Docker
	@echo "Running simulation in Docker..."
	docker run --rm train-control-system:latest

docker-test: ## Run tests in Docker
	@echo "Running tests in Docker..."
	docker run --rm train-control-system:latest pytest tests/ -v

docker-shell: ## Get a shell in the Docker container
	@echo "Starting interactive shell..."
	docker run -it --rm train-control-system:latest /bin/bash

# Deployment commands
deploy: docker-build ## Deploy the application (build and push to registry)
	@echo "Deployment prepared. To push to registry:"
	@echo "  docker tag train-control-system:latest <registry>/train-control-system:latest"
	@echo "  docker push <registry>/train-control-system:latest"

validate: ## Validate deployment readiness
	@echo "Validating deployment..."
	@echo "  - Checking Dockerfile exists..."
	@test -f Dockerfile && echo "    ✓ Dockerfile found" || (echo "    ✗ Dockerfile missing"; exit 1)
	@echo "  - Checking requirements.txt exists..."
	@test -f requirements.txt && echo "    ✓ requirements.txt found" || (echo "    ✗ requirements.txt missing"; exit 1)
	@echo "  - Checking examples directory exists..."
	@test -d examples && echo "    ✓ examples directory found" || (echo "    ✗ examples directory missing"; exit 1)
	@echo "  - Running basic validation (import test)..."
	@python -c "import sys; sys.path.insert(0, 'src'); from train_control.train import Train; print('    ✓ Core modules importable')"
	@echo ""
	@echo "✓ All validation checks passed!"
