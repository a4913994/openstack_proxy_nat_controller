import iptc
import netns
from random import randint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--vmport",required=False, help="ip of vm")
parser.add_argument("--newport",required=False, help="enter port vm")
parser.add_argument("--qrouter",required=True, help="gateway")
parser.add_argument("--ip",required=True, help="ipis of vm")
args = parser.parse_args()

with netns.NetNS(nsname=args.qrouter):

	prerouting = iptc.easy.dump_chain('nat','custom-PREROUTING',ipv6=False)
	postrouting = iptc.easy.dump_chain('nat','custom-POSTROUTING',ipv6=False)
    	mapping_ports = {}
    	router_ports = []
	vm_ports = {}
	# ports which vm opened
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
	if args.ip not in vm_ports:
		print('vm has no port to modify')
	elif args.vmport not in vm_ports[args.ip]:
		print('vm port has not opened yet')
	elif args.newport not in router_ports:
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
		print('Success modify')
	else:
		for key, value in mapping_ports.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
    			if value == args.newport:
				print('Port you want open is used. Detailed:{}-->{}\nPlease check in option 6: Show port mapping to see available router ports').format(key,value)

	
     


		
