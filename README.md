## Interstate

This project is a job execution helper that allows people to very easily run functions on remote computers.

For example:

```python

import interstate

def my_job():
  for i in xrange(0, 100):
    thread.sleep(1)
    print "Processing..."

interstate.execute(my_job, host = "ssh://jeremy@my-remote-computer")
  # Could also be ..., hosts = [ "ssh://...", "ssh://..." ], to run on
  # multiple hosts in parallel.

```