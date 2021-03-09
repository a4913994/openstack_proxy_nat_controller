import iptc
import netns
from random import randint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--server",required=True, help="ip vm")
parser.add_argument("--qrouter",required=True, help="router namespace")
args = parser.parse_args()


with netns.NetNS(nsname=args.qrouter):
    prerouting = iptc.easy.dump_chain('nat','custom-PREROUTING',ipv6=False)
    postrouting = iptc.easy.dump_chain('nat','custom-POSTROUTING',ipv6=False)
    vm_ports = {}
    mapping_ports = {}
    router_ports = []

    # list vm_port which vm opened (vms)
    for rule in postrouting:
        dst = rule['dst']
        dst = dst[:-3]
        if dst in vm_ports:
                vm_ports[dst].append(rule['tcp']['dport'])
        else:
                vm_ports[dst] = []
                vm_ports[dst].append(rule['tcp']['dport'])

    for rule in prerouting:
        src = rule['target']['DNAT']['to-destination']
        dport = rule['tcp']['dport']

	# the port which router opened (vmy)
        router_ports.append(dport)
	# mapping the vm_port_opened with router_port_opened
        mapping_ports[src] = dport

    result = '' 
    if args.server in vm_ports:
    	for i in vm_ports[args.server]:
    		s = '{}:{}'.format(args.server,i)
		text = 'Port:{}-->{}\n'.format(s,mapping_ports[s])
		result = result + text
    print(result)

     


		
