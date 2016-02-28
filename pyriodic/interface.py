import os


try:
	import cherrypy
except ImportError:
	cherrypy = None


def start_web_interface(scheduler):
	if cherrypy is None:
		raise TypeError('The web interface requires that CherryPy be installed')
	else:
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
				return '<div class="job" data-job="{0}"><div><span class="jobName">{0}</span></div><div><span ' \
					'class="funcName">Function: {1}</span><span>Run Count: {6}</span></div><div><span ' \
					'class="lastRunTime">Last Run Time: {2}</span><span class="nextRunTime">Next Run Time: {' \
					'3}</span></div><div><span class="when">Interval: {4}</span><span>Status: {' \
					'5}</span></div><span class="start">Start</span><span class="pause">Pause</span><span ' \
					'class="clear">Clear</span></div>'.format(job.name, job.func.__name__,
						job.last_run_time.strftime('%Y-%m-%d %I:%M:%S %p') if job.last_run_time else '',
						job.next_run_time.strftime('%Y-%m-%d %I:%M:%S %p') if job.next_run_time else '',
						job.when, job.status.title(), job.run_count)

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
				scheduler.stop()


		conf = {
			'/jobs': {
				'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			}
		}

		cherrypy.tree.mount(Interface(), '/pyriodic', config=conf)
