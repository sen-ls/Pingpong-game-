import threading


class ReadWriteLock:
    """
    This class defines a lock which is able to distinguish between read and write access to enable a higher
    performance while providing thread safe access.
    """
    def __init__(self):
        """
        Initialization of a ReadWriteLock object
        """
        # Internal lock to handle lock states
        self.lock = threading.Lock()

        # Lock states for read and write access
        self.reader_state, self.writer_state = threading.Condition(self.lock), threading.Condition(self.lock)

        # Amount of active read accesses
        self.readers = 0

        # Amount of waiting write accesses
        self.writer_in_queue = 0

        # Boolean if write access is granted currently
        self.writer_active = False

    def acquire_write_lock(self):
        """
        Acquires a write lock when it is possible. Otherwise waits until notified
        """
        self.lock.acquire()
        # Wait until no read access granted and no writer active
        while self.readers > 0 and self.writer_active:
            self.writer_in_queue += 1
            self.writer_state.wait()
            self.writer_in_queue -= 1
        self.writer_active = True
        self.lock.release()

    def release_write_lock(self):
        """
        Releases a write lock and notifies writers and readers
        """
        self.lock.acquire()
        self.writer_active = False
        # Check if writers or readers need to be notified
        if self.writer_in_queue > 0:
            self.writer_state.notify()
        else:
            self.reader_state.notifyAll()
        self.lock.release()

    def acquire_read_lock(self):
        """
        Acquires a read lock when it is possible. Otherwise waits until notified
        """
        self.lock.acquire()
        # Wait until no write access is granted
        while self.writer_in_queue or self.writer_active:
            self.reader_state.wait()
        self.readers += 1
        self.lock.release()

    def release_read_lock(self):
        """
        Releases a read lock and notifies writers
        """
        self.lock.acquire()
        # Adjust readers
        if self.readers > 0:
            self.readers -= 1
        # Check if writers could acquire write lock
        if self.readers == 0 and not self.writer_active:
            self.writer_state.notify()
        self.lock.release()


if __name__ == "__main__":

    import random
    import time

    class TestThread(threading.Thread):

        lock = ReadWriteLock()
        value = 0

        def __init__(self, t_id):
            super().__init__()
            self.running = True
            self.t_id = t_id

        def stop(self):
            self.running = False

        def run(self):
            while self.running:
                if random.randint(0, 1) == 0:
                    TestThread.lock.acquire_read_lock()
                    print('Thread {}: Reading value {}'.format(self.t_id, TestThread.value))
                    TestThread.lock.release_read_lock()
                else:
                    TestThread.lock.acquire_write_lock()
                    TestThread.value += 1
                    print('Thread {}: Writing value {}'.format(self.t_id, TestThread.value))
                    TestThread.lock.release_write_lock()

                sleep_time = random.randint(1, 5)
#                print('Thread {} sleeps for {} seconds.'.format(self.t_id, sleep_time))
                time.sleep(sleep_time)
#            print('Thread {} shut down.'.format(self.t_id))

    def test_read_write_lock():
        """
        Small test setup for the ReadWriteLock
        """
        threads = []
        thread_amount = 10
        for i in range(thread_amount):
            threads.append(TestThread(i))

        for i in threads:
            i.start()

        deletion_timeout = 5
        while len(threads) > 0:
            time.sleep(deletion_timeout)
            to_stop = random.choice(threads)
            to_stop.stop()
            threads.remove(to_stop)

    test_read_write_lock()
