# Executable name
EXEC = bchoc

# Python interpreter
PYTHON = python3

# Main script
MAIN = main.py

# Default target
.PHONY: all
all: $(EXEC)

# Create the executable
$(EXEC): $(MAIN)
	cp $(MAIN) $(EXEC)
	chmod +x $(EXEC)
	dos2unix $(EXEC) || true

# Clean up
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f $(EXEC)

# Help target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make        : Create the executable"
	@echo "  make clean  : Remove Python cache files and executable"
	@echo "  make help   : Show this help message"