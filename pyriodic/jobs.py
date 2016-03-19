from calendar import isleap
from calendar import monthrange
from time import sleep
from collections import OrderedDict
from collections import deque
from abc import ABCMeta
from abc import abstractclassmethod
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


class Job(metaclass=ABCMeta):
	"""
	The Abstract Base Class for all Job Types.
	"""
	def __init__(self, func, when, name=None, repeating=True, threaded=True,
			ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None):
		self.func = func
		self.when = when
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
		"""
		Returns the first time a job instance was run
		"""
		if self.run_time_history:
			return self.run_time_history[0]

	@property
	def last_run_time(self):
		"""
		Returns the most recent time a job instance was run
		"""
		if self.run_time_history:
			return self.run_time_history[-1]

	def _add_run_time(self, dt):
		"""
		Adds a run time to the history of the job instance and clears the microseconds
		from the datetime object to prevent drift from the slight lag between run times
		"""
		self.run_time_history.append(dt.replace(microsecond=0))

	@property
	def run_count(self):
		"""
		Returns the number of times the job instance has been run based on the run time history
		"""
		return len(self.run_time_history)

	def start(self):
		"""
		Sets a job instance status to 'waiting' and resets the parent object to properly sort it's jobs
		"""
		self.status = 'waiting'
		if self.parent:
			self.parent.reset()

	def is_waiting(self):
		"""
		A test of the job instance to see if it is currently in the waiting status
		"""
		return self.status == 'waiting'

	def wait(self):
		"""
		Sets a job instance status to 'waiting'
		"""
		self.status = 'waiting'

	def pause(self):
		"""
		Sets a job instance status to 'paused' and resets the parent object to properly sort it's jobs
		"""
		self.status = 'paused'
		if self.parent:
			self.parent.reset()

	def is_paused(self):
		"""
		A test of the job instance to see if it is currently in the paused status
		"""
		return self.status == 'paused'

	def run(self, retrys=0, alt=False):
		"""
		Sets a job instance status to 'running' and executes the function associated with the job
		"""
		self.status = 'running'
		self._add_run_time(now())
		self.parent.log.info('Job "{}" was started. Run count = {}'.format(self.name, self.run_count))
		try:
			if alt:
				self.alt_func()
			else:
				self.func()
		except Exception as e:
			self.exceptions.append((e, self.run_count))
			self.parent.log.info('Job "{}" enountered an exception ({}). Run count = {}'.format(self.name, e, self.run_count))
			if retrys:
				if self.retry_time:
					self.pause()
					sleep(self.retry_time)
				if self.alt_func:
					self.run(retrys - 1, True)
				else:
					self.run(retrys - 1)
				self.parent.reset()
				return
			if not self.ignore_exceptions:
				self.pause()
				raise

	def is_running(self):
		"""
		A test of the job instance to see if it is currently in the running status
		"""
		return self.status == 'running'

	@staticmethod
	def is_in_future(when):
		"""
		A test of a datetime object to see if it is in the past or the future compared to the present
		"""
		return (when - now()).total_seconds() > 0

	def __repr__(self):
		return '{}({}, \'{}\', name=\'{}\')'.format(self.__class__.__name__, self.func.__name__, self.when, self.name)


class DurationJob(Job):
	"""
	A Job Type that sets up execution based on an interval of time.
	For example it could execute every 10 minutes, 3 hours or 7 days.
	Works best for tasks that need to be run on a regular basis but
	not at a specific time.
	"""
	# noinspection PyUnusedLocal
	def __init__(self, func, when, *argums, start_time=None, name=None, repeating=True,
			threaded=True, ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None, **keyargs):
		super().__init__(func, when, name, repeating,
			threaded, ignore_exceptions, retrys, retry_time, alt_func)
		if isinstance(start_time, str):
			self.start_time = parse.datetime_string(start_time)
		else:
			self.start_time = start_time
		self.time_initialized = now()

	@property
	def next_run_time(self):
		"""
		Returns the next run time based on the set time interval
		"""
		if not self.is_paused():
			if not self.first_run_time:
				if self.start_time:
					if self.is_in_future(self.start_time):
						return self.start_time
				return self.time_initialized + parse.duration_string(self.when)
			else:
				return self.last_run_time + parse.duration_string(self.when)


class DatetimeJob(Job):
	"""
	A Job Type that sets up execution based on a specific datetime and interval.
	For example it could execute every day at noon, every Tuesday or the 15th
	of the month. Works best for jobs that need to run at specific times in intervals
	of a day or greater.
	"""
	# noinspection PyUnusedLocal
	def __init__(self, func, when, *argums, interval=None, name=None, repeating=True, threaded=True,
			ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None, custom_format=None, **keyargs):
		super().__init__(func, when, name, repeating, threaded, ignore_exceptions, retrys, retry_time, alt_func)
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
		"""
		Returns the next run time based on the set datetime and interval
		"""
		if not self.is_paused():
			return self.increment(parse.datetime_string(self.when, self.custom_format))

	def increment(self, when):
		"""
		Takes a datetime object and if it is in the past compared to the present it will
		add the defined interval of time to it till it is in the future
		"""
		while not self.is_in_future(when):
			n = now()
			if self.interval == 'daily':
				when = when + timedelta(days=1)
			elif self.interval == 'weekly':
				when = when + timedelta(days=7)
			elif self.interval == 'monthly':
				when = when + timedelta(days=monthrange(n.year, n.month)[1])
			elif self.interval == 'yearly':
				if isleap(n.year) and self.is_in_future(datetime(year=n.year, month=2, day=29)):
					when = when + timedelta(days=366)
				else:
					when = when + timedelta(days=365)
		return when


class DatetimesJob(DatetimeJob):
	"""
	A Job Type that sets up execution based on multiple datetimes and an interval.
	For example it could execute every 1st of the month at 5:30 pm and every 15th of the month at 12:30 am.
	Works best for jobs that need to run at multiple specific times in intervals of a day or greater.
	The 'when' argument needs to be a string with a comma delimiting the datetimes
	"""
	# noinspection PyUnusedLocal
	def __init__(self, func, when, interval, *argums, name=None, repeating=True, threaded=True,
			ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None, custom_format=None, **keyargs):
		super().__init__(func, when, interval, name, repeating, threaded,
			ignore_exceptions, retrys, retry_time, alt_func, custom_format)
		self.queue = deque([parse.datetime_string(dt.rstrip(' ').lstrip(' '), custom_format) for dt in when.split(',')])

	@property
	def next_run_time(self):
		"""
		Returns the next run time based on the set datetime and interval
		for the next datetime in the queue
		"""
		if not self.is_paused():
			x = len(self.queue)
			while x > 0 and not self.is_in_future(self.queue[0]):
				x -= 1
				self.queue.rotate()
			if self.last_run_time == self.queue[0]:
				self.queue.rotate()
			next_runtime = self.increment(self.queue[0])
			self.queue[0] = next_runtime
			return next_runtime
