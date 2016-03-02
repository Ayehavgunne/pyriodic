from time import sleep
from datetime import datetime
from threading import Timer
from threading import Thread
from . import now
from . import start_web_interface


class Scheduler(object):
	def __init__(self, log=None):
		self.jobs = []
		self.current_job = None
		self.sleeper = None
		self.running = False
		if log:
			self.log = log
		else:
			import logging
			self.log = logging.getLogger('pyriodic_dummy')

	def set_timer(self):
		if self.jobs:
			x = 0
			while self.jobs[x].is_paused():
				x += 1
				if x >= len(self.jobs):
					return
			next_job = self.jobs[x]
			if self.current_job != next_job:
				if self.sleeper:
					self.sleeper.cancel()
				wait_time = (next_job.next_run_time - now()).total_seconds()
				self.sleeper = Timer(wait_time, self.execute_job)
				self.sleeper.start()
				self.current_job = next_job
				self.running = True

	def execute_job(self):
		if self.current_job:
			if not self.current_job.is_paused():
				if self.current_job.threaded:
					self.current_job.thread = Thread(target=job_func_wrapper,
						args=(self.current_job, self.log, self.current_job.retrys))
					self.current_job.thread.start()
				else:
					job_func_wrapper(self.current_job, self.log, self.current_job.retrys)
			self.current_job = None
		if self.running:
			self.trim_jobs()
			self.sort_jobs()
			self.set_timer()

	def sort_jobs(self):
		if len(self.jobs) > 1:
			self.jobs.sort(key=lambda job: job.next_run_time if job.next_run_time is not None else datetime.max)

	def add_job(self, job):
		if job.name is None:
			job.name = 'Job{}'.format(len(self.jobs) + 1)
		job.parent = self
		self.jobs.append(job)
		self.sort_jobs()
		self.set_timer()
		return job.name

	def schedule_job(self, job_type, when, args=None, kwargs=None, name=None, repeating=True, threaded=True,
			ignore_exceptions=False, retrys=0, retry_time=0, alt_func=None, start_time=None, interval=None,
			custom_format=None):
		def inner(func):
			self.add_job(job_type(func=func, when=when, args=args, kwargs=kwargs, name=name, repeating=repeating,
				threaded=threaded, ignore_exceptions=ignore_exceptions, retrys=retrys, retry_time=retry_time,
				alt_func=alt_func, start_time=start_time, interval=interval, custom_format=custom_format))
			return func
		return inner

	def trim_jobs(self):
		for job in self.jobs:
			if not job.repeating and job.run_count > 0:
				self.remove(job.name)

	def get_job(self, name):
		return self.jobs[self.find_job_index(name)]

	def reset(self):
		self.running = True
		self.current_job = None
		if self.sleeper:
			self.sleeper.cancel()
		self.sort_jobs()
		self.set_timer()

	def remove(self, name):
		del self.jobs[self.find_job_index(name)]
		self.reset()

	def pop(self, name):
		idx = self.find_job_index(name)
		if self.current_job == self.jobs[idx]:
			self.reset()
		return self.jobs.pop(idx)

	def job_names(self):
		return [job.name for job in self.jobs]

	def find_job_index(self, name):
		for x, job in enumerate(self.jobs):
			if job.name == name:
				return x

	def next_run_times(self):
		return {job.name: job.next_run_time for job in self.jobs}

	def start_all(self):
		for job in self.jobs:
			job.start()
		self.reset()

	def stop_scheduler(self):
		self.running = False
		self.current_job = None
		if self.sleeper:
			self.sleeper.cancel()

	def pause_all(self, cancel_current=False):
		for job in reversed(self.jobs):
			job.pause()
		if cancel_current:
			self.reset()

	def start_web_server(self, existing=False, port=8765):
		try:
			# noinspection PyUnresolvedReferences
			import cherrypy
			start_web_interface(self)
			if not existing:
				cherrypy.config.update({'server.socket_port': port})
				cherrypy.engine.start()
		except ImportError:
			raise ImportError('The web interface requires that CherryPy be installed')


def job_func_wrapper(job, log, retrys, alt=False):
	job.run()
	args = job.args
	kwargs = job.kwargs
	job.add_run_time(now())
	log.info('Job "{}" was started. Run count = {}'.format(job.name, job.run_count))
	try:
		if alt:
			if args and not kwargs:
				job.alt_func(*args)
			elif not args and kwargs:
				job.alt_func(**kwargs)
			elif args and kwargs:
				job.alt_func(*args, **kwargs)
			else:
				job.alt_func()
		else:
			if args and not kwargs:
				job.func(*args)
			elif not args and kwargs:
				job.func(**kwargs)
			elif args and kwargs:
				job.func(*args, **kwargs)
			else:
				job.func()
		job.wait()
	except Exception as e:
		job.exceptions.append((e, job.run_count))
		log.info('Job "{}" enountered an exception ({}). Run count = {}'.format(job.name, e, job.run_count))
		if retrys:
			if job.retry_time:
				job.pause()
				sleep(job.retry_time)
			if job.alt_func:
				job_func_wrapper(job, log, retrys - 1, True)
			else:
				job_func_wrapper(job, log, retrys - 1)
			job.parent.reset()
			return
		if not job.ignore_exceptions:
			job.pause()
			raise
