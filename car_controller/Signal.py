""" Generic MVC signal."""
class Signal():
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        """
        Connect a method to the signal.

        When the signal is emitted, all connected methods will
        be called in order of connection.
        """
        self.callbacks.append(callback)

    def emit(self):
        """ 
        Emit the signal.
        
        Emitting the signal means calling all registered callbacks,
        in order connected.
        """
        for callback in self.callbacks:
            callback()