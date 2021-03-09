import iptc
import netns
from random import randint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--vmport",required=True, help="ip of vm")
parser.add_argument("--newport",required=True, help="enter port vm")
parser.add_argument("--qrouter",required=True, help="gateway")
parser.add_argument("--ip",required=True, help="ipis of vm")
args = parser.parse_args()
# reduce oldport ok?

with netns.NetNS(nsname=args.qrouter):

	prerouting = iptc.easy.dump_chain('nat','custom-PREROUTING',ipv6=False)
    	mapping_ports = {}
    	router_ports = []


    	for rule in prerouting:
        	src = rule['target']['DNAT']['to-destination']
        	dport = rule['tcp']['dport']
        	# the port which router opened (vmy)
        	router_ports.append(dport)
        	# mapping the vm_port_opened with router_port_opened
        	mapping_ports[src] = dport

	if args.newport not in router_ports:
		dst = args.ip + ':' +  args.vmport
		chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-PREROUTING")
    		old_rule = iptc.Rule()
    		old_rule.protocol ="tcp"
    		match = iptc.Match(old_rule, "tcp")
    		match.dport = mapping_ports[dst] 
    		target = old_rule.create_target("DNAT")
    		target.to_destination = dst 
    		old_rule.add_match(match)
    		old_rule.target = target
    		chain.delete_rule(old_rule)	

    		new_rule = iptc.Rule()
    		new_rule.protocol ="tcp"
    		match = iptc.Match(new_rule, "tcp")
    		match.dport = args.newport 
    		target = new_rule.create_target("DNAT")
    		target.to_destination = dst 
    		new_rule.add_match(match)
    		new_rule.target = target
    		chain.insert_rule(new_rule)
	else:
		print('Used')

	
     


		
