from abc import ABCMeta
from abc import abstractclassmethod
from isodate import parse_duration
# from isodate import parse_datetime
# from dateutil.parser import parser
#
# parse_datetime = parser().parse

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

class DurationJob(Job):
	def __init__(self, func, args=None, kwargs=None, date_portion=None, time_portion=None, repeating=True, name=None):
		if date_portion and time_portion:
			when = 'P{}T{}'.format(date_portion.upper(), time_portion.upper())
		elif date_portion and not time_portion:
			when = 'P{}'.format(date_portion.upper())
		elif not date_portion and time_portion:
			when = 'PT{}'.format(time_portion.upper())
		else:
			raise ValueError('There must be a date portion and/or a time portion')
		super().__init__(func, when, args, kwargs, repeating, name)
		self.date_portion = date_portion
		self.time_portion = time_portion

	def next_run_time(self):
		return self.last_run_time + parse_duration(self.when)

	def __repr__(self):
		if self.date_portion and self.time_portion:
			return 'DurationJob({}, \'{}\', \'{}\', {}, \'{}\')'.format(self.func.__name__, self.date_portion, self.time_portion, self.repeating, self.name)
		elif self.date_portion and not self.time_portion:
			return 'DurationJob({}, \'{}\', None, {}, \'{}\')'.format(self.func.__name__, self.date_portion, self.repeating, self.name)
		elif not self.date_portion and self.time_portion:
			return 'DurationJob({}, None, \'{}\', {}, \'{}\')'.format(self.func.__name__, self.time_portion, self.repeating, self.name)

# class DatetimeJob(Job):
# 	def __init__(self, func, when, repeating=True, name=None):
# 		super().__init__(func, when, repeating, name)
#
# 	def next_run_time(self):
# 		return parse_datetime(self.when) - now()