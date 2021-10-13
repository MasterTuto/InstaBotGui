import threading

class InstaBotThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(InstaBotThread, self).__init__(*args, **kwargs)
        self.stop_event = threading.Event()
    
    def stop(self):
        self.stop_event.set()
    
    def stoped(self):
        return self.stop_event.is_set()