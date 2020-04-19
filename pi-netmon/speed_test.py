import speedtest


class SpeedTest():
    def __init__(self):
        self.speed_test = speedtest.Speedtest()

    def run_test(self):
        self.speed_test.get_best_server()
        self.speed_test.download()
        self.speed_test.upload()
        self._results_dict = self.speed_test.results.dict()

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


def main():
    s = SpeedTest()
    s.run_test()
    print(s.ping_time, s.upload_speed, s.download_speed)


if __name__ == '__main__':
    main()
