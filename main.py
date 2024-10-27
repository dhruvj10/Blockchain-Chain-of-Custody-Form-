import os
import importlib
import logging

def load_modules():
    modules = {}
    for filename in os.listdir('.'):
        if filename.endswith('.py') and filename != 'main.py':
            module_name = filename[:-3]
            module = importlib.import_module(module_name)
            modules[module_name] = module
    return modules

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load all Python modules in the current directory
    project_modules = load_modules()

    # Main project loop
    while True:
        command = input("Enter a command (or 'quit' to exit): ").strip().lower()
        
        if command == 'quit':
            break
        
        if command in project_modules:
            try:
                project_modules[command].run()
            except Exception as e:
                logging.error(f"Error running module {command}: {str(e)}")
        else:
            print(f"Unknown command: {command}")

    print("Project execution completed.")

if __name__ == "__main__":
    main()
