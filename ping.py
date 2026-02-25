import time
import socket
import functools


class TimerError(Exception):
    pass


class Timer(object):
    def __init__(self):
        self._start_time = None
        self.elapsed_time = 0

    def __call__(self, func):
        @functools.wraps(func)
        def with_wrapper(*args, **kwargs):
            self.start()
            result = func(*args, **kwargs)
            self.stop()
            if result:
                return self.elapsed_time * 1000  # in milliseconds
            else:
                return None
        return with_wrapper

    def start(self) -> None:
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._start_time = time.perf_counter()

    def stop(self) -> None:
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        self.elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

    def __enter__(self) -> None: pass

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()


class Socket(object):
    def __init__(self, host, port, timeout):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # use TCP IP
        self.sock.settimeout(timeout)
        self.address = (host, int(port))
        self.error = None

    @Timer()
    def tcping(self) -> bool:
        try:
            self.sock.connect(self.address)
            self.sock.shutdown(socket.SHUT_RD)
            return True
        except socket.gaierror:
            self.error = "No such address"
            return False
        except socket.timeout:
            self.error = "Time out"
            return False
        except ConnectionRefusedError:
            self.error = "Connection refused"
            return False

    def close(self) -> None:
        self.sock.close()


class Ping(object):
    def __init__(self, host, port=80, count=10, timeout=1):
        self._conn_times = []
        self._error_message = []
        self.host = host
        self.port = port
        self.timeout = timeout
        self.count = count

        self.pinger()

    def _create_socket(self):
        return Socket(self.host, self.port, self.timeout)

    def pinger(self):
        for n in range(1, self.count + 1):
            s = self._create_socket()
            try:
                time.sleep(0.1)
                runtime = s.tcping()
                if runtime:
                    self._conn_times.append(runtime)
                    self._error_message.append(None)
                else:
                    self._conn_times.append(None)
                    self._error_message.append(s.error)
            finally:
                s.close()

    @property
    def bool(self):
        return all(self._conn_times)

    @property
    def max(self):
        return max([co for co in self._conn_times if co])

    @property
    def min(self):
        return min([co for co in self._conn_times if co])

    @property
    def avg(self):
        return sum([co for co in self._conn_times if co])/len(self._conn_times)

    @property
    def success(self):
        return sum([1 for conn in self._conn_times if conn])

    @property
    def false(self):
        return sum([1 for conn in self._conn_times if not conn])

    @property
    def rate(self):
        try:
            rate = (float(self.success) / self.count) * 100
        except ZeroDivisionError:
            rate = 0
        return int(rate)

    def txt(self):
        print(f"Connected to {self.host} port {self.port} :")
        for num, conn in enumerate(self._conn_times):
            if conn:
                print(f"Attempt {num + 1}: time {conn:0.2f} ms")
            else:
                print(f"Attempt {num + 1}: ", self._error_message[num])


#if __name__ == '__main__':
ping = Ping('zaya.ru', 80, 10, 1)
ping.txt()
print(ping.count)
