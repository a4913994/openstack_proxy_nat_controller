import iptc
import netns
from random import randint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--vmport",required=True, help="ip of vm")
parser.add_argument("--qrouter",required=True, help="gateway")
parser.add_argument("--ip",required=True, help="ipis of vm")
args = parser.parse_args()
# reduce oldport ok?

with netns.NetNS(nsname=args.qrouter):

	prerouting = iptc.easy.dump_chain('nat','custom-PREROUTING',ipv6=False)
	postrouting = iptc.easy.dump_chain('nat','custom-POSTROUTING',ipv6=False)
    	mapping_ports = {}
    	router_ports = []
    	vm_ports = {}

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

        	# mapping the vm_port_opened with router_port_opened
        	mapping_ports[src] = dport

	if (args.ip in vm_ports) and (args.vmport in vm_ports[args.ip]) :
		dst = args.ip + ':' +  args.vmport
		prerouting_chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-PREROUTING")
    		old_rule = iptc.Rule()
    		old_rule.protocol ="tcp"
    		match = iptc.Match(old_rule, "tcp")
    		match.dport = mapping_ports[dst] 
    		target = old_rule.create_target("DNAT")
    		target.to_destination = dst 
    		old_rule.add_match(match)
    		old_rule.target = target
    		prerouting_chain.delete_rule(old_rule)	

		postrouting_chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-POSTROUTING")
    		new_rule = iptc.Rule()
    		new_rule.protocol ="tcp"
		new_rule.dst = args.ip
    		match = iptc.Match(new_rule, "tcp")
    		match.dport = args.vmport 
    		new_rule.add_match(match)
    		new_rule.target = iptc.Target(new_rule,"MASQUERADE") 
    		postrouting_chain.delete_rule(new_rule)
		print('Success')
	else:
		print('Not Used')

	
     


		
