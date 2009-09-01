#import array, fcntl, struct, socket

import os,sys,re,platform



windows_output1 = """
Windows IP Configuration


Ethernet adapter Network Bridge (Network Bridge):

        Connection-specific DNS Suffix  . :
        IP Address. . . . . . . . . . . . : 192.168.0.10
        Subnet Mask . . . . . . . . . . . : 255.255.255.0
        Default Gateway . . . . . . . . . : 192.168.0.1
"""

class IfConfigWindows:
    """
    """

    def _read_ipconfig(self):
        p = os.popen("ipconfig")
        address = p.read()
        p.close()

        return address

    def get_info(self, the_output = None):
        if the_output == None:
            output = self._read_ipconfig()
        else:
            output = the_output
        
        lines = output.split("\n")

        ip_addresses = []
        subnet_masks = []
        default_gateway = []
        
        for l in lines:
            if "IP Address" in l:
                parts = l.split(":")
                ip_addr = parts[1].strip()
                ip_addresses.append(ip_addr)
            elif "Subnet Mask" in l:
                parts = l.split(":")
                ip_addr = parts[1].strip()
                subnet_masks.append(ip_addr)
            elif "Default Gateway" in l:
                parts = l.split(":")
                ip_addr = parts[1].strip()
                default_gateway.append(ip_addr)
                
        return [ip_addresses, subnet_masks, default_gateway]

    def get_ips(self, the_output = None):
        return self.get_info(the_output)[0]

    def get_subnet_masks(self, the_output = None):
        return self.get_info(the_output)[1]

    def get_default_gateways(self, the_output = None):
        return self.get_info(the_output)[2]



linux_output2 = """eth0      Link encap:Ethernet  HWaddr 00:0C:76:41:D5:E1
          inet addr:64.251.25.208  Bcast:64.251.25.255  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:24222107 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1693415 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:2578326033 (2.4 GiB)  TX bytes:287660600 (274.3 MiB)
          Interrupt:23 Base address:0xe400

eth0:1    Link encap:Ethernet  HWaddr 00:0C:76:41:D5:E1
          inet addr:64.251.25.209  Bcast:64.255.255.255  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          Interrupt:23 Base address:0xe400

eth0:2    Link encap:Ethernet  HWaddr 00:0C:76:41:D5:E1
          inet addr:64.251.25.210  Bcast:64.255.255.255  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          Interrupt:23 Base address:0xe400

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:407668 errors:0 dropped:0 overruns:0 frame:0
          TX packets:407668 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:35240368 (33.6 MiB)  TX bytes:35240368 (33.6 MiB)
"""

linux_output1 = """eth0      Link encap:Ethernet  HWaddr 00:E0:81:23:7D:3A
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:92494052 errors:0 dropped:0 overruns:0 frame:0
          TX packets:106532110 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:1940058549 (1850.1 Mb)  TX bytes:657317003 (626.8 Mb)
          Interrupt:11

eth0:py3d Link encap:Ethernet  HWaddr 00:E0:81:23:7D:3A
          inet addr:209.135.140.56  Bcast:209.135.140.255  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          Interrupt:11

lo        Link encap:Local Loopback
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:9500783 errors:0 dropped:0 overruns:0 frame:0
          TX packets:9500783 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:3537945659 (3374.0 Mb)  TX bytes:3537945659 (3374.0 Mb)
"""


class IfConfigLinux:

    def get_ips(self):

        output = p.read()
        print output
        p.close()

    def _read_ipconfig(self):
        p = os.popen("/sbin/ifconfig")

        output = p.read()
        p.close()

        return output


    def get_info(self, the_output = None):

        if the_output == None:
            output = self._read_ipconfig()
        else:
            output = the_output

        inet_regex = re.compile(r".*addr:(.*?)\s*[Bcast|Mask].*")
        
        lines = output.split("\n")

        ip_addresses = []
        subnet_masks = []
        default_gateway = []

        info = {}
        info['ip_addresses'] = []

        
        for l in lines:
            if "inet" in l:
                print l
                info['ip_addresses'].append(inet_regex.match(l).groups()[0])
                
                
        return info

    def get_ips(self, the_output = None):
        return self.get_info(the_output)['ip_addresses']



# freebsd ifconfig output.
"""fxp0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> mtu 1500
        inet 207.142.132.145 netmask 0xffffff00 broadcast 207.142.132.255
        inet 207.142.132.146 netmask 0xffffffff broadcast 207.142.132.146
        inet 207.142.132.147 netmask 0xffffffff broadcast 207.142.132.147
        inet 207.142.132.148 netmask 0xffffffff broadcast 207.142.132.148
        inet 207.142.132.149 netmask 0xffffffff broadcast 207.142.132.149
        ether 00:07:e9:08:d7:7c
        media: Ethernet autoselect (100baseTX <full-duplex>)
        status: active
lp0: flags=8810<POINTOPOINT,SIMPLEX,MULTICAST> mtu 1500
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
        inet 127.0.0.1 netmask 0xff000000
"""


class IfConfigFreeBSD:

    def get_info(self):
        raise NotImplementedError

        output = self._read_ipconfig()

        lines = output.split("\n")

        # keyed by interface name, valued by dicts containing various.
        interfaces = {}

        ip_addresses = []
        subnet_masks = []
        default_gateway = []
        
        for l in lines:
            if "inet" in l:
                
                parts = l.split(":")
                ip_addr = parts[1].strip()
                ip_addresses.append(ip_addr)
            elif "Subnet Mask" in l:
                parts = l.split(":")
                ip_addr = parts[1].strip()
                subnet_masks.append(ip_addr)
            elif "Default Gateway" in l:
                parts = l.split(":")
                ip_addr = parts[1].strip()
                default_gateway.append(ip_addr)



    def _read_ifconfig(self):
        p = os.popen("/sbin/ifconfig")
        output = p.read()
        p.close()

        return output



def IfConfig():
    """
    """
    the_plat = platform.platform()

    if ('Microsoft' in the_plat or
        'CYGWIN' in the_plat):
        return IfConfigWindows()
    elif('FreeBSD' in the_plat):
        return ifConfigFreeBSD()
    elif('Linux' in the_plat):
        return ifConfigFreeBsd()
    





    



if __name__ == "__main__":
    i = IfConfigWindows()
    print i.get_ips(windows_output1)

    i = IfConfigLinux()
    
    print i.get_ips(linux_output1)
    print i.get_ips(linux_output2)

    i = IfConfig()
    print i.get_ips()

