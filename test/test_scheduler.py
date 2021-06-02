import unittest
from datetime import timedelta

import celery
from celery.schedules import crontab

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

    def test_periodictask_creation(self):
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

    def test_add_entry_to_scheduler(self):

        self.scheduler.add(**dict(
            name="test-task-interval-1",
            task="foo",
            schedule=timedelta(**{"days": 1}),
            enabled=True,
            interval=Interval(every=1, period="days")
        ))
        self.scheduler.add(**dict(
            name="test-task-interval-2",
            task="foo",
            schedule=timedelta(**{"days": 2}),
            enabled=True,
            interval=Interval(every=2, period="days")
        ))
        self.scheduler.add(**dict(
            name="test-task-crontab-1",
            task="foo",
            schedule=crontab(minute=5),
            enabled=False,
            interval=Interval(every=5, period="minute")
        ))

        self.assertEqual(len(self.scheduler.schedule), 4)
        from celerybeatredis.schedulers import RedisScheduleEntry
        for name, entry in self.scheduler.schedule.items():
            self.assertIsInstance(entry, RedisScheduleEntry)
        self.assertIn('celery.backend_cleanup', self.scheduler.schedule)
        self.assertIn('test-task-interval-1', self.scheduler.schedule)
        self.assertIn('test-task-interval-2', self.scheduler.schedule)
        self.assertIn('test-task-crontab-1', self.scheduler.schedule)

    def test_max_interval(self):
        scheduler = RedisScheduler(self.app, max_interval=600, sync_every_tasks=10)
        self.assertEqual(600, scheduler.max_interval)

    def test_should_create_redis_db_connection(self):
        scheduler = RedisScheduler(self.app, max_interval=600, sync_every_tasks=10)
        self.assertIsNotNone(scheduler.rdb)

    def test_scheduler_methods(self):
        # scheduler = RedisScheduler(self.app, max_interval=600, sync_every_tasks=10)
        scheduler = self.scheduler
        scheduler.add(**dict(
            name=b"test-task-crontab-1",
            task="foo",
            schedule=crontab(minute=5),
            enabled=False,
        ))

        # method sync
        # load names into _dirty collection
        print(scheduler.data)
        print(scheduler._dirty)
        print(scheduler._schedule)
        scheduler._dirty = {"celery.backend_cleanup", 'test-task-crontab-1'}
        scheduler.sync()
        self.assertEqual(scheduler._dirty, set())
