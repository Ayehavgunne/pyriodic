from calendar import isleap
from abc import ABCMeta
from abc import abstractclassmethod
from datetime import timedelta
from pyriodic import parse
from . import now

intvl = {
	'weekly': ('monday', 'mon', 'mo', 'm', 'tuesday', 'tue', 'tu', 'wednesday', 'wed', 'we', 'w', 'thursday', 'thu', 'th', 'friday', 'fri', 'fr', 'saturday', 'sat', 'sa', 'sunday', 'sun', 'su'),
	'yearly': ('january', 'jan', 'ja', 'february', 'feb', 'fe', 'march', 'mar', 'april', 'apr', 'ap' 'may', 'june', 'jun', 'july', 'jul', 'august', 'aug', 'au', 'september', 'sep', 'se', 'october', 'oct', 'oc', 'november', 'nov', 'no', 'december', 'dec', 'de')
}

days_in_month = {'ja': 31, 'fe': 28, 'mar': 31, 'ap': 30, 'may': 31, 'jun': 30, 'jul': 31, 'au': 31, 'se': 30, 'oc': 31, 'no': 30, 'de': 31}
days_in_year = 365
days_in_week = 7

class Job(metaclass=ABCMeta):
	def __init__(self, func, when, args, kwargs, name=None, repeating=True, threaded=True):
		self.func = func
		self.when = when
		self.args = args
		self.kwargs = kwargs
		self.repeating = repeating
		self.name = name
		self.run_time_history = []
		self.scheduled = False
		self.status = 'waiting'
		self.threaded = threaded
		self.thread = None

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

	def __repr__(self):
		return '{}({}, \'{}\', name=\'{}\')'.format(self.__class__.__name__, self.func.__name__, self.when, self.name)

class DurationJob(Job):
	def __init__(self, func, when, args=None, kwargs=None, repeating=True, name=None, threaded=True):
		if not isinstance(when, (str, timedelta)):
			raise TypeError('Argument \'when\' must be either a string or timedelta object, not {}'.format(type(when)))
		super().__init__(func, when, args, kwargs, name, repeating, threaded)

	def next_run_time(self):
		if self.last_run_time:
			if isinstance(self.when, str):
				return self.last_run_time + parse.duration(self.when)
			else:
				return self.last_run_time + self.when
		else:
			if isinstance(self.when, str):
				return now() + parse.duration(self.when)
			else:
				return now() + self.when

class DatetimeJob(Job):
	def __init__(self, func, when, args=None, kwargs=None, repeating=True, name=None, threaded=True, custom_format=None, interval=None):
		if not isinstance(when, str):
			raise TypeError('Argument \'when\' must be a string object, not {}'.format(type(when)))
		if interval is None:
			for key, val in intvl.items():
				for itm in val:
					if itm in when:
						self.interval = key
						break
		super().__init__(func, when, args, kwargs, name, repeating, threaded)
		self.custom_format = custom_format

	def next_run_time(self):
		when = parse.datetime(self.when, self.custom_format)
		while not self.is_in_future(when):
			if self.interval == 'weekly':
				when = when + timedelta(days=days_in_week)
			elif self.interval == 'monthly':
				when = when + timedelta(days=31)
			elif self.interval == 'yearly':
				if isleap(now().year):
					when = when + timedelta(days=days_in_year + 1)
				else:
					when = when + timedelta(days=days_in_year)
		return when

	@staticmethod
	def is_in_future(when):
		return (when - now()).total_seconds() > 0