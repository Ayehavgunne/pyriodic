from datetime import datetime

now = datetime.now

from pyriodic.interface import start_web_interface
from pyriodic.scheduler import Scheduler
from pyriodic.jobs import DurationJob
from pyriodic.jobs import DatetimeJob