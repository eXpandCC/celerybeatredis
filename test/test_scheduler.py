import unittest
from datetime import timedelta

import celery

from celerybeatredis import Interval
from celerybeatredis.schedulers import RedisScheduler
from celery import Celery


class RedisSchedulerTest(unittest.TestCase):

    def setUp(self):
        conf = {
            "CELERY_REDIS_SCHEDULER_URL": "redis://localhost:6379/0",
            "CELERYBEAT_SCHEDULER": RedisScheduler,
            "CELERY_REDIS_SCHEDULER_KEY_PREFIX": 'tasks:meta:',
        }
        self.app = Celery(**conf)
        self.app.conf.update(**conf)
        self.scheduler = RedisScheduler(app=self.app)

    def tearDown(self):
        # disconnect()
        pass

    def test_get_from_database(self):
        from celerybeatredis.task import PeriodicTask

        PeriodicTask(
            name="a1",
            task="foo",
            # schedule=self.scheduler,
            schedule=celery.schedules.schedule(timedelta(**{"days": 1})),
            enabled=True,
            interval=Interval(every=1, period="days")
        )
        PeriodicTask(
            name="b1",
            task="foo",
            # schedule=self.scheduler,
            schedule=celery.schedules.schedule(timedelta(**{"days": 2})),
            enabled=True,
            interval=Interval(every=2, period="days")
        )
        PeriodicTask(
            name="c2",
            task="foo",
            # schedule=self.scheduler,
            schedule=celery.schedules.schedule(timedelta(**{"days": 3})),
            enabled=False,
            interval=Interval(every=3, period="days")
        )

        # TODO
        # self.assertEqual(
        #     2,
        #     len(self.scheduler.all_as_schedule()),
        #     "all_as_schedule should return just enabled tasks"
        # )

    def test_max_interval(self):
        scheduler = RedisScheduler(self.app, max_interval=600, sync_every_tasks=10)
        self.assertEqual(600, scheduler.max_interval)

    def test_should_create_mongo_db_connection(self):
        scheduler = RedisScheduler(self.app, max_interval=600, sync_every_tasks=10)
        self.assertIsNotNone(scheduler.rdb)
