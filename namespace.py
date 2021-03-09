import iptc
import netns
from random import randint

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--server",required=True, help="ip of vm")
parser.add_argument("--qrouter",required=True, help="router namespace")
parser.add_argument("--vmport",required=True, help="enter port vm")
#parser.add_argument("--interface",required=True, help="interface")
parser.add_argument("--gateway",required=True, help="gateway")
args = parser.parse_args()

with netns.NetNS(nsname=args.qrouter):
    prerouting = iptc.easy.dump_chain('nat','custom-PREROUTING',ipv6=False)
    postrouting = iptc.easy.dump_chain('nat','custom-POSTROUTING',ipv6=False)
    vm_ports = {}
    mapping_ports = {}
    router_ports = []

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

	# ports which router opened
        router_ports.append(dport)
	# mapping the vm_ports with router_ports
        mapping_ports[src] = dport
    
    if ( args.server in vm_ports ) and (args.vmport in vm_ports[args.server]):
	
	mapping = '{}:{}'.format(args.server,args.vmport)
        print('server:{} with port {} mapped with router port {}').format(args.server,args.vmport,mapping_ports[mapping])

    else:
	port = str(randint(4000,4100))
	# check len router_ports if full will make error
        while port in router_ports:
        	port = str(randint(4000,4100))
	dst = args.server + ':' +  args.vmport
        prerouting_chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-PREROUTING")
        old_rule = iptc.Rule()
        old_rule.protocol ="tcp"
        match = iptc.Match(old_rule, "tcp")
        match.dport = port 
        target = old_rule.create_target("DNAT")
        target.to_destination = dst
        old_rule.add_match(match)
        old_rule.target = target
        prerouting_chain.insert_rule(old_rule)

        postrouting_chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-POSTROUTING")
        new_rule = iptc.Rule()
        new_rule.protocol ="tcp"
        new_rule.dst = args.server
        match = iptc.Match(new_rule, "tcp")
        match.dport = args.vmport
        new_rule.add_match(match)
        new_rule.target = iptc.Target(new_rule,"MASQUERADE")
        postrouting_chain.insert_rule(new_rule)
        print('Success create server:{}:{} mapping with router port {}').format(args.server,args.vmport,port)

     


		
