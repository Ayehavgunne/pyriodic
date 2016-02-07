import os
try:
	import cherrypy
except ImportError:
	cherrypy = None

port = 8765

def start_web_interface(scheduler):
	if cherrypy:
		class Interface(object):
			@cherrypy.expose
			def index(self):
				return open(os.path.join(os.path.dirname(__file__), './interface.html'))

			@cherrypy.expose
			def getjobs(self):
				html = ''
				for job in scheduler.jobs:
					html = '{0}<div class="job" id="{1}"><div><span class="jobName">{1}</span><span class="funcName">Function: {2}</span></div><div><span class="lastRunTime">Last Run Time: {3}</span><span class="nextRunTime">Next Run Time: {4}</span></div><span class="startJob">Start</span><span class="pauseJob">Pause</span><span class="clearJob">Clear</span></div>'.format(html, job.name, job.func.__name__, job.last_run_time.strftime('%Y-%m-%d %H:%M:%S'), job.next_run_time().strftime('%Y-%m-%d %H:%M:%S'))
				return html

		cherrypy.config.update({'server.socket_port': port})
		cherrypy.quickstart(Interface(), '/')