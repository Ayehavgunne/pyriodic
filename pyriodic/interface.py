import os
try:
	import cherrypy
except ImportError:
	cherrypy = None

port = 8765

def start_web_interface(scheduler):
	if cherrypy:
		# noinspection PyPep8Naming
		# noinspection PyMethodMayBeStatic
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

			def POST(self):
				raise cherrypy.HTTPError(405, 'Method not implemented.')

			def PUT(self, status, name=None):
				action = getattr(scheduler, status)
				if name:
					action(name, True)
				else:
					for job in scheduler.jobs:
						action(job.name, True)

			def DELETE(self, name=None):
				if name:
					scheduler.remove(name)
				else:
					for job in reversed(scheduler.jobs):
						scheduler.remove(job.name)

			@staticmethod
			def job_to_html(job):
				return '<div class="job" data-job="{0}"><div><span class="jobName">{0}</span><span class="funcName">Function: {1}</span></div><div><span class="lastRunTime">Last Run Time: {2}</span><span class="nextRunTime">Next Run Time: {3}</span></div><div><span class="when">Interval: {4}</span></div><span class="start">Start</span><span class="pause">Pause</span><span class="clear">Clear</span></div>'.format(job.name, job.func.__name__, job.last_run_time.strftime('%Y-%m-%d %I:%M:%S %p'), job.next_run_time().strftime('%Y-%m-%d %I:%M:%S %p'), job.when)

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

		cherrypy.config.update({'server.socket_port': port, 'engine.autoreload.on': False})
		cherrypy.quickstart(Interface(), '/', config=conf)