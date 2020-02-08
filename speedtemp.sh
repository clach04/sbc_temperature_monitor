#!/bin/bash
# from https://github.com/bamarni/pi64/issues/4#issuecomment-315829737
#
# Rasperry Pi Health script. (c) 2017 by tkaiser (Thomas Kaiser)
#
# Initial version and some more information can be found here:
# https://github.com/bamarni/pi64/issues/4#issuecomment-292707581

show_throttle_key_tail()
{
cat <<EOF
                              ||||             ||||
                              ||||             ||||_ under-voltage
                              ||||             |||_ currently throttled
                              ||||             ||_ arm frequency capped
                              ||||             |_ soft temperature reached
                              ||||_ under-voltage has occurred since last reboot
                              |||_ throttling has occurred since last reboot
                              ||_ arm frequency capped has occurred since last reboot
                              |_ soft temperature reached since last reboot
EOF
}

show_throttle_key_mirror()
{
cat <<EOF
                              |_ soft temperature reached since last reboot
                              ||_ arm frequency capped has occurred since last reboot
                              |||_ throttling has occurred since last reboot
                              ||||_ under-voltage has occurred since last reboot
                              ||||             |_ soft temperature reached
                              ||||             ||_ arm frequency capped
                              ||||             |||_ currently throttled
                              ||||             ||||_ under-voltage
EOF
}

show_throttle_key_head()
{
cat <<EOF
                              +- soft temperature reached since last reboot
                              |+- arm frequency capped has occurred since last reboot
                              ||+- throttling has occurred since last reboot
                              |||+- under-voltage has occurred since last reboot
                              ||||             +- soft temperature reached
                              ||||             |+- arm frequency capped
                              ||||             ||+- currently throttled
                              ||||             |||+- under-voltage
                              ||||             ||||
EOF
}

trap "show_throttle_key_tail" EXIT

echo -e "To stop simply press [ctrl]-[c]\n"
Maxfreq=$(( $(awk '{printf ("%0.0f",$1/1000); }'  </sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq) -15 ))
Counter=0
DisplayHeader="Time       Temp  CPU fake/real     Health state    Vcore"
echo -e "${DisplayHeader}"
show_throttle_key_head
while true ; do
   let Counter++
   if [ ${Counter} -eq 15 ]; then
       echo -e "${DisplayHeader}"
       Counter=0
   fi
   Health=$(perl -e "printf \"%21b\n\", $(vcgencmd get_throttled | cut -f2 -d=)")
   Temp=$(vcgencmd measure_temp | cut -f2 -d=)
   RealClockspeed=$(vcgencmd measure_clock arm | awk -F"=" '{printf ("%0.0f",$2/1000000); }' )
   SysFSClockspeed=$(awk '{printf ("%0.0f",$1/1000); }' </sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
   CoreVoltage=$(vcgencmd measure_volts | cut -f2 -d= | sed 's/000//')
   echo -e "$(date "+%H:%M:%S") ${Temp}$(printf "%5s" ${SysFSClockspeed})/$(printf "%4s" ${RealClockspeed}) MHz $(printf "%021d" ${Health}) ${CoreVoltage}"
   sleep 5 
done
