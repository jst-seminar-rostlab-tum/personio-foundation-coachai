import os

env = os.getenv("stage", "dev")

if env == "prod":
    from .config_prod import ProdConfig as Config
else:
    from .config_dev import DevConfig as Config
