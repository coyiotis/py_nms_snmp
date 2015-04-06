from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
import time, bisect
from mon_stats import getDiskSpace, getRAMinfo, getCPUuse, getHostname

class SysDescr:
    name = (1,3,6,1,2,1,1,1,0)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
        return api.protoModules[protoVer].OctetString(
            'PySNMP example command responder'
            )

class Uptime:
    name = (1,3,6,1,2,1,1,3,0)
    birthday = time.time()
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other    
    def __call__(self, protoVer):
        return api.protoModules[protoVer].TimeTicks(
            (time.time()-self.birthday)*100
            )
class SysHost:
    name = (1,3,6,1,2,1,1,10,0)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
    
        return api.protoModules[protoVer].OctetString(
            str(getHostname())
            )

class SysMemus:
    name = (1,3,6,1,2,1,1,11,0)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
    
        return api.protoModules[protoVer].OctetString(
            str(getRAMinfo()[1])
            )

class SysMemTot:
    name = (1,3,6,1,2,1,1,11,1)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
    
        return api.protoModules[protoVer].OctetString(
            str(getRAMinfo()[0])
            )
        
class SysHDus:
    name = (1,3,6,1,2,1,1,12,0)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
    
        return api.protoModules[protoVer].OctetString(
            str(getDiskSpace()[1])
            )

class SysHDTot:
    name = (1,3,6,1,2,1,1,12,1)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
    
        return api.protoModules[protoVer].OctetString(
            str(getDiskSpace()[0])
            )

class SysCPU:
    name = (1,3,6,1,2,1,1,13,0)
    def __eq__(self, other): return self.name == other
    def __ne__(self, other): return self.name != other
    def __lt__(self, other): return self.name < other
    def __le__(self, other): return self.name <= other
    def __gt__(self, other): return self.name > other
    def __ge__(self, other): return self.name >= other
    def __call__(self, protoVer):
    
        return api.protoModules[protoVer].OctetString(
            str(getCPUuse().split('%',1)[0])
            )

mibInstr = (
    SysDescr(), Uptime(), SysHost(), SysMemus(), SysMemTot(), SysHDus(), SysHDTot(), SysCPU() # sorted by object name
    )

mibInstrIdx = {}
for mibVar in mibInstr:
    mibInstrIdx[mibVar.name] = mibVar

def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = api.decodeMessageVersion(wholeMsg)
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]
        else:
            print('Unsupported SNMP version %s' % msgVer)
            return
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg, asn1Spec=pMod.Message(),
            )
        rspMsg = pMod.apiMessage.getResponse(reqMsg)
        rspPDU = pMod.apiMessage.getPDU(rspMsg)        
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        varBinds = []; pendingErrors = []
        errorIndex = 0
        # GETNEXT PDU
        if reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
            # Produce response var-binds
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                errorIndex = errorIndex + 1
                # Search next OID to report
                nextIdx = bisect.bisect(mibInstr, oid)
                if nextIdx == len(mibInstr):
                    # Out of MIB
                    varBinds.append((oid, val))
                    pendingErrors.append(
                        (pMod.apiPDU.setEndOfMibError, errorIndex)
                        )
                else:
                    # Report value if OID is found
                    varBinds.append(
                        (mibInstr[nextIdx].name, mibInstr[nextIdx](msgVer))
                        )
        elif reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                if oid in mibInstrIdx:
                    varBinds.append((oid, mibInstrIdx[oid](msgVer)))
                else:
                    # No such instance
                    varBinds.append((oid, val))
                    pendingErrors.append(
                        (pMod.apiPDU.setNoSuchInstanceError, errorIndex)
                        )
                    break
        else:
            # Report unsupported request type
            pMod.apiPDU.setErrorStatus(rspPDU, 'genErr')
        pMod.apiPDU.setVarBinds(rspPDU, varBinds)
        # Commit possible error indices to response PDU
        for f, i in pendingErrors:
            f(rspPDU, i)
        transportDispatcher.sendMessage(
            encoder.encode(rspMsg), transportDomain, transportAddress
            )
    return wholeMsg

transportDispatcher = AsynsockDispatcher()
transportDispatcher.registerRecvCbFun(cbFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpSocketTransport().openServerMode(('<IPv4>', 161))
)

# UDP/IPv6
transportDispatcher.registerTransport(
    udp6.domainName, udp6.Udp6SocketTransport().openServerMode(('<IPv6>', 161))
)

transportDispatcher.jobStarted(1)

try:
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.runDispatcher()
except:
    transportDispatcher.closeDispatcher()
    raise

