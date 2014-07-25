(function(){

var ZC = Ext.ns('Zenoss.component');


function render_link(ob) {
    if (ob && ob.uid) {
        return Zenoss.render.link(ob.uid);
    } else {
        return ob;
    }
}

ZC.SLASPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'SLAS',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'severity'},
                {name: 'status'},
                {name: 'hasMonitor'},
                {name: 'monitor'},
                {name: 'rttMonCtrlAdminOwner'},
                {name: 'rttMonCtrlAdminTag'},
                {name: 'rttMonCtrlAdminRttType'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 60
            },{
               id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                width: 120,
                sortable: true
            },{
                id: 'rttMonCtrlAdminOwner',
                dataIndex: 'rttMonCtrlAdminOwner',
                header: _t('Owner'),
                sortable: true,
            },{
                id: 'rttMonCtrlAdminTag',
                dataIndex: 'rttMonCtrlAdminTag',
                header: _t('Group'),
                sortable: true
            },{
                id: 'rttMonCtrlAdminRttType',
                dataIndex: 'rttMonCtrlAdminRttType',
                header: _t('Type'),
                sortable: true,
                width: 200,
            }]
        });
        ZC.SLASPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('SLASPanel', ZC.SLASPanel);
ZC.registerName('SLAS', _t('SLA'), _t('SLAs'));
})();
