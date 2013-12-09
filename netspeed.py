import time

fname = '/proc/net/dev'
iface = 'eth0'

avg_sent = []
avg_recv = []

def run():
        i_recv = 0
        i_sent = 8
        b_recv = 0
        b_sent = 0

        while True:
                for line in open(fname):
                        if iface in line:
                                line = [l for l in line.split(':')[-1].split(' ') if l != '']
                                _recv = int(line[i_recv])
                                _sent = int(line[i_sent])

                                if b_recv and b_sent:
                                        r_bytes = _recv - b_recv
                                        s_bytes = _sent - b_sent
                                        print '[INFO]: RX %.2f kb/sec ; TX %.2f kb/sec' % (r_bytes/1024.0, 
s_bytes/1024.0)
                                        avg_recv.append(r_bytes)
                                        avg_sent.append(s_bytes)

                                b_recv = _recv
                                b_sent = _sent

                time.sleep(1)


if __name__ == '__main__':
        try:
                run()
        except KeyboardInterrupt:
                sum_recv = 0
                sum_sent = 0
                for s in avg_recv:
                        sum_recv += s
                for s in avg_sent:
                        sum_sent += s
                print '[INFO]: Average RX %.2f kb/sec ; TX %.2f kb/sec' % ((sum_recv/len(avg_recv))/1024.0, 
(sum_sent/len(avg_sent))/1024.0)

