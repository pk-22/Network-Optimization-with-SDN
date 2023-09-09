from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel,info
from random import randint
import sys

class CustomTopology(Topo):
    allowed_macs = ['00:00:00:00:00:01', '00:00:00:00:00:02', '00:00:00:00:00:03', '00:00:00:00:00:04', '00:00:00:00:00:05', '00:00:00:00:00:06', '00:00:00:00:00:07', '00:00:00:00:00:08', '00:00:00:00:00:09', '00:00:00:00:00:0A']
    def build(self):
        # Add switches
        root = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        # Add hosts
        h1_mac = '00:00:00:00:00:01'
        if h1_mac in self.allowed_macs:
            h1 = self.addHost('h1', mac=h1_mac)
        h2_mac = '00:00:00:00:00:02'
        if h2_mac in self.allowed_macs:
            h2 = self.addHost('h2', mac=h2_mac)
        h3_mac = '00:00:00:00:00:03'
        if h3_mac in self.allowed_macs:
            h3 = self.addHost('h3', mac=h3_mac)
        h4_mac = '00:00:00:00:00:04'
        if h4_mac in self.allowed_macs:
            h4 = self.addHost('h4', mac=h4_mac)
        h5_mac = '00:00:00:00:00:05'
        if h5_mac in self.allowed_macs:
            h5 = self.addHost('h5', mac=h5_mac)
        h6_mac = '00:00:00:00:00:06'
        if h6_mac in self.allowed_macs:
            h6 = self.addHost('h6', mac=h6_mac)
        h7_mac = '00:00:00:00:00:07'
        if h7_mac in self.allowed_macs:
            h7 = self.addHost('h7', mac=h7_mac)
        h8_mac = '00:00:00:00:00:08'
        if h8_mac in self.allowed_macs:
            h8 = self.addHost('h8', mac=h8_mac)
        h9_mac = '00:00:00:00:00:09'
        if h9_mac in self.allowed_macs:
            h9 = self.addHost('h9', mac=h9_mac)
        h10_mac = '00:00:00:00:00:0A'
        if h10_mac in self.allowed_macs:
            h10 = self.addHost('h10', mac=h10_mac)

        # Add links
        self.addLink(root, s2, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(root, s3, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(root, s4, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(root, s5, bw=50, delay=f'{randint(1,5)}ms')

        self.addLink(s2, h1, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(s2, h2, bw=50, delay=f'{randint(1,5)}ms')

        self.addLink(s3, h3, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(s3, h4, bw=50, delay=f'{randint(1,5)}ms')

        self.addLink(s4, h5, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(s4, h6, bw=50, delay=f'{randint(1,5)}ms')

        self.addLink(s5, h7, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(s5, h8, bw=50, delay=f'{randint(1,5)}ms')

        self.addLink(root, s6, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(s6, h9, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(s6, h10, bw=50, delay=f'{randint(1,5)}ms')

topos = { 'custom': ( lambda: CustomTopology())  }

if __name__ == '__main__':
    topo = CustomTopology()
    net = Mininet(topo=topo, link=TCLink)
    
    net.start()

    # Add MAC address to Hosts
    # h1, h2, h3, h4, h5, h6, h7, h8, h9, h10 = net.get('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10')
    # h1.setMAC('00:00:00:00:00:01')
    # h2.setMAC('00:00:00:00:00:02')
    # h3.setMAC('00:00:00:00:00:03')
    # h4.setMAC('00:00:00:00:00:04')
    # h5.setMAC('00:00:00:00:00:05')
    # h6.setMAC('00:00:00:00:00:06')
    # h7.setMAC('00:00:00:00:00:07')
    # h8.setMAC('00:00:00:00:00:08')
    # h9.setMAC('00:00:00:00:00:09')
    # h10.setMAC('00:00:00:00:00:0A')

    CLI(net)

    net.stop()


