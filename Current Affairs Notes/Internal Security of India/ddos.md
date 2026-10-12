# Distributed denial of service and cyber resilience

## Attack and objective

- **DDoS:** distributed traffic/requests exhaust a service's bandwidth or processing resources, degrading **availability** for legitimate users.
- Compromised computers/IoT devices in **botnets** are common sources; reflection/amplification can also misuse other infrastructure. Not every source is necessarily a knowingly participating user or compromised machine.
- **DoS** can originate from one source; distributed origin complicates filtering. Floods can target network, protocol or application resources.
- DDoS does not inherently require stealing data; “never breaches security” is too absolute. A disruption may coexist with or distract from another intrusion.

## Defensive chain

- Monitor abnormal traffic →coordinate with ISP/defence provider →filter/rate-limit appropriate requests →maintain service redundancy →preserve logs and investigate.
- Capacity planning, DDoS protection, resilient load balancing, secure IoT updates and incident-response rehearsals; avoid blocking legitimate users indiscriminately.
- Government/financial services and elections depend on availability; clear public communication and recovery accountability reduce disruption. [CISA guidance](https://www.cisa.gov/sites/default/files/publications/understanding-and-responding-to-ddos-attacks_508c.pdf).

## PDF coverage

2025-02-18: pp. 19
