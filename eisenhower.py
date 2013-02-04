import subprocess
import marshal
import atexit
import base64
import select
import urlparse
import pickle
import sys

class Connection(object):
  """
  Manages a connection to the Python interpreter on a remote machine.
  
  Usually, this connection is made with SSH.
  """
  
  def __init__(self, input, output):
    """
    Initializes this Connection given input and output streams.
    """
    
    self.input = input
    self.output = output
    self.consumed = False
  
  def send_function(self, method, *vargs, **dargs):
    """
    Serializes the given callable object and sends it over the wire,
    returning any results present in evaluation.
    """
    
    if self.consumed:
      raise StateError, "Cannot reuse SSH connections."
    else:
      self.consumed = True
    
    template = """

import pickle
import marshal
import base64
import types
import sys

def make_cell(x):
  return (lambda: x).func_closure[0]

vargs = pickle.loads(%(vargs)s)
dargs = pickle.loads(%(dargs)s)

code = marshal.loads(%(code)s)
closure = %(closure)s
tuple_of_cells = tuple( make_cell(x) for x in closure ) if closure else None
function = types.FunctionType(code, globals(), %(name)s, %(defaults)s, tuple_of_cells)
function.__module__ = %(module)s
result = function(*vargs, **dargs)
sys.stdout.write(base64.b64encode(marshal.dumps(result)))
sys.stdout.close()

    """ % dict(
      code = repr(marshal.dumps(method.func_code)),
      name = repr(method.func_name),
      module = repr(method.__module__),
      defaults = repr(method.func_defaults),
      closure = repr([ x.cell_contents for x in method.func_closure ]) if method.func_closure else "None",
      
      vargs = repr(pickle.dumps(vargs)),
      dargs = repr(pickle.dumps(dargs))
    )
    
    self.input.write(template)
    self.input.close() # Python interpreter doesn't run the code until here.
  
  def fileno(self): # :nodoc:
    """
    Returns the file descriptor of the output stream, meaning that
    Connection objects can be monitored just like sockets or files
    using the "select" function.
    """
    return self.output.fileno()
  
  def update(self):
    """
    Pulls a line of input from this connection or reports termination.
    """
    
    # N.B.: This may block if lines are too long!
    read = self.output.readline()
    
    if read[-1:] != "\n":
       # We're done with this channel, so pack up the 
       # return value and shut down.
      
      if read == "":
        sys.stderr.write("(connection terminates)\n")
        sys.stderr.flush()
        return (False, None)
      
      return_value = marshal.loads(base64.b64decode(read))
      self.output.close()
      
      return (False, return_value)
    else:
      
      # We expect more input.
      print read,
      return (True, None)
  
  @classmethod
  def establish_ssh_connection(self, user, host, port = None, via = None):
    """
    Creates and returns a SSH Connection to the server on the given
    host and port. This method assumes that passwordless SSH
    authentication has already been set up.
    """
    
    if user:
      netloc = '%s@%s' % (user, host)
    else:
      netloc = host
    
    args = [ '/usr/bin/env' ]
    
    if via: # Allows connection by proxy.
      args.extend([ 'ssh', '-p', str(via[1] or 22), via[0] ])
    
    args.extend([ 'ssh', '-p', str(port or 22), netloc, 'python', '-u' ])
    
    command = subprocess.Popen( # This assumes that Python is in the PATH.
      args = args,
      stdin = subprocess.PIPE,
      stdout = subprocess.PIPE
    )
    
    # Ensure that the connection is terminated on system shutdown.
    atexit.register(command.terminate)
    
    # Initialize a connection over the given stream.
    return Connection(output = command.stdout, input = command.stdin)

def execute(function, host = None, hosts = [ ], via = None):
  """
  Executes the given function on each of the hosts specified in the 
  "hosts" array, or just on the single "host" specified.
  
  This method does not process return values.
  """
  
  if host is not None:
    hosts.append(host)
  
  if len(hosts) == 0:
    raise ValueError, "Must run on at least one host."
  
  if type(via) in (str, unicode):
    result = urlparse.urlparse(via)
    
    if result.scheme != 'ssh':
      raise ValueError, "Can only forward via SSH."
    
    via = ('%s@%s' % (result.username, result.hostname), result.port)
  
  connections = [ ]
  
  for host_index, host in enumerate(hosts):
    result = urlparse.urlparse(host, scheme = 'ssh')
    
    if result.scheme != 'ssh':
      raise ValueError, "Can only connect to SSH."
    
    connection = Connection.establish_ssh_connection(
      user = result.username,
      host = result.hostname,
      port = result.port,
      via = via
    )
    
    # Prepare some basic information for the new job.
    environment = dict()
    environment["current_host"] = host
    environment["hosts"] = hosts
    
    environment["host_number"] = host_index
    environment["total_hosts"] = len(hosts)
    
    environment["start_slice"] = float(host_index) / len(hosts)
    environment["end_slice"]   = float(host_index) / len(hosts)
    
    connection.send_function(function, environment)
    
    connections.append(connection)
  
  while connections != [ ]:
    (reads, writes, exceptions) = select.select(connections, [ ], connections, None)
    
    for read in reads:
      (keep_going, return_value) = read.update()
      
      if not keep_going:
        connections.remove(read)
    
    for exception in exceptions:
      connections.remove(exception)