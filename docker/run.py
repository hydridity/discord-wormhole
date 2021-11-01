import os
import json


def to_env_name(key):  # Convert config key to appropriate environment variable name
    return key.upper().replace(" ", "_")


defaults = json.load(open("./config.default.json"))
config = {}

for key in defaults:
    if key == "__comment":  # Skip comment line
        continue
    key_env = to_env_name(key)  # Convert key to env variable: bot id -> BOT_ID
    if os.getenv(key_env):
        if os.getenv(key_env).isdecimal():  # token or database path is not decimal, we cannot convert using int()
            config[key] = int(os.getenv(key_env))
        else:
            config[key] = os.getenv(key_env)
    else:
        print(f"{key_env} not defined, using default '{key}': {defaults[key]}")
        config[key] = defaults[key]

with open("./config.json", "w") as config_file:
    json.dump(config, config_file)
