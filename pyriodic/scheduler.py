from threading import Timer
from threading import Thread
from . import now
from . import start_web_interface

class Scheduler(object):
	def __init__(self, log_path=None, web=False):
		self.jobs = []
		self.current_job = None
		self.current_job_thread = None
		self.sleeper = None
		self.running = False
		self.log_path = None
		self.log = None
		self.web = None
		if log_path:
			import logging
			self.log_path = log_path
			logging.basicConfig(filename=log_path)
			self.log = logging.getLogger('Scheduler')
		if web:
			self.web = Thread(target=start_web_interface, args=(self,))
			self.web.start()

	def set_timer(self):
		if self.jobs:
			x = 0
			while self.jobs[x].paused:
				x += 1
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
				self._run_threaded()
				self.current_job_thread.start()
			else:
				self._run_synchronously()
			self.current_job.run_count += 1
			if self.log:
				self.log.info('Job "{}" was started. Run count = {}'.format(self.current_job.name, self.current_job.run_count))
			self.current_job.last_run_time = now()
			self.current_job.scheduled = False
			self.current_job = None
		if self.running:
			self.trim_jobs()
			self.sort_jobs()
			self.set_timer()

	def _run_threaded(self):
		if self.current_job.args and not self.current_job.kwargs:
			self.current_job_thread = Thread(target=self.current_job.func, args=self.current_job.args)
		elif not self.current_job.args and self.current_job.kwargs:
			self.current_job_thread = Thread(target=self.current_job.func, kwargs=self.current_job.kwargs)
		elif self.current_job.args and self.current_job.kwargs:
			self.current_job_thread = Thread(target=self.current_job.func, args=self.current_job.args, kwargs=self.current_job.kwargs)
		else:
			self.current_job_thread = Thread(target=self.current_job.func)

	def _run_synchronously(self):
		if self.current_job.args and not self.current_job.kwargs:
			self.current_job.func(*self.current_job.args)
		elif not self.current_job.args and self.current_job.kwargs:
			self.current_job.func(**self.current_job.kwargs)
		elif self.current_job.args and self.current_job.kwargs:
			self.current_job.func(*self.current_job.args, **self.current_job.kwargs)
		else:
			self.current_job.func()

	def sort_jobs(self):
		if len(self.jobs) > 1:
			self.jobs.sort(key=lambda job: job.next_run_time())

	def add_job(self, job):
		if job.name is None:
			job.name = 'Job{}'.format(len(self.jobs) + 1)
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

	def reset(self):
		self.running = True
		self.current_job = None
		if self.sleeper:
			self.sleeper.cancel()
		self.sort_jobs()
		self.set_timer()

	def remove(self, name):
		idx = self.find_job_index(name)
		if self.current_job == self.jobs[idx]:
			self.reset()
		del self.jobs[idx]

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

	def start(self, name=None):
		if name:
			self.jobs[self.find_job_index(name)].paused = False
		self.reset()

	def stop(self):
		self.running = False
		self.current_job = None
		if self.sleeper:
			self.sleeper.cancel()

	def pause(self, name, cancel_current=False):
		job = self.jobs[self.find_job_index(name)]
		job.paused = True
		if cancel_current:
			if self.current_job == job:
				self.reset()