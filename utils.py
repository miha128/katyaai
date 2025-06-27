import yaml
import os

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_command_modules():
    modules = []
    for file in os.listdir("commands"):
        if file.endswith(".py") and not file.startswith("_"):
            modules.append(f"commands.{file[:-3]}")
    return modules