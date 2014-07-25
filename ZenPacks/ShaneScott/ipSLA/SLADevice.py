import Globals
from AccessControl import ClassSecurityInfo
from Products.ZenModel.Device import Device
from Products.ZenModel.ZenossSecurity import *
from Products.ZenRelations.RelSchema import *
import copy
from Products.ZenWidgets import messaging
from Products.ZenUtils.Utils import prepId
from ZenPacks.ShaneScott.ipSLA.SLAS import SLAS
from Products.ZenModel.Commandable import Commandable
import logging
log = logging.getLogger('zen.ZenSLA')


def toHex(ip):
    splitIp = ip.split('.')
    list = ''
    for i in splitIp:
        ii = hex(int(i))
        iii = ii.replace('0x','')
        if len(iii) < 2: iii = '0' + iii
        list = list + iii + ' '
    if len(list) > 11:
       list = list[:-1]
    #list = list + "00 00"
    list = list.upper()
    return list


class SLADevice(Device):
    "Service Level Agreement Panel"

    _relations = Device._relations + (
        ('ipSLAs', ToManyCont(ToOne,
            "ZenPacks.ShaneScott.ipSLA.SLAS", "SLADevice")),
        )

    slaTypeMap = ('ECHO', 'HTTP', 'DNS', 'DHCP')

    factory_type_information = copy.deepcopy(Device.factory_type_information)

    def __init__(self, *args, **kw):
        Device.__init__(self, *args, **kw)
        self.buildRelations()


    def manage_delSLAS(self, rttIndex, deviceIp, community, REQUEST=None):
        """Delete a SLA on a host"""
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 6
               """
        newId = "delSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA delete command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_writeMemSLAS(self, deviceIp, community, REQUEST=None):
        """Write mem on a host"""
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.2.1.54.0 i 1
               """
        newId = "writeMemSLA" 

        Commandable.manage_addUserCommand(self, newId, desc='SLA write mem command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_addTcpSLAS(self, newId, rttIndex, deviceIp, community, rttMonEchoAdminTargetAddress, rttMonEchoAdminTargetPort, rttMonScheduleAdminRttStartTime=1, rttMonCtrlAdminOwner="zenoss", REQUEST=None):
        """Add a SLA to this SLA host"""
        tag = str(newId)
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 4 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.4.""" + str(rttIndex) + """ i 6 \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.1.""" + str(rttIndex) + """ i 24 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.3.""" + str(rttIndex) + """ s '""" + newId + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.2.""" + str(rttIndex) + """ s '""" + rttMonCtrlAdminOwner + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.2.""" + str(rttIndex) + """ x '""" + toHex(rttMonEchoAdminTargetAddress) + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.5.""" + str(rttIndex) + """ i """ + str(rttMonEchoAdminTargetPort) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.5.1.2.""" + str(rttIndex) + """ t """ + str(rttMonScheduleAdminRttStartTime) + """
               """
        log.info("SLA Add cmd %s", cmd)
        newId = "addSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA add command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_addJitterSLAS(self, newId, rttIndex, deviceIp, community, rttMonEchoAdminTargetAddress, rttMonEchoAdminTargetPort, rttMonEchoAdminInterval=60, rttMonEchoAdminNumPackets=100, rttMonScheduleAdminRttStartTime=1, rttMonCtrlAdminOwner="zenoss", REQUEST=None):
        """Add a SLA to this SLA host"""
        tag = str(newId)
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.4.""" + str(rttIndex) + """ i 9 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.3.""" + str(rttIndex) + """ s '""" + newId + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.2.""" + str(rttIndex) + """ s '""" + rttMonCtrlAdminOwner + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.1.""" + str(rttIndex) + """ i 27 \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.2.""" + str(rttIndex) + """ x '""" + toHex(rttMonEchoAdminTargetAddress) + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.5.""" + str(rttIndex) + """ i """ + str(rttMonEchoAdminTargetPort) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.17.""" + str(rttIndex) + """ i """ + str(rttMonEchoAdminInterval) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.18.""" + str(rttIndex) + """ i """ + str(rttMonEchoAdminNumPackets) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.5.1.2.""" + str(rttIndex) + """ t """ + str(rttMonScheduleAdminRttStartTime) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 4
               """
        log.info("SLA Add cmd %s", cmd)
        newId = "addSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA add command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_addDnsSLAS(self, newId, rttIndex, deviceIp, community, rttMonEchoAdminNameServer, rttMonEchoAdminTargetAddressString, rttMonScheduleAdminRttStartTime=1, rttMonCtrlAdminOwner="zenoss", REQUEST=None):
        """Add a SLA to this SLA host"""
        tag = str(newId)
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.4.""" + str(rttIndex) + """ i 8 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.3.""" + str(rttIndex) + """ s '""" + newId + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.2.""" + str(rttIndex) + """ s '""" + rttMonCtrlAdminOwner + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.1.""" + str(rttIndex) + """ i 26 \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.11.""" + str(rttIndex) + """ s '""" + rttMonEchoAdminTargetAddressString + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.12.""" + str(rttIndex) + """ s '""" + rttMonEchoAdminNameServer + """' \
               .1.3.6.1.4.1.9.9.42.1.2.5.1.2.""" + str(rttIndex) + """ t """ + str(rttMonScheduleAdminRttStartTime) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 4
               """
        log.info("SLA Add cmd %s", cmd)
        newId = "addSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA add command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_addDhcpSLAS(self, newId, rttIndex, deviceIp, community, rttMonScheduleAdminRttStartTime=1, rttMonCtrlAdminOwner="zenoss", REQUEST=None):
        """Add a SLA to this SLA host"""
        tag = str(newId)
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.4.""" + str(rttIndex) + """ i 11 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.3.""" + str(rttIndex) + """ s '""" + newId + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.2.""" + str(rttIndex) + """ s '""" + rttMonCtrlAdminOwner + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.1.""" + str(rttIndex) + """ i 29 \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.13.""" + str(rttIndex) + """ i 2 \
               .1.3.6.1.4.1.9.9.42.1.2.5.1.2.""" + str(rttIndex) + """ t """ + str(rttMonScheduleAdminRttStartTime) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 4
               """
        log.info("SLA Add cmd %s", cmd)
        newId = "addSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA add command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_addEchoSLAS(self, newId, rttIndex, deviceIp, community, rttMonEchoAdminTargetAddress, rttMonScheduleAdminRttStartTime=1, rttMonCtrlAdminFrequency=60, rttMonCtrlAdminOwner="zenoss", rttMonCtrlAdminThreshold=5000, rttMonCtrlAdminTimeout=5, REQUEST=None):
        """Add a SLA to this SLA host"""
        tag = str(newId)
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.4.""" + str(rttIndex) + """ i 1 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.3.""" + str(rttIndex) + """ s '""" + newId + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.2.""" + str(rttIndex) + """ s '""" + rttMonCtrlAdminOwner + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.1.""" + str(rttIndex) + """ i 2 \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.2.""" + str(rttIndex) + """ x '""" + toHex(rttMonEchoAdminTargetAddress) + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.5.""" + str(rttIndex) + """ i """ + str(rttMonCtrlAdminThreshold) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.6.""" + str(rttIndex) + """ i """ + str(rttMonCtrlAdminFrequency) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.7.""" + str(rttIndex) + """ i """ + str(rttMonCtrlAdminTimeout) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.13.""" + str(rttIndex) + """ i 2 \
               .1.3.6.1.4.1.9.9.42.1.2.5.1.2.""" + str(rttIndex) + """ t """ + str(rttMonScheduleAdminRttStartTime) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 4
               """
        log.info("SLA Add cmd %s", cmd)
        newId = "addSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA add command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId)
        if REQUEST:
            return self.callZenScreen(REQUEST)


    def manage_addHttpSLAS(self, newId, rttIndex, deviceIp, community, rttMonEchoAdminURL, rttMonScheduleAdminRttStartTime=1, rttMonCtrlAdminFrequency=60, rttMonCtrlAdminOwner="zenoss", rttMonCtrlAdminThreshold=5000, rttMonCtrlAdminTimeout=5, REQUEST=None):
        """Add a SLA to this SLA host"""
        tag = str(newId)
        cmd="""
               snmpset -v2c -c """ + community + """ """ + deviceIp + """  \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.4.""" + str(rttIndex) + """ i 7 \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.3.""" + str(rttIndex) + """ s '""" + newId + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.2.""" + str(rttIndex) + """ s '""" + rttMonCtrlAdminOwner + """' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.5.""" + str(rttIndex) + """ i """ + str(rttMonCtrlAdminThreshold) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.6.""" + str(rttIndex) + """ i """ + str(rttMonCtrlAdminFrequency) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.7.""" + str(rttIndex) + """ i """ + str(rttMonCtrlAdminTimeout) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.1.""" + str(rttIndex) + """ i 25 \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.13.""" + str(rttIndex) + """ i 2 \
               .1.3.6.1.4.1.9.9.42.1.2.5.1.2.""" + str(rttIndex) + """ t """ + str(rttMonScheduleAdminRttStartTime) + """ \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.15.""" + str(rttIndex) + """ s '""" + rttMonEchoAdminURL + """' \
               .1.3.6.1.4.1.9.9.42.1.2.2.1.20.""" + str(rttIndex) + """ s 'GET / HTTP/1.0\r\n' \
               .1.3.6.1.4.1.9.9.42.1.2.1.1.9.""" + str(rttIndex) + """ i 4
               """
        log.info("SLA Add cmd %s", cmd)
        newId = "addSLA" + str(rttIndex)

        Commandable.manage_addUserCommand(self, newId, desc='SLA add command', cmd=cmd)
        Commandable.manage_doUserCommand(self, newId)
        Commandable.manage_deleteUserCommand(self, ids=newId) 
        if REQUEST:
            return self.callZenScreen(REQUEST)
