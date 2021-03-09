import iptc
import netns
from random import randint


with netns.NetNS(nsname='qrouter-03b72092-e8bb-473e-b671-e1dce6c4b73d'):

        prerouting_chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-PREROUTING")
        old_rule = iptc.Rule()
        old_rule.protocol ="tcp"
        match = iptc.Match(old_rule, "tcp")
        match.dport = '4022' 
        target = old_rule.create_target("DNAT")
        target.to_destination = '192.168.20.220:22' 
        old_rule.add_match(match)
        old_rule.target = target
        prerouting_chain.insert_rule(old_rule)

        postrouting_chain = iptc.Chain(iptc.Table(iptc.Table.NAT),"custom-POSTROUTING")
        new_rule = iptc.Rule()
        new_rule.protocol ="tcp"
        new_rule.dst = '192.168.20.220' 
        match = iptc.Match(new_rule, "tcp")
        match.dport = '22' 
        new_rule.add_match(match)
        new_rule.target = iptc.Target(new_rule,"MASQUERADE")
        postrouting_chain.insert_rule(new_rule)


		
