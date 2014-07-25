from Products.ZenHub.services.PerformanceConfig import PerformanceConfig
from Products.ZenHub.PBDaemon import translateError

from sets import Set
from Products.ZenRRD.zensla import SLAConfig

import logging
log = logging.getLogger('zen.ZenSLA')

def getComponentConfig(comp):
    oids = []
    if comp.snmpIgnore(): return None
    basepath = comp.rrdPath()
    perfServer = comp.device().getPerformanceServer()
    for templ in comp.getRRDTemplates():
        for ds in templ.getRRDDataSources("SLA"):
            if not ds.enabled: continue
            oid = ds.oid
            if not oid: continue
            snmpindex = getattr(comp, "instance", comp.snmpindex)
            if snmpindex: oid = "%s.%s" % (oid, snmpindex)
            for dp in ds.getRRDDataPoints():
                cname = comp.meta_type != "Device" \
                        and comp.viewName() or dp.id
                oids.append((cname,
                             oid,
                             "/".join((basepath, dp.name())),
                             dp.rrdtype,
                             dp.getRRDCreateCommand(perfServer),
                             (dp.rrdmin, dp.rrdmax)))
    return (oids, comp.getThresholdInstances('SLA'))


def getDeviceConfig(dev):
    dev = dev.primaryAq()
    if not dev.snmpMonitorDevice(): 
        log.debug("skipping %s SNMP-SLA monitoring disabled", dev.id)
        return None
    result = SLAConfig()
    oids, threshs = getComponentConfig(dev)
    for comp in dev.os.getMonitoredComponents(collector="zensla"):
        cfg = getComponentConfig(comp)
        if cfg:
            oids.extend(cfg[0])
            threshs.extend(cfg[1])
    result.lastChangeTime = float(dev.getLastChange())
    result.device = dev.id
    result.connInfo = dev.getSnmpConnInfo()
    result.thresholds = threshs
    result.oids = oids
    return result


class SLAPerfConfig(PerformanceConfig):

    @translateError
    def remote_getDevices(self, devices=None):
        """Return the subset of devices that should be monitored.
        
        If devices is empty, then all the monitored devices are given.
        """
        if devices:
            if not isinstance(devices, list):
                devices = Set([devices])
            else:
                devices = Set(devices)
        snmp = []
        for dev in self.config.devices():
            if devices and dev.id not in devices: continue
            dev = dev.primaryAq()
            if dev.snmpMonitorDevice():
                snmp.append(dev.id)
        return snmp


    def getDeviceConfig(self, device):
        "Fill in the template method to push our configs"
        return getDeviceConfig(device)


    @translateError
    def remote_getDeviceConfigs(self, devices):
        "Fetch the configs for the given devices"
        result = []
        for d in devices:
            device = self.getPerformanceMonitor().findDevice(d)
            if device:
                config = self.getDeviceConfig(device)
                if config:
                    result.append(config)
        return result


    @translateError
    def remote_getDeviceUpdates(self, devices):
        """Return a list of devices that have changed.
        Takes a list of known devices and the time of last known change.
        The result is a list of devices that have changed,
        or not in the list."""
        lastChanged = dict(devices)
        new = Set()
        all = Set()
        for dev in self.config.devices():
            dev = dev.primaryAq()
            if dev.snmpMonitorDevice():
                all.add(dev.id)
                if lastChanged.get(dev.id, 0) < float(dev.getLastChange()):
                    new.add(dev.id)
        deleted = Set(lastChanged.keys()) - all
        return list(new | deleted)


    def sendDeviceConfig(self, listener, config):
        "Template method helper for PerformanceConfig.pushConfig"
        return listener.callRemote('updateDeviceConfig', config)


    def update(self, object):
        from Products.ZenModel.RRDDataSource import RRDDataSource
        if isinstance(object, RRDDataSource):
            if object.sourcetype != 'SLA':
                return
        PerformanceConfig.update(self, object)