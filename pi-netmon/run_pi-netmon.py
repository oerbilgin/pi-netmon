from multiprocessing import Process
from monitors import UptimeTest, SpeedTest


def start_uptime_monitor(interval):
    UptimeTest(servers=[
        '8.8.8.8',  # google DNS
        '8.8.4.4',  # Another google DNS
        '1.1.1.1',  # cloudflare DNS
        '139.130.4.5',  # Australia
        ]).monitor(interval)


def start_speed_monitor(interval):
    SpeedTest().monitor(interval)


def main():
    Process(
        target=start_uptime_monitor,
        args=(60,)
    ).start()

    Process(
        target=start_speed_monitor,
        args=(1740,)
    ).start()


if __name__ == '__main__':
    main()
