#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#

import argparse
import datetime
import sys
import threading
import time

import json

__copyright__ = "Copyright (c) 2017-2019, Nico Schloemer, Chris Clark"
__version__ = "0.2.2"

import subprocess
import time as tme
from os import cpu_count


def stress_cpu(num_cpus, time):
    subprocess.check_call(
        ["stress", "--cpu", str(num_cpus), "--timeout", "{}s".format(time)]
    )
    return


def cooldown(interval=60, filename=None):
    """Lets the CPU cool down until the temperature does not change anymore.
    """
    prev_tmp = measure_temp(filename=filename)
    while True:
        tme.sleep(interval)
        tmp = measure_temp(filename=filename)
        print(
            "Current temperature: {:4.1f}'C - Previous temperature: {:4.1f}'C".format(
                tmp, prev_tmp
            )
        )
        if abs(tmp - prev_tmp) < 0.2:
            break
        prev_tmp = tmp
    return tmp


def measure_temp(filename=None):
    """Returns the core temperature in Celsius.
    """
    if filename is not None:
        with open(filename, "r") as f:
            temp = float(f.read()) / 1000
    else:
        # Using vcgencmd is specific to the raspberry pi
        out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        temp = float(out.replace("temp=", "").replace("'C", ""))
    return temp


def measure_core_frequency(filename=None):
    """Returns the CPU frequency in MHz
    """
    if filename is not None:
        with open(filename, "r") as f:
            frequency = float(f.read()) / 1000
    else:
        # Only vcgencmd measure_clock arm is accurate on Raspberry Pi.
        # Per: https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=219358&start=25
        out = subprocess.check_output(["vcgencmd", "measure_clock arm"]).decode("utf-8")
        frequency = float(out.split("=")[1]) / 1000000
    return frequency


def measure_ambient_temperature(sensor_type="2302", pin="23"):
    """Uses Adafruit temperature sensor to measure ambient temperature
    """
    try:
        import Adafruit_DHT  # Late import so that library is only needed if requested
    except ImportError as e:
        print("Install adafruit_dht python module: pip --user install Adafruit_DHT")
        raise e

    sensor_map = {
        "11": Adafruit_DHT.DHT11,
        "22": Adafruit_DHT.DHT22,
        "2302": Adafruit_DHT.AM2302,
    }
    try:
        sensor = sensor_map[sensor_type]
    except KeyError as e:
        print("Invalid ambient temperature sensor")
        raise e
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    # Note that sometimes you won't get a reading and the results will be null
    # (because Linux can't guarantee the timing of calls to read the sensor).
    # The read_retry call will attempt to read the sensor 15 times with a 2 second delay.
    # Care should be taken when reading if on a time sensitive path
    # Temperature is in 'C but can also be None
    return temperature


def test(stress_duration, idle_duration, cores):
    """Run stress test for specified duration with specified idle times
       at the start and end of the test.
    """
    if cores is None:
        cores = cpu_count()

    print(
        "Preparing to stress [{}] CPU Cores for [{}] seconds".format(
            cores, stress_duration
        )
    )
    print("Idling for {} seconds...".format(idle_duration))
    tme.sleep(idle_duration)

    stress_cpu(num_cpus=cores, time=stress_duration)

    print("Idling for {} seconds...".format(idle_duration))
    tme.sleep(idle_duration)
    return

def _get_version_text():
    return "\n".join(
        [
            "stressberry {} [Python {}.{}.{}]".format(
                __version__,
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            ),
            __copyright__,
        ]
    )


def _get_parser_run():
    parser = argparse.ArgumentParser(
        description="Run stress test for the Raspberry Pi."
    )
    parser.add_argument(
        "--version", "-v", action="version", version=_get_version_text()
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        default="stressberry data",
        help="name the data set (default: 'stressberry data')",
    )
    parser.add_argument(
        "-t",
        "--temperature-file",
        type=str,
        default=None,
        help="temperature file e.g /sys/class/thermal/thermal_zone0/temp (default: vcgencmd)",
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=int,
        default=600,
        help="stress test duration in seconds (default: 600 - 10 mins)",
    )
    parser.add_argument(
        "-i",
        "--idle",
        type=int,
        default=150,
        help="idle time in seconds at start and end of stress test (default: 150)",
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=60,
        help="poll interval seconds to check for stable temperature (default: 60)",
    )
    parser.add_argument(
        "-c",
        "--cores",
        type=int,
        default=None,
        help="number of CPU cores to stress (default: all)",
    )
    parser.add_argument(
        "-f",
        "--frequency-file",
        type=str,
        default=None,
        help="CPU core frequency file e.g. /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq (default: vcgencmd)",
    )
    parser.add_argument(
        "-a",
        "--ambient",
        type=str,
        nargs=2,
        default=None,
        help="measure ambient temperature. Sensor Type [11|22|2302] <GPIO Number> e.g. 2302 26",
    )
    parser.add_argument("outfile", type=argparse.FileType("w"), help="output data file")
    return parser


def run(argv=None):
    parser = _get_parser_run()
    args = parser.parse_args(argv)

    # Cool down first
    print("Awaiting stable baseline temperature...")
    cooldown(interval=args.cooldown, filename=args.temperature_file)

    # Start the stress test in another thread
    t = threading.Thread(
        target=lambda: test(args.duration, args.idle, args.cores), args=()
    )
    t.start()

    times = []
    temps = []
    freqs = []
    ambient = []
    while t.is_alive():
        times.append(time.time())
        temps.append(measure_temp(args.temperature_file))
        freqs.append(measure_core_frequency(args.frequency_file))
        if args.ambient:
            ambient_temperature = measure_ambient_temperature(
                sensor_type=args.ambient[0], pin=args.ambient[1]
            )
            if ambient_temperature is None:
                # Reading the sensor can return None if it times out.
                # If never had a good result, probably configuration error
                # Else use last known value if available or worst case set to zero
                if not ambient:
                    message = "Could not read ambient temperature sensor {} on pin {}".format(
                        args.ambient[0], args.ambient[1]
                    )
                else:
                    message = "WARN - Could not read ambient temperature, using last good value"
                print(message)
                ambient_temperature = next(
                    (temp for temp in reversed(ambient) if temp is not None), 0
                )
            ambient.append(ambient_temperature)
            delta_t = temps[-1] - ambient[-1]
            print(
                "Temperature (current | ambient | dT): {:4.1f}'C | {:4.1f}'C | {:4.1f}'C - Frequency: {:4.0f}MHz".format(
                    temps[-1], ambient[-1], delta_t, freqs[-1]
                )
            )
        else:
            print(
                "Current temperature: {:4.1f}'C - Frequency: {:4.0f}MHz".format(
                    temps[-1], freqs[-1]
                )
            )
        # Choose the sample interval such that we have a respectable number of
        # data points
        t.join(2.0)

    # normalize times
    time0 = times[0]
    times = [tm - time0 for tm in times]

    version_comment = "# This file was created by stressberry v{} on {}\n".format(
            __version__, datetime.datetime.now()
        )
    #args.outfile.write(
    json.dump(
        {
            "name": args.name,
            "time": times,
            "temperature": temps,
            "cpu frequency": freqs,
            "ambient": ambient,
            "version_comment": version_comment,
        },
        args.outfile,
    )
    return

def main(argv=None):
    if argv is None:
        argv = sys.argv

    run(argv)

    return 0


if __name__ == "__main__":
    sys.exit(main())

