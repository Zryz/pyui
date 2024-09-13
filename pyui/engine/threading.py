from typing import List, Dict
import threading

class Threader:
    def __init__(self) -> None:
        
        self.threads:Dict[int, List[threading.Thread, threading.Event]] = {}
        self.stop_events: Dict [int, threading.Event] = {}
        self.stack = []

        self.lock = threading.Lock()

    def next_id(self):
        return len(self.stack)+1

    def pop_thread(self, id):
        if not self.stack: return
        return self.stop_thread(self.threads.pop(id))
    
    def new_event(self):
        return threading.Event()
    
    def new_thread(self, task:callable, *args)->threading.Thread:
        thread = threading.Thread(target=task, args=(args), daemon=True)
        return self.register_thread(thread, args)
    
    def reset_threads(self):
        if not self.stack:return
        while self.stack:
            self.stop_thread(self.stack.pop())

    def register_thread(self, thread, stop_event)->int:
        next_id = len(self.stack) + 1
        self.threads[next_id] = [thread, stop_event]
        self.stack.append(next_id)
        thread.start()
        return next_id

    #Start a thread by it's ID
    def start_thread(self, id)->int:
        self.threads[id][0].start()

    #Remove a thread by it's ID
    def stop_thread(self, id):
        self.threads[id][1][0].set()
        self.threads[id][0].join()
