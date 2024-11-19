<<<<<<< HEAD
 # Python interpreter
=======
# Python interpreter
>>>>>>> Temp
PYTHON = python3

# Main script
MAIN = main.py

# Default target
.PHONY: all
all: run

# Run the project
.PHONY: run
run:
	$(PYTHON) $(MAIN)

# Clean up Python cache files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f blockchain.bin

# Install required dependencies
.PHONY: install
install:
	$(PYTHON) -m pip install pycryptodome

# Help target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make        : Run the project"
	@echo "  make clean  : Remove Python cache files and blockchain data"
	@echo "  make install: Install required dependencies"
	@echo "  make help   : Show this help message"