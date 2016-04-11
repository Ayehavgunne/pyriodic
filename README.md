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

Pyriodic can be installed and used on it's own but if tasks need to be
scheduled at a specific date/time then the module dateutil is invaluble.
Without it acceptable datetime strings are rather limited.

If dateutil is already installed then it will be used automatically.

For the web front end to work CherryPy must be installed but it is
entirely optional to use.

---

##Usage

```python
from pyriodic import DurationJob
from pyriodic import DatetimeJob
from pyriodic import DatetimesJob
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

my_job_handle = s.add_job(
	DurationJob(
		lambda: func1('This', 'is', arg3='the', arg4='first function'),
		'10s',
		name='MyJob',
		retrys=3,
		retry_time=5
	)
)
s.add_job(DatetimeJob(func2, when='Monday'))
s.add_job(DatetimesJob(
	func3,
	when='11:36 pm,11:37 pm',
	interval='daily'
))

print(s.next_run_times())
```


---

##Todo

- [ ] Add timezone awareness
- [ ] Write tests
- [ ] Add Python 2.7 compatibility
    - [ ] Use Six?
- [x] Add type hints
- [x] Add ability to schedule jobs with decorators
- [x] Expand types of scheduled tasks
    - [x] Allow daily tasks
    - [x] Allow weekly tasks
    - [x] Allow monthly tasks
    - [x] Allow yearly tasks
    - [x] Allow tasks to run on specific days, example:
        - [x] every tuesday, thursday and saturday
        - [x] 1st and 15th of the month
- [x] Add options for error handling
    - [x] Add option for a waiting time before the next function call
            after an exception
    - [x] Add option for the number of retrys after exceptions
    - [x] Add option to execute a different function upon an exception
- [x] A web front end using CherryPy
    - [x] Be able to see the scheduled jobs
    - [x] Control jobs; pause, start back up, remove, reschedule
    - [ ] Make the front end look better
- [x] Expand the abilities of the custom datetime string parser in case
        dateutil cannot be used
- [x] Add stop and start methods to scheduler
- [x] Add some kind of logging for executed tasks
- [ ] Add some backend storage options
