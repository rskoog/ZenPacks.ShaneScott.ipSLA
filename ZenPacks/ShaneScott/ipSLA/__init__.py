import Globals
import logging
import os
log = logging.getLogger('zen.ZenSLA')

from Products.CMFCore.DirectoryView import registerDirectory
from Products.ZenModel.ZenossSecurity import ZEN_VIEW

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

import ZenPacks.ShaneScott.ipSLA
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath
from Products.ZenModel.ZenMenu import ZenMenu

def initialize(registrar):
        registrar.registerClass(
                SLAS.SLAS,
                permission='Add DMD Objects',
        )

class ZenPack(ZenPackBase):
    packZProperties =  []

    def install(self, app):
        super(ZenPack, self).install(app)
        log.info('Installing menus')
        self.installMenuItems(app.zport.dmd)
        self.symlinkPlugin()

        log.info('Adding IPSLA organizer')
        ipSlaOrg = app.dmd.Devices.createOrganizer('/Network/IPSLA')
        plugins=[]
        networkOrg = app.dmd.findChild('Devices/Network')
        for plugin in networkOrg.zCollectorPlugins:
            plugins.append(plugin)

        plugins.append('SLADevice')

        log.info('Setting /Network/IPSLA properties')
        ipSlaOrg.setZenProperty( 'zCollectorPlugins', plugins )
        ipSlaOrg.setZenProperty( 'zPythonClass', 'ZenPacks.ShaneScott.ipSLA.SLADevice' )
        log.info('Starting ZenSLA daemon')
        os.system('$ZENHOME/bin/zensla start')


    def remove(self, app, leaveObjects=False):
        log.info('Stopping ZenSLA daemon')
        os.system('chmod a+x %s' % (zenPath('bin', 'zensla')))
        os.system('$ZENHOME/bin/zensla stop')

        if not leaveObjects:
            self.removePluginSymlink()
            log.info('Removing menus')
            self.removeMenuItems(app.zport.dmd)
            log.info('Removing devices')
            for i in app.dmd.Devices.Network.IPSLA.getSubDevices():
                i.deleteDevice()

            log.info('Removing IPSLA organizer')
            app.dmd.Devices.Network.manage_deleteOrganizer('IPSLA')
        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)


    def symlinkPlugin(self):
        log.info('Linking daemon into $ZENHOME/Products/ZenRRD')
        os.system('ln -sf %s %s' % (self.path('zensla.py'), zenPath('Products/ZenRRD', 'zensla.py')))
        os.system('chmod 0755 %s' % (zenPath('Products/ZenRRD', 'zensla.py')))
        log.info('Linking daemon listener into $ZENHOME/Products/ZenHub/services')
        os.system('ln -sf %s %s' % (self.path('services/SLAPerfConfig.py'), zenPath('Products/ZenHub/services', 'SLAPerfConfig.py')))
        os.system('chmod 0755 %s' % (zenPath('Products/ZenHub/services', 'SLAPerfConfig.py')))
        log.info('Making daemon executable')
        os.system('chmod a+x %s' % (zenPath('bin', 'zensla')))


    def removePluginSymlink(self):
        log.info('Removing daemon from $ZENHOME/Products/ZenRRD')
        os.system('rm -f %s' % (zenPath('Products/ZenRRD', 'zensla.py')))
        log.info('Removing daemon listener from $ZENHOME/Products/ZenHub/services')
        os.system('rm -f %s' % (zenPath('Products/ZenHub/services', 'SLAPerfConfig.py')))

    
    def installMenuItems(self, dmd):
        dmd.zenMenus.More.manage_addZenMenuItem(
            'ipSLAipSlaDevice',
            action='ipSLAipSlaDevice',
            description='View SLAs',
            allowed_classes=('SLADevice',),
            ordering=5.0)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'addEchoSLAS',
            action='dialog_addEchoSLAS',
            description='Add Echo SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'addHttpSLAS',
            action='dialog_addHttpSLAS',
            description='Add HTTP SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'addDnsSLAS',
            action='dialog_addDnsSLAS',
            description='Add DNS SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'addDhcpSLAS',
            action='dialog_addDhcpSLAS',
            description='Add DHCP SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'addJitterSLAS',
            action='dialog_addJitterSLAS',
            description='Add Jitter SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'addTcpSLAS',
            action='dialog_addTcpSLAS',
            description='Add TCP SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'writeMemSLAS',
            action='dialog_writeMemSLAS',
            description='Write mem...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)

        dmd.zenMenus.More.manage_addZenMenuItem(
            'delSLAS',
            action='dialog_delSLAS',
            description='Delete SLA...',
            allowed_classes=('SLADevice',),
            ordering=5.0,
            isdialog=True)
    
    def removeMenuItems(self, dmd):
        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "ipSLAipSlaDevice",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "addEchoSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "addHttpSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "addDnsSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "addDhcpSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "addJitterSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "addTcpSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "writeMemSLAS",))
        except (KeyError, AttributeError):
            pass

        try:
            dmd.zenMenus.More.manage_deleteZenMenuItem((
                "delSLAS",))
        except (KeyError, AttributeError):
            pass