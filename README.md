# sbc_temperature_monitor

collection of temperature monitoring and stress notes/tools for SBCs like (Linux) ARM based Raspberry Pi and Rock64

## Tools

  * speedtemp.sh - (bash) shell script for monitoring CPU speed and temperature (on Raspberry Pi also includes throttling information). Relies on; vcgencmd, perl, awk, sed
  * stressmon.py - Python 2 or 3 with no external module dependecies to run `stress` and monitor temperature usage - essentially a portable/light weight version of stressberry-plot. Requires `stress`, and will use `vcgencmd` if available. Generates json log files suitable for `stress_plot.py` (below). Runs for 10 mins by default (configurable)
      * TODO log throttling information is available
      * TODO allow monitor only mode without stress
      * TODO alow alternative stress tools
      * TODO Update output with more status information (e.g. currently idling/testing, along with time-progress (to help determine finish time) to avoid scrolling back
  * stress_plot.py - python (2 or 3) script for plotting multiple json files that contain temperature readings. Generates an interactive SVG (using https://github.com/Kozea/pygal/)
      * convert_stressberry.py - can be used to convert to/from https://github.com/nschloe/stressberry format data files - also see https://github.com/clach04/stressberry/tree/rock64 and https://github.com/clach04/rock64_vcgencmd


## Running

Installing, stress_plot.py needs pygal. Known to work with Python 3.12.5 and pygal-3.0.5:

    pip install pygal

Running:

    ./stressmon.py pi3_py2.json  # needs vcgencmd (i.e. Raspbian for Raspberry Pi)

    python stressmon.py  -t /sys/class/thermal/thermal_zone0/temp -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq --cooldown 0 -n 'rock64_armbian_pi_box_lid_fan_on' rock64_armbian_pi_box_lid_fan_on.json  # should work for more devices/processors under Linux with default CPU info, e.g. armbian, DietPi, x86 Ubuntu

    env PYTHONIOENCODING=utf-8 python stressmon.py  -t /sys/class/thermal/thermal_zone0/temp -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq --cooldown 0 -n 'rock64_armbian_pi_box_lid_fan_on' rock64_armbian_pi_box_lid_fan_on.json


    ./stress_plot.py | gzip > demo.svgz

## Useful resources

  * https://github.com/ThomasKaiser/sbc-bench
  * ThomasKaiser raspimon https://github.com/bamarni/pi64/issues/4#issuecomment-315829737 (his repo with this script is no longer available)
      * https://forum.openmediavault.org/index.php/Thread/18991-New-approach-for-Raspberry-Pi-OMV-images/?postID=190184#post190184
  * https://core-electronics.com.au/tutorials/stress-testing-your-raspberry-pi.html
  * https://www.raspberrypi.org/blog/thermal-testing-raspberry-pi-4/
  * https://raspberrypi.stackexchange.com/questions/3371/how-can-i-stress-test-my-raspberry-pi
  * https://www.reddit.com/r/RASPBERRY_PI_PROJECTS/comments/8eo6om/cpu_stress_testing_on_a_rpi_temperature_data/
  * Raspberry Pi 1 http://www.roylongbottom.org.uk/Raspberry%20Pi%20Stress%20Tests.htm
      * Roy Longbottom's Raspberry Pi 2 and 3 Stress Tests http://www.roylongbottom.org.uk/Raspberry%20Pi%202%20Stress%20Tests.htm
  * https://harlemsquirrel.github.io/shell/2019/01/05/monitoring-raspberry-pi-power-and-thermal-issues.html
