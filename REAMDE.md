# Notes
-------

## set QoS on packets with iptables

change qdisc for net dev and set iptables rules
```
sudo tc qdisc add dev en0 root pfifo_fast
sudo iptables -t mangle -A PREROUTING -j TOS --set-tos Minimize-Delay
sudo iptables -t mangle -A PREROUTING -j TOS --set-tos Maximize-Throughput
```

save it to `/etc/iptables/iptables.rules`
```
*mangle
-A PREROUTING -j TOS --set-tos Minimize-Delay
-A PREROUTING -j TOS --set-tos Maximize-Throughput
COMMIT
```

[Taken from here](https://debian-handbook.info/browse/stable/sect.quality-of-service.html)
