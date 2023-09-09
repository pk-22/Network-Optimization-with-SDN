from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel,info
from random import randint
import sys

class CustomTopology(Topo):
    def build(self):
        # Add switches
        root = self.addSwitch('s1')

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Add links

        self.addLink(root, h1, bw=50, delay=f'{randint(1,5)}ms')
        self.addLink(root, h2, bw=50, delay=f'{randint(1,5)}ms')


topos = { 'custom': ( lambda: CustomTopology())  }

if __name__ == '__main__':
    topo = CustomTopology()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    CLI(net)

    net.stop()

