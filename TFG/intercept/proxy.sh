#!/bin/bash


function help {
	echo "Intercept traffic from a specified apk. Usage:"
	echo
	echo "	proxy.sh [-h] [-i <target ip>] [-a <target apk>] [-s <script to load in Frida>]"
	echo
}

function network_redirect {
	# Enable IP forwarding
	sudo sysctl -w net.ipv4.ip_forward=1
	sudo sysctl -w net.ipv6.conf.all.forwarding=1

	# Disable ICMP redirects
	sudo sysctl -w net.ipv4.conf.all.send_redirects=0

	# Redirect traffic
	sudo iptables -t nat -A PREROUTING -i eth1 -p tcp -j REDIRECT --to-port 8080
	sudo iptables -t nat -A PREROUTING -i eth1 -p tcp -j REDIRECT --to-port 8080
	sudo ip6tables -t nat -A PREROUTING -i eth1 -p tcp -j REDIRECT --to-port 8080
	sudo ip6tables -t nat -A PREROUTING -i eth1 -p tcp -j REDIRECT --to-port 8080
}

function run_adb {
	# Starting adb as root
	adb connect $1
	adb root
	adb connect $1

	# Install apk
	adb install -r $2
	xfce4-terminal -e 'adb shell "/data/local/frida &"'

	# Run monkey
	read -p "Do you want to run Frida? [N/y] " answer
	if [ "$answer" == "y" -o "$answer" == "Y" ]; then
		echo "frida -U -l $4 -f $3 --no-pause"
		frida -U -l $4 -f $3 --no-pause
	fi
}

function run_mitmproxy {
	#Run proxy in another terminal
	xfce4-terminal -e "mitmdump -s ./inspect_requests.py --set app=$1"
}

unset apk
while getopts "n:a:i:s:h" options;
do
	case "${options}" in
		h)
			help
			exit 0
			;;
		i)
			ip=${OPTARG}
			;;
		a)
			apk=${OPTARG}
			eval $(aapt dump badging $apk | grep "package: name" | awk '{print $2}')
			;;
		s)
			script=${OPTARG}
			;;
		*)
			echo "Nope"
			;;
	esac
done
if [ -z "$apk" ]
then
	help
	exit 0
fi

run_mitmproxy $name &

network_redirect
run_adb $ip $apk $name $script 
