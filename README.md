#pyriodic
A scheduler written in Python using dateutil to run periodic jobs.

This project is in the alpha stage so there is a lot yet to do.


---

##Todo

- [ ] Add timezone awareness
- [ ] Add logging capability
- [ ] Add more options for error handling
  - [ ] Add option for a waiting time before the next function call after an exception
  - [ ] Add option for the number of retrys after exceptions
  - [ ] Add the option to execute a different function upon an exception
- [ ] Add docstrings
- [ ] Add capturing of function results
- [ ] A web front end; probably with CherryPy
  - [ ] Be able to see the scheduled jobs
  - [ ] Control jobs; pause, stop, reschedule, (see results?)
- [ ] Allow setup with a configuration file
- [ ] Add a shutdown process
- [ ] Return the job to allow easier access to it later