__author__ = 'Grp10'

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import time
# from ShortestPath import ProjectController
# from Q4 import ProjectController
# from time import time
from linkcost import MyController
from ryu.topology import event
# Below is the library used for topo discovery
from ryu.topology.api import get_switch, get_link, get_host
import copy

# from path_discovery import PathDiscovery

# from topostructure import TopoStructure
try:
    f1 = open('info.txt', 'r')
    lines = f1.readlines()

except Exception as e:
    print('Error:', e)
    exit()

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        self.output_printed = False
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        # USed for learning switch functioning
        self.mac_to_port = {}
        # Holds the topology data and structure
        # self.topo_shape = TopoStructure()
        #shortest path
        # self.path_discovery = PathDiscovery(self)
        # Holds the topology data and structure
        self.topo_raw_switches = []
        self.topo_raw_links = []
        self.topo_raw_hosts = []
        self.flows = {}

        self.num_s = int(lines[0].split()[0])
        self.num_h = int(lines[0].split()[1])
        # hardcoded link costs
        for i in range(1, self.num_s + 1):
            self.flows[i] = []
        
        self.pathinfo = [[{'cost': 0, 'dl': 0, 'bw': 0}] * self.num_s for _ in range(self.num_s)]
        self.adj = [[0]*self.num_s for _ in range(self.num_s)] # contains all costs

        # Initialize costs
        for i in range(1,len(lines)):
            l = lines[i].split()
            if l[0][0] == 'S' and l[1][0] == 'S':
                a, b = int(l[0][1:]) - 1, int(l[1][1:]) - 1
                dl, bw = int(l[3]), int(l[2])
                self.pathinfo[a][b] = {'cost': dl/bw, 'dl': dl, 'bw': bw}
                self.pathinfo[b][a] = {'cost': dl/bw, 'dl': dl, 'bw': bw}

                self.adj[a][b] = dl/bw
                self.adj[b][a] = dl/bw

        print("Link costs...")

        # Print costs
        for i in range(len(self.adj)):
            for j in range(len(self.adj[i])):
                if i!=j:
                    if self.adj[i][j]==0:
                        print("switch",i+1,"- switch",j+1,": ",-1)
                    else:
                        print("switch",i+1,"- switch",j+1,": ",self.adj[i][j])

        
    

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        self.logger.info('OFPSwitchFeatures received: '
                         '\n\tdatapath_id=0x%016x n_buffers=%d '
                         '\n\tn_tables=%d auxiliary_id=%d '
                         '\n\tcapabilities=0x%08x',
                         msg.datapath_id, msg.n_buffers, msg.n_tables,
                         msg.auxiliary_id, msg.capabilities)

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    # We are not using this function
    def delete_flow(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        for dst in self.mac_to_port[datapath.id].keys():
            match = parser.OFPMatch(eth_dst=dst)
            mod = parser.OFPFlowMod(
                datapath, command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
                priority=1, match=match)
            datapath.send_msg(mod)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    """
    This is called when Ryu receives an OpenFlow packet_in message. The trick is set_ev_cls decorator. This decorator
    tells Ryu when the decorated function should be called.
    """
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # self.logger.info("\tpacket in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    ###################################################################################
    """
    The event EventSwitchEnter will trigger the activation of get_topology_data().
    """
    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        # Delay for 5 seconds
        # time.sleep(5)
        # The Function get_switch(self, None) outputs the list of switches.
        self.topo_raw_switches = copy.copy(get_switch(self, None))
        # The Function get_link(self, None) outputs the list of links.
        self.topo_raw_links = copy.copy(get_link(self, None))
        #The Function get_host(self) outputs hosts.
        self.topo_raw_hosts = copy.copy(get_host(self,None))
        
        """
        Now you have saved the links and switches of the topo. So you could do all sort of stuf with them. 
        """
        if not self.output_printed:
            print(" \t" + "Current Links:")
            for l in self.topo_raw_links:
                print (" \t\t" + str(l))

            print(" \t" + "Current Links between host and switches:")
            for h in self.topo_raw_hosts:
                print ("\t\t" + str(h.mac) + " connected to switch " + str(h.port.dpid))

            print(" \t" + "Current Switches:")
            for s in self.topo_raw_switches:
                print (" \t\t" + str(s.dp.id))
            
            # link cost method implemented
            # obj = MyController(app_manager.RyuApp)
            # obj.get_topology_data(ev)

            # print(" \t" + "Current Hosts:")
            # for h in self.topo_raw_hosts:
            #     print (" \t\t" + str(h))
            # time.sleep(10)
            # obj = ProjectController(app_manager.RyuApp)
            # obj.get_topology_data(ev)
            # obj._packet_in_handler( ev)
            # self.output_printed = True
    """
    This event is fired when a switch leaves the topo. i.e. fails.
    """
    @set_ev_cls(event.EventSwitchLeave, [MAIN_DISPATCHER, CONFIG_DISPATCHER, DEAD_DISPATCHER])
    def handler_switch_leave(self, ev):
        self.logger.info("Not tracking Switches, switch leaved.")


