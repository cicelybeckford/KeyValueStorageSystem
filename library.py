"""A set of libraries that are useful to both the proxy and regular servers."""

# This code uses Python 2.7. These imports make the 2.7 code feel a lot closer
# to Python 3. (They're also good changes to the language!)
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# THe Python socket API is based closely on the Berkeley sockets API which
# was originally written for the C programming language.
#
# https://en.wikipedia.org/wiki/Berkeley_sockets
#
# The API is more flexible than you need, and it does some quirky things to
# provide that flexibility. I recommend tutorials instead of complete
# descriptions because those can skip the archaic bits. (The API was released
# more than 35 years ago!)
import socket

import time

# Read this many bytes at a time of a command. Each socket holds a buffer of
# data that comes in. If the buffer fills up before you can read it then TCP
# will slow down transmission so you can keep up. We expect that most commands
# will be shorter than this.
COMMAND_BUFFER_SIZE = 256

def CreateServerSocket(port):
    """Creates a socket that listens on a specified port.
        
        Args:
        port: int from 0 to 2^16. Low numbered ports have defined purposes. Almost
        all predefined ports represent insecure protocols that have died out.
        Returns:
        An socket that implements TCP/IP.
        """

    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.bind(('', port))
      sock.listen(5)
    except socket.error, e:
      print(e)
      sys.exit(1)
    return sock

def ConnectClientToServer(server_sock):
    # Wait until a client connects and then get a socket that connects to the
    # client.
    
    print("Waiting for client...")
    return server_sock.accept()



def CreateClientSocket(server_addr, port):
    """Creates a socket that connects to a port on a server."""
    
    try:
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((server_addr, port))
    except socket.error, e:
      print(e)
      sys.exit(1)
    return sock

def ReadCommand(sock):
    """Read a single command from a socket. The command must end in newline."""
    
    try:
        data = sock.recv(COMMAND_BUFFER_SIZE)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            sleep(1)
            print("No data available")
        else:
            print(e)
            sys.exit(1)
    return data



def ParseCommand(command):
    """Parses a command and returns the command name, first arg, and remainder.
        
        All commands are of the form:
        COMMAND arg1 remaining text is called remainder
        Spaces separate the sections, but the remainder can contain additional spaces.
        The returned values are strings if the values are present or `None`. Trailing
        whitespace is removed.
        
        Args:
        command: string command.
        Returns:
        command, arg1, remainder. Each of these can be None.
        """
    args = command.strip().split(' ')
    command = None
    if args:
        command = args[0]
    arg1 = None
    if len(args) > 1:
        arg1 = args[1]
    remainder = None
    if len(args) > 2:
        remainder = ' '.join(args[2:])
    return command, arg1, remainder


class KeyValueStore(object):
    """A dictionary of strings keyed by strings.
        
        The values can time out once they get sufficiently old. Otherwise, this
        acts much like a dictionary.
        """
    
    def __init__(self):

        self._dict = {}
    
    def GetValue(self, key, max_age_in_sec=None):
        """Gets a cached value or `None`.
            
            Values older than `max_age_in_sec` seconds are not returned.
            
            Args:
            key: string. The name of the key to get.
            max_age_in_sec: float. Maximum time since the value was placed in the
            KeyValueStore. If not specified then values do not time out.
            Returns:
            None or the value.
            """
        # Check if we've ever put something in the cache.

        val = None
        if key in self._dict:
            tup = self._dict[key]
            age = time.time() - tup[1]
            val = tup[0]
            if max_age_in_sec and age > max_age_in_sec:
                del self._dict[key]
                val = None
        return val
    
    
    
    def StoreValue(self, key, value):
        """Stores a value under a specific key.
            
            Args:
            key: string. The name of the value to store.
            value: string. A value to store.
            """
        
        self._dict[key] = (value, time.time())
    
    
    def Keys(self):
        """Returns a list of all keys in the datastore."""
        
        return self._dict.keys()

