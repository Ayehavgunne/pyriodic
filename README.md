#Pyriodic

_Pronounced just like "periodic"_

A job scheduler written in Python to run periodic tasks.

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

---

##Usage

```python
from pyriodic import DurationJob
from pyriodic import DatetimeJob
from pyriodic import Scheduler

s = Scheduler()

start = datetime.now()

def func1(arg1=None, arg2=None, arg3=None, arg4=None):
	print('Func 1', arg1, arg2, arg3, arg4, datetime.now() - start, datetime.now())

def func2():
	print('Func 2', datetime.now() - start, datetime.now())

def func3():
	print('Func 3', datetime.now() - start, datetime.now())

s.add_job(DurationJob(func1, when='30m', args=('This', 'is'), kwargs={'arg3': 'the', 'arg4': 'first function'}, name='MyJob'))
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
- [ ] Add more options for error handling
  - [ ] Add option for a waiting time before the next function call after an exception
  - [ ] Add option for the number of retrys after exceptions
  - [ ] Add the option to execute a different function upon an exception
- [ ] A web front end; probably with CherryPy
  - [ ] Be able to see the scheduled jobs
  - [ ] Control jobs; pause, remove, reschedule
- [ ] Expand the abilities of the custom datetime string parser in case dateutil cannot be used
- [x] Add stop and start methods to scheduler
- [x] Add some kind of logging for executed tasks