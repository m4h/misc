# Notes
-------

## set QoS on packets with iptables

might work on networks who appreciate user end QoS. smooth network experience in overall.

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

## ssh_config - connect to private network via nat|bastion|gateway node

ssh_config content:
```
Host gateway
    HostName 1.2.3.4
    IdentityFile /home/meadow/.ssh/london.pem
    User ubuntu

Host 172.31.*
    ProxyJump gateway
    IdentityFile /home/meadow/.ssh/london.pem
    User ubuntu
```

to connect:
```
┌─berry@meadow [workspace]
└─14:52─> $ ssh 172.31.62.94
Welcome to Ubuntu 16.04.3 LTS (GNU/Linux 4.4.0-1049-aws x86_64)
...
ubuntu@ip-172-31-62-94:~$
```
