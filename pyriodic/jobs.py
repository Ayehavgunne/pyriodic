from calendar import isleap
from collections import OrderedDict
from abc import ABCMeta
from abc import abstractclassmethod
from collections import deque
from datetime import datetime
from datetime import timedelta
from pyriodic import parse
from . import now


intvl = OrderedDict()
intvl['yearly'] = (
	'january', 'jan', 'ja', 'february', 'feb', 'fe', 'march', 'mar', 'april', 'apr', 'ap' 'may', 'june', 'jun', 'july',
	'jul', 'august', 'aug', 'au', 'september', 'sep', 'se', 'october', 'oct', 'oc', 'november', 'nov', 'no',
	'december', 'dec', 'de'
)
intvl['monthly'] = ('st', 'th', 'rd', 'nd')
intvl['weekly'] = (
	'monday', 'mon', 'mo', 'tuesday', 'tue', 'tu', 'wednesday', 'wed', 'we', 'thursday', 'thu', 'th', 'friday', 'fri',
	'fr', 'saturday', 'sat', 'sa', 'sunday', 'sun', 'su'
)

days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
days_in_year = 365
days_in_week = 7


class Job(metaclass=ABCMeta):
	def __init__(self, func, when, args=None, kwargs=None, name=None, repeating=True,
			threaded=True, ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None):
		self.func = func
		self.when = when
		self.args = args
		self.kwargs = kwargs
		self.repeating = repeating
		self.name = name
		self.run_time_history = []
		self.status = 'waiting'
		self.threaded = threaded
		self.thread = None
		self.ignore_exceptions = ignore_exceptions
		self.parent = None
		self.exceptions = []
		self.retrys = retrys
		self.retry_time = retry_time
		self.alt_func = alt_func

	@property
	@abstractclassmethod
	def next_run_time(self):
		pass

	@property
	def first_run_time(self):
		if self.run_time_history:
			return self.run_time_history[0]

	@property
	def last_run_time(self):
		if self.run_time_history:
			return self.run_time_history[-1]

	def add_run_time(self, dt):
		self.run_time_history.append(dt.replace(microsecond=0))

	@property
	def run_count(self):
		return len(self.run_time_history)

	def start(self):
		self.status = 'waiting'
		if self.parent:
			self.parent.reset()

	def is_waiting(self):
		return self.status == 'waiting'

	def wait(self):
		self.status = 'waiting'

	def pause(self):
		self.status = 'paused'
		if self.parent:
			self.parent.reset()

	def is_paused(self):
		return self.status == 'paused'

	def run(self):
		self.status = 'running'

	def is_running(self):
		return self.status == 'running'

	@staticmethod
	def is_in_future(when):
		return (when - now()).total_seconds() > 0

	def __repr__(self):
		return '{}({}, \'{}\', name=\'{}\')'.format(self.__class__.__name__, self.func.__name__, self.when, self.name)


class DurationJob(Job):
	# noinspection PyUnusedLocal
	def __init__(self, func, when, *argums, start_time=None, args=None, kwargs=None, name=None, repeating=True,
			threaded=True, ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None, **keyargs):
		if not isinstance(when, (str, timedelta)):
			raise TypeError('Argument \'when\' must be either a string or timedelta object, not {}'.format(type(when)))
		super().__init__(func, when, args, kwargs, name, repeating,
			threaded, ignore_exceptions, retrys, retry_time, alt_func)
		if isinstance(start_time, str):
			self.start_time = parse.datetime_string(start_time)
		elif not isinstance(start_time, datetime) or start_time is None:
			self.start_time = start_time
		else:
			raise TypeError('Argument \'start\' must be a datetime object, not {}'.format(type(when)))
		self.time_initialized = now()

	@property
	def next_run_time(self):
		if self.is_paused():
			return
		else:
			if not self.first_run_time:
				if self.start_time:
					if self.is_in_future(self.start_time):
						return self.start_time
				if isinstance(self.when, str):
					return self.time_initialized + parse.duration_string(self.when)
				else:
					return self.time_initialized + self.when
			else:
				if isinstance(self.when, str):
					return self.last_run_time + parse.duration_string(self.when)
				else:
					return self.last_run_time + self.when


class DatetimeJob(Job):
	# noinspection PyUnusedLocal
	def __init__(self, func, when, *argums, interval=None, args=None, kwargs=None,
			name=None, repeating=True, threaded=True, ignore_exceptions=False,
			retrys=0, retry_time=0, alt_func=None, custom_format=None, **keyargs):
		if not isinstance(when, str):
			raise TypeError('Argument \'when\' must be a string, not {}'.format(type(when)))
		super().__init__(func, when, args, kwargs, name, repeating,
			threaded, ignore_exceptions, retrys, retry_time, alt_func)
		self.custom_format = custom_format
		if interval is None:
			for key, val in intvl.items():
				for itm in val:
					if itm in when.lower():
						self.interval = key
						return
			self.interval = 'daily'
		else:
			self.interval = interval

	@property
	def next_run_time(self):
		if self.is_paused():
			return
		else:
			return self.increment(parse.datetime_string(self.when, self.custom_format))

	def increment(self, when):
		while not self.is_in_future(when):
			if self.interval == 'daily':
				when = when + timedelta(days=1)
			elif self.interval == 'weekly':
				when = when + timedelta(days=days_in_week)
			elif self.interval == 'monthly':
				if now().month == 2 and isleap(now().year):
					when = when + timedelta(days=days_in_month[2] + 1)
				else:
					when = when + timedelta(days=days_in_month[now().month])
			elif self.interval == 'yearly':
				if isleap(now().year) and self.is_in_future(datetime(year=now().year, month=2, day=29)):
					when = when + timedelta(days=days_in_year + 1)
				else:
					when = when + timedelta(days=days_in_year)
		return when


class DatetimesJob(DatetimeJob):
	# noinspection PyUnusedLocal
	def __init__(self, func, when, interval, *argums, args=None, kwargs=None, repeating=True, name=None, threaded=True,
			ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None, custom_format=None, **keyargs):
		super().__init__(func, when, interval, args, kwargs, name, repeating,
			threaded, ignore_exceptions, retrys, retry_time, alt_func, custom_format)
		self.queue = deque([parse.datetime_string(dt.rstrip(' ').lstrip(' '), custom_format) for dt in when.split(',')])

	@property
	def next_run_time(self):
		if self.is_paused():
			return
		else:
			x = len(self.queue)
			while x > 0 and not self.is_in_future(self.queue[0]):
				x -= 1
				self.queue.rotate()
			if self.last_run_time == self.queue[0]:
				self.queue.rotate()
			next_runtime = self.increment(self.queue[0])
			self.queue[0] = next_runtime
			return next_runtime
