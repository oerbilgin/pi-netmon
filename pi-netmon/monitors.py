import speedtest
import subprocess
import re
from abc import ABC, abstractmethod
from time import sleep
import os
import datetime


LOGFILE_PATH = os.path.expanduser('~/.logs')
UPTIME_LOGFILE = 'uptime.log'
SPEED_LOGFILE = 'netspeed.log'


def _init_logdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


class AbstractTest(ABC):
    """
    Abstract Base Class of a network test.

    Can run a single test, and also continually monitor.

    The following methods must be overwritten:
    * run_test: The method that runs the test
    * store_results: A method to store (or simply print)
      the results of the test.
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def run_test(self):
        """Performs the test"""
        pass

    @abstractmethod
    def store_results(self):
        """Stores the results of the last test."""
        pass

    def monitor(self, test_interval):
        """
        Begins monitoring.

        Runs each test of the monitor at the specified interval,
        and logs the results as specified.

        Args:
            test_interval (int): Interval between tests, in seconds.
        """
        while True:
            self.run_test()
            self.store_results()
            sleep(test_interval)


class SpeedTest(AbstractTest):
    def __init__(self):
        super().__init__()
        self.speed_test = speedtest.Speedtest()

    def run_test(self):
        self.speed_test.get_best_server()
        self.speed_test.download()
        self.speed_test.upload()
        self._results_dict = self.speed_test.results.dict()

    def store_results(self):
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        with open(os.path.join(LOGFILE_PATH, SPEED_LOGFILE), 'a') as f:
            f.write(
                f"{{'time': {now}, "
                f"'ping_time_ms': {self.ping_time:.3f}, "
                f"'download_speed_Mbps': {self.download_speed:.3f}, "
                f"'upload_speed_Mbps': {self.upload_speed:.3f}}},\n"
            )

    @property
    def download_speed(self):
        """Download speed in Megabits per second"""
        return self._results_dict['download'] / 1e6

    @property
    def upload_speed(self):
        """Upload speed in Megabits per second"""
        return self._results_dict['upload'] / 1e6

    @property
    def ping_time(self):
        """Ping time in seconds"""
        return self._results_dict['ping']


class UptimeTest(AbstractTest):
    def __init__(self, servers=['8.8.8.8']):
        super().__init__()
        self.servers = servers

    def run_test(self):
        self.ping_responses = []
        for server in self.servers:
            resp = str(subprocess.Popen(
                ["/bin/ping", "-c1", "-W1", server],
                stdout=subprocess.PIPE).stdout.read())
            self.ping_responses.append(resp)

    def store_results(self):
        _init_logdir(LOGFILE_PATH)
        now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        with open(os.path.join(LOGFILE_PATH, UPTIME_LOGFILE), 'a') as f:
            f.write(
                f"{{'time': {now}, "
                f"'mean_ping_time_ms': {self.mean_ping_time:.3f}, "
                f"'ping_success_rate': {self.ping_success_rate}}},\n"
            )

    @property
    def ping_times(self):
        # regex to get the ping times
        ping_times = [
            re.findall(r'time=([0-9]*\.?[0-9]+)', x)
            for x in self.ping_responses
        ]
        return [float(x[0]) for x in ping_times if len(x) != 0]

    @property
    def ping_success_rate(self):
        return len(self.ping_times) / len(self.servers)

    @property
    def mean_ping_time(self):
        return sum(self.ping_times) / len(self.ping_times)


def main():
    # s = SpeedTest()
    # s.run_test()
    # s.store_results()

    UptimeTest(servers=[
        '8.8.8.8',  # google DNS
        '8.8.4.4',  # Another google DNS
        '1.1.1.1',  # cloudflare DNS
        '139.130.4.5',  # Australia
        ]).monitor(test_interval=3)


if __name__ == '__main__':
    main()
