"""Logging functionality"""

from datetime import datetime

class StatusMessenger:
    """Handler for status messages. Instances are callable 
    and send messages to a specified output (e.g. console 
    or ui element)."""

    def __init__(self, out_fcn):
        """
        Creates a callable object that can forward messages
        in string format to a specified output.

        Arguments:
        - out_fcn: function to display status messages (e.g. print)"""
        self._out_fcn = out_fcn
        self.message_log:list = []

    def __call__(self, message:str):
        """"""
        # display message
        self._out_fcn(message)
        # add message to log
        log_entry = {
            "timestamp": datetime.now(),
            "message": message,
        }
        self.message_log.append(log_entry)
    
    def clear_log(self):
        self.message_log = []
    
status_in_console = StatusMessenger(print)


class StatusLogger:
    """Simple message logger"""

    def __init__(self):
        self.data:list[dict] = []

    def add_log(self, message:str, source:str):
        """Create a now log record."""
        log = {
            'date':datetime.now(),
            'source':source, 
            'message':message
        }
        self.data.append(log)
    
    def get_log(self, idx:int=-1):
        """Get a log entry (the latest by default)."""
        if self.data:
            return self.data[idx]
    
    def clear(self):
        """Clear log data."""
        self.data = []
    
    def to_console(self, idx):
        """Prints a status message to the console/terminal 
        (the latest by default)."""
        log = self.get_log(idx)
        if log:
            print(log['message'])
    

