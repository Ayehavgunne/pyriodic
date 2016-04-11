import os

try:
	import cherrypy
except ImportError:
	cherrypy = None

job_template = '''
<tr class="job" data-job="{0}">
	<td rowspan=2>
		<span class="jobName run" title="click to run now">{0}</span>
	</td>
	<td>
		<span class="when">Interval: {3}</span>
	</td>
	<td>
		<span class="lastRunTime">Last Run Time: {1}</span>
	</td>
	<td>
		<span>Run Count: {5}</span>
	</td>
	<td rowspan=2>
		<div class="start">Start</div>
		<div class="pause">Pause</div>
		<div class="remove">Remove</div>
	</td>
</tr>
<tr class="job divider" data-job="{0}">
	<td>
		<span>Status: {4}</span>
	</td>
	<td colspan=2>
		<span class="nextRunTime">Next Run Time: {2}</span>
	</td>
</tr>'''


def start_web_interface(scheduler):
	"""
	Sets up the web interface for displaying and maintining of jobs within the scheduler
	"""
	# noinspection PyPep8Naming
	class Jobs(object):
		exposed = True

		def GET(self, name=None):
			html = ''
			if name:
				html = self.job_to_html(scheduler.get_job(name))
			else:
				for job in scheduler.jobs:
					html = '{}{}'.format(html, self.job_to_html(job))
			return html

		# noinspection PyMethodMayBeStatic
		def POST(self):
			raise cherrypy.HTTPError(405, 'Method not implemented.')

		def PUT(self, name=None, status=None, when=None):
			if status != 'when':
				if name == 'all':
					if status == 'pause':
						scheduler.pause_all()
					elif status == 'start':
						scheduler.start_all()
				else:
					job = scheduler.get_job(name)
					if status == 'pause':
						job.pause()
					elif status == 'start':
						job.start()
					elif status == 'run':
						job.run()
			else:
				if name != 'all' and when:
					job = scheduler.get_job(name)
					job.when = when
					scheduler.reset()
			return self.GET()

		def DELETE(self, name=None):
			if name:
				scheduler.remove(name)
			else:
				for job in reversed(scheduler.jobs):
					scheduler.remove(job.name)
			return self.GET()

		@staticmethod
		def job_to_html(job):
			return job_template.format(
				job.name,
				job.last_run_time.strftime('%Y-%m-%d %I:%M:%S %p') if job.last_run_time else '',
				job.next_run_time.strftime('%Y-%m-%d %I:%M:%S %p') if job.next_run_time else '',
				job.when,
				job.status.title(),
				job.run_count
			)

		@staticmethod
		def job_history_to_html(job):
			html = '<div class="job" data-job="{}">'.format(job.name)
			for run_time in job.run_time_history:
				html = '{}<div>{}</div>'.format(html, run_time.strftime('%Y-%m-%d %I:%M:%S %p'))
			html = '{}</div>'.format(html)
			return html

	class Interface(object):
		jobs = Jobs()

		def __init__(self):
			self.running = False
			cherrypy.engine.subscribe('start', self.start)
			cherrypy.engine.subscribe('stop', self.stop)

		@cherrypy.expose
		def index(self):
			return open(os.path.join(os.path.dirname(__file__), './interface.html'))

		def start(self):
			self.running = True

		def stop(self):
			self.running = False

	conf = {
		'/jobs': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		}
	}

	cherrypy.tree.mount(Interface(), '/pyriodic', config=conf)
