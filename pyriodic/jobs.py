from abc import ABCMeta
from abc import abstractclassmethod
from datetime import timedelta
from pyriodic import parse
from . import now

class Job(metaclass=ABCMeta):
	def __init__(self, func, when, args, kwargs, repeating=True, name=None):
		self.func = func
		self.when = when
		self.args = args
		self.kwargs = kwargs
		self.repeating = repeating
		self.name = name
		self.last_run_time = None
		self.scheduled = False
		self.run_count = 0

	@abstractclassmethod
	def next_run_time(self):
		pass

	def __repr__(self):
		return '{}({}, \'{}\', {}, \'{}\')'.format(self.__class__.__name__, self.func.__name__, self.when, self.repeating, self.name)

class DurationJob(Job):
	def __init__(self, func, when, args=None, kwargs=None, repeating=True, name=None):
		if not isinstance(when, (str, timedelta)):
			raise TypeError('Argument \'when\' must be either a string or timedelta object, not {}'.format(type(when)))
		super().__init__(func, when, args, kwargs, repeating, name)

	def next_run_time(self):
		if isinstance(self.when, str):
			return self.last_run_time + parse.duration(self.when)
		else:
			return self.last_run_time + self.when

class DatetimeJob(Job):
	def __init__(self, func, when, args=None, kwargs=None, repeating=True, name=None):
		if not isinstance(when, str):
			raise TypeError('Argument \'when\' must be a string object, not {}'.format(type(when)))
		super().__init__(func, when, args, kwargs, repeating, name)

	def next_run_time(self):
		when = parse.datetime(self.when)
		while not self.is_in_future(when):
			when = when + timedelta(days=1)
		return when

	@staticmethod
	def is_in_future(when):
		return (when - now()).total_seconds() > 0