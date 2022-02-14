from logging.config import dictConfig

# Logger configuration
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s:%(name)s - - [%(asctime)s] %(message)s',
        }},
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
            'level': 'DEBUG'
            },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default',
            'level': 'DEBUG'
            }
        },
    'root': {
        'level': 'DEBUG',
        'handlers': ['stdout', 'stderr']
        }
    });
