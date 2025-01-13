import logging
import logging.config
import os

def setup_logging(default_path='config/logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration

    Args:
        default_path (str, optional): Path to logging configuration file. Defaults to 'config/logging.yaml'.
        default_level (int, optional): Default logging level. Defaults to logging.INFO.
        env_key (str, optional): Environment variable key for logging configuration file path. Defaults to 'LOG_CFG'.
    """
    path = os.getenv(env_key, default_path)
    if path and os.path.exists(path):
        with open(path, 'rt') as f:
            import yaml
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
