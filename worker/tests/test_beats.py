from celery.local import PromiseProxy
from django.test.testcases import SimpleTestCase
from django.utils.module_loading import import_string

from worker import celery


class BeatSchedulesTestCase(SimpleTestCase):

    def setUp(self):
        self.celery = celery

    def test_beat_schedule(self):
        beat_schedule = self.celery.conf.beat_schedule
        self.assertGreater(len(beat_schedule), 0)

        for key in beat_schedule:
            beat = beat_schedule[key]
            # try to load task
            task = import_string(beat['task'])
            # assert task is a celery task
            assert isinstance(task, PromiseProxy)
