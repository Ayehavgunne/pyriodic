from threading import Timer
from . import now

class Scheduler(object):
	def __init__(self, log_path=None):
		self.jobs = []
		self.current_job = None
		self.sleeper = None
		self.running = False
		if log_path:
			import logging
			self.log_path = log_path
			self.log = logging.basicConfig(filename=log_path)

	def set_timer(self):
		if self.jobs:
			next_job = self.jobs[0]
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
			if self.current_job.args and not self.current_job.kwargs:
				self.current_job.func(*self.current_job.args)
			elif not self.current_job.args and self.current_job.kwargs:
				self.current_job.func(**self.current_job.kwargs)
			elif self.current_job.args and self.current_job.kwargs:
				self.current_job.func(*self.current_job.args, **self.current_job.kwargs)
			else:
				self.current_job.func()
			if self.log:
				self.log.info('Job "{}" was executed. Run count = {}'.format(self.current_job.name, self.current_job.run_count))
			self.current_job.run_count += 1
			self.current_job.last_run_time = now()
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
			job.name = 'job{}'.format(len(self.jobs) + 1)
		job.last_run_time = now()
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

	def remove(self, name):
		del self.jobs[self.find_job_index(name)]

	def pop(self, name):
		return self.jobs.pop(self.find_job_index(name))

	def job_names(self):
		return [job.name for job in self.jobs]

	def find_job_index(self, name):
		for x, job in enumerate(self.jobs):
			if job.name == name:
				return x

	def next_run_times(self):
		return {job.name: job.next_run_time() for job in self.jobs}

	def start(self):
		self.sort_jobs()
		self.set_timer()

	def stop(self):
		self.running = False
		if self.sleeper:
			self.sleeper.cancel()