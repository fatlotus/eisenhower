## Interstate

This project is a basic job execution helper. It that allows people to better run in-line functions and closures on remote computers.

For example:

```python

import interstate
import time

def my_job(environ):
  for i in xrange(0, 100):
    time.sleep(1)

interstate.execute(my_job, host = "ssh://jeremy@my-remote-computer")
  # Could also be ..., hosts = [ "ssh://...", "ssh://..." ], to run on
  # multiple hosts in parallel.

```

#### Larger Example

Suppose we wish to factor a large number, and have significant compute power to waste. We thus decide to do the following:

```python

import interstate
import math

def parallel_factor(number):
  last_number = math.sqrt(number)
  
  def process_factors(environ):
    start = int(environ["start_slice"] * last_number)
    end = int(environ["end_slice"] * last_number)
    
    if start <= 2:
      start = 2
    
    for i in xrange(start, end):
      if number % i == 0:
        print "%i has factor %i" % (number, i)
  
  hosts = [ ]
  
  for i in xrange(0, 999):
    hosts.append("ssh://node-%3i.very-large-cluster.1e100.net" % i)
  
  interstate.execute(process_factors, hosts = hosts)

parallel_factor(1000000007)
```

#### Firewalled Cluster Operation

If the nodes you are using are behind a firewall and require first connecting to a head node, you might find the following snippet helpful. It uses the `via` option to forward a connection to the given host and port before connecting to the destination.

```python

import interstate

def test_forwarded_connection():
  print "It works!"
  
interstate.execute(test_forwarded_connection,
  host = 'ssh://privateuser@inner-node.local',
  via = 'ssh://publicuser@head-node.very-large-cluster.1e100.net')
```

#### License

Copyright (c) 2013 Jeremy Archer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

