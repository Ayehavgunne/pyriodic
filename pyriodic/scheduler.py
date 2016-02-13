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
			while self.jobs[x].status == 'paused':
				x += 1
				if x >= len(self.jobs):
					return
			next_job = self.jobs[x]
			if self.current_job != next_job:
				if self.sleeper:
					self.sleeper.cancel()
				wait_time = (next_job.next_run_time() - now()).total_seconds()
				self.sleeper = Timer(wait_time, self.execute_job)
				self.sleeper.start()
				next_job.scheduled = True
				self.current_job = next_job
				self.running = True

	def execute_job(self):
		if self.current_job:
			if self.current_job.threaded:
				self.current_job.thread = Thread(target=job_func_wrapper, args=(self.current_job,))
				self.current_job.thread.start()
			else:
				job_func_wrapper(self.current_job)
			self.log.info('Job "{}" was started. Run count = {}'.format(self.current_job.name, self.current_job.run_count))
			self.current_job.add_run_time(now())
			self.current_job.scheduled = False
			self.current_job = None
		if self.running:
			self.trim_jobs()
			self.sort_jobs()
			self.set_timer()

	def sort_jobs(self):
		if len(self.jobs) > 1:
			self.jobs.sort(key=lambda job: job.next_run_time())

	def add_job(self, job):
		if job.name is None:
			job.name = 'Job{}'.format(len(self.jobs) + 1)
		self.jobs.append(job)
		self.sort_jobs()
		self.set_timer()
		return job.name

	def trim_jobs(self):
		for job in self.jobs:
			if not job.scheduled and not job.repeating and job.run_count > 0:
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

	def remove(self, name, _=False):
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
		return {job.name: job.next_run_time() for job in self.jobs}

	def start(self, name=None, _=False):
		if name:
			self.jobs[self.find_job_index(name)].status = 'waiting'
		self.reset()

	def stop(self):
		self.running = False
		self.current_job = None
		if self.sleeper:
			self.sleeper.cancel()

	def pause(self, name, cancel_current=False):
		job = self.jobs[self.find_job_index(name)]
		job.status = 'paused'
		if cancel_current:
			if self.current_job == job:
				self.reset()

	def start_web_server(self, existing=False, port=8765):
		import cherrypy
		start_web_interface(self)
		if existing:
			cherrypy.config.update({'server.socket_port': port, 'engine.autoreload.on': False})
			cherrypy.engine.start()

def job_func_wrapper(job):
	job.status = 'running'
	args = job.args
	kwargs = job.kwargs
	if args and not kwargs:
		job.func(*args)
	elif not args and kwargs:
		job.func(**kwargs)
	elif args and kwargs:
		job.func(*args, **kwargs)
	else:
		job.func()
	job.status = 'waiting'