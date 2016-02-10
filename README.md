#Pyriodic

_Pronounced just like "periodic"_

A job scheduler for running periodic tasks in Python.

This project is in the alpha stage so there is a lot yet to do.

---

##Installation

```
pip install pyriodic
```

---

##Dependencies

Pyriodic can be installed and used on it's own but if tasks need to be scheduled at a specific date/time then the module dateutil is invaluble. Without it acceptable datetime strings are rather limited.

If dateutil is already installed then it will be used automatically.

For the web front end to work CherryPy must be installed but it is entirely optional to use.

---

##Usage

```python
from pyriodic import DurationJob
from pyriodic import DatetimeJob
from pyriodic import Scheduler

now = datetime.now
s = Scheduler()

start = now()

def func1(arg1=None, arg2=None, arg3=None, arg4=None):
	print('Func1', arg1, arg2, arg3, arg4, now() - start, now())

def func2():
	print('Func2', now() - start, now())

def func3():
	print('Func3', now() - start, now())

s.add_job(DurationJob(func1,
                    when='30m',
                    args=('This', 'is'),
                    kwargs={'arg3': 'the', 'arg4': 'first function'},
                    name='MyJob'))
s.add_job(DurationJob(func2, when='2h'))
s.add_job(DatetimeJob(func3, when='12:00 pm'))

print(s.next_run_times())
```


---

##Todo

- [ ] Add timezone awareness
- [ ] Add tests
- [ ] Add docstrings
- [ ] Add ability to schedule jobs with decorators
- [ ] Expand capabilities of a datetime scheduled task
  - [x] Allow daily tasks
  - [ ] Allow tasks to run on specific days, example: tuesday, thursday and friday only at noon
  - [ ] Allow weekly tasks
  - [ ] Allow monthly tasks
  - [ ] Allow yearly tasks
- [ ] Add options for error handling
  - [ ] Add option for a waiting time before the next function call after an exception
  - [ ] Add option for the number of retrys after exceptions
  - [ ] Add the option to execute a different function upon an exception
- [x] A web front end using CherryPy
  - [x] Be able to see the scheduled jobs
  - [x] Control jobs; pause, start back up, remove, reschedule
- [x] Expand the abilities of the custom datetime string parser in case dateutil cannot be used
- [x] Add stop and start methods to scheduler
- [x] Add some kind of logging for executed tasks