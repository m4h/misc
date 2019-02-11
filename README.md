# Notes
-------

## set QoS on packets with iptables

might work on networks who appreciate userend QoS. smooth network experience in overall.

change qdisc for net dev and set iptables rules
```
sudo tc qdisc add dev en0 root pfifo_fast
sudo tc qdisc del dev en0 root fd_codel
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

## connect between wireless and wired

scenario were you want to share internet with devices connected to a switch, e.g.:
  [internet] <--> [wlan0.laptop.eth0] <--> [switch] <--> [nodes]

this can be achieved by these methods:
- NAT       - all sessions going though laptop are SNATed - laptop acts much as home router 
- bridging  - bridge wireless and wired to be part of same L2 segment - laptop acts as a switch
  - briding will only work on OPEN wireless network, as NIC have to forward frames with different MAC addresses.
- routing   - networks on wireless and wired must to know each other (routing table) - laptop acts as regular network router

## run graphical applications by a user
when user is logging using Display Manager (gdm, lxdm) it is allocating a graphical session and DISPLAY for that user.
if another user wants to run a graphical app in context of that graphical session - he need to get permissions.
permissions are managed by `xhost` program.

in example below user `artyomk` is owner of graphical session and user `t0m` want to run `firefox` in a context of that session.

at first `artyomk` allow to any user from local host run graphical app.
```
┌─130artyomk@BOX [~]
└──> $ xhost +local:
non-network local connections being added to access control list
┌─artyomk@BOX [~]
└──> $ echo $DISPLAY
:1
```

after we switch to user `t0m`, specify artyomk's `DISPLAY` and run `firefox`
```
┌─artyomk@BOX [~]
└──> $ sudo su - t0m
┌─t0m@BOX [~:14]
└──> $ export DISPLAY=:1
┌─t0m@BOX [~:14]
└──> $ firefox
...
```

## artificially increase network latency

why doing it?
- because in networks is there always a "fight" between `latency` and `throughput` - by adding latency may help for network devices to cope up with high amount of packet and increase throughput.

more details are below:
```
- me asking question on a group:

During network tests (AWS) i found an interesting behavior - adding a small delay (0.5ms) on network device lead to better throughput results. Without delay 359MB/sec in avg, with delay 422MB/sec in avg (38 samples were taken).

The question is simple - why? :-)

Test was done on AWS eu-west-1c, instance type r5.2xlarge with ENA enabled, OS ubuntu 14.04.
node A and B:
- tc qdisc add dev eth0 root netem delay 0.5ms
node A:
- nc -vlp 1024 > /dev/null
node B:
- dd if=/dev/zero bs=1M count=2096 | nc -v node_A 1024

My quick suggestion - additional delay give to kernel a breath to process more packets/sec.
Will be happy to hear yours with explanation (if possible).

- answer from Avishai Ish-Shalom:
One of the general results of queuing theory is the latency/throughput tradeoff - meaning that tuning for latency hurts throughput and vice versa. Since many components in the network stack heavily rely on queueing and batching increasing latency often helps throughput, and in fact this is how schedulers work! E.g. if you look at the IO scheduler settings in linux one of the important tunables is the queue length, which improves throughput by hurting latency and gives the O/S better chance to merge IO requests, etc. Note that increasing latency in this case was done in the kernel and not in the network itself, true network latency will reduce throughput due to TCP window starvation.
```
