from unittest import TestCase
from pyriodic import Scheduler
from pyriodic import DurationJob
from pyriodic import DatetimeJob


def test_func_one():
	print('Test Func 1')


def test_func_two():
	print('Test Func 2')


class TestScheduler(TestCase):
	def setUp(self):
		super().setUp()
		self.scheduler = Scheduler()
		self.job1 = self.scheduler.add_job(DurationJob(test_func_one, '2m', name='job1'))
		self.job2 = self.scheduler.add_job(DatetimeJob(test_func_two, '12:00 pm', name='job2'))

	def tearDown(self):
		super().tearDown()
		self.scheduler.stop_scheduler()
		self.scheduler.remove(self.job1)
		self.scheduler.remove(self.job2)
		self.scheduler = None

	def test_set_timer(self):
		self.fail()

	def test_execute_job(self):
		self.fail()

	def test_sort_jobs(self):
		self.fail()

	def test_add_job(self):
		self.fail()

	def test_schedule_job(self):
		self.fail()

	def test_trim_jobs(self):
		self.fail()

	def test_get_job(self):
		self.fail()

	def test_reset(self):
		self.fail()

	def test_remove(self):
		self.fail()

	def test_pop(self):
		self.fail()

	def test_job_names(self):
		self.fail()

	def test_find_job_index(self):
		self.fail()

	def test_next_run_times(self):
		self.fail()

	def test_start_all(self):
		self.fail()

	def test_stop_scheduler(self):
		self.fail()

	def test_pause_all(self):
		self.fail()

	def test_start_web_server(self):
		self.fail()


class TestJobFuncWrapper(TestCase):
	def test_job_func_wrapper(self):
		self.fail()
