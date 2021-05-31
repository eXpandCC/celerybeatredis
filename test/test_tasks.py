import unittest
import time
from celery import Celery
from sys import path

path.insert(0, "../")
path.insert(0, "../celerybeatredis")


class RedisSchedulerTest(unittest.TestCase):
    def setUp(self):
        from datetime import timedelta
        conf = {
            "CELERY_REDIS_SCHEDULER_URL": "redis://localhost:6379/0",
            "BROKER_URL": "redis://localhost:6379/0",
            "CELERY_IMPORTS": ["test.tasks"],
            "CELERYBEAT_SCHEDULER": "celerybeatredis.schedulers.RedisScheduler",
            "CELERY_REDIS_SCHEDULER_KEY_PREFIX": 'tasks:meta:',
            "CELERYBEAT_SCHEDULE": {
                'add-every-3-seconds': {
                    'task': 'test.tasks.add',
                    'schedule': timedelta(seconds=1),
                    'args': (16, 16)
                },
            }
        }
        self.app = Celery(**conf)
        self.app.conf.update(**conf)

        @self.app.task(bind=True, acks_late=True, ignore_result=True)
        def add(x, y):
            time.sleep(3)
            return x + y

        self.add = add

    def tearDown(self):
        pass

    def test_get_from_database(self):
        self.add.delay(5, 10)
