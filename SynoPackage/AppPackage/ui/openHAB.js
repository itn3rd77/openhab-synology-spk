Ext.ns("ORG.OPENHAB");

ORG.OPENHAB.CGI_OPENHAB = "/webman/3rdparty/openHAB/openhab.cgi";
ORG.OPENHAB.HTTP_PORT = "8080";
ORG.OPENHAB.HTTPS_PORT = "8443";

Ext.define('ORG.OPENHAB.Instance', {
    extend: 'SYNO.SDS.AppInstance',
    appWindowName: 'ORG.OPENHAB.Manager',
    constructor: function() {
        this.callParent(arguments);
    }
});

Ext.define('ORG.OPENHAB.SettingPanel', {
    extend: 'SYNO.SDS.Utils.FormPanel',
    constructor: function(a) {
        var config = Ext.apply({
            border: false,
            trackresetonload: true,
            buttons: [{
                xtype: "syno_button",
                btnStyle: "blue",
                text: _T("common", "commit"),
                handler: this.onSave,
                scope: this
            }, {
                xtype: "syno_button",
                text: _T("common", "reset"),
                handler: this.onReset,
                scope: this
            }],
            items: [{
                title: "HTTP/HTTPS",
                xtype: "syno_numberfield",
                name: "http_port",
                fieldLabel: _TT("ORG.OPENHAB.Instance", 'main', 'http_port'),
                allowBlank: false,
                allowDecimals: false,
                maxlength: 5,
                vtype: "port",
                value: ORG.OPENHAB.HTTP_PORT
            }, {
                xtype: "syno_numberfield",
                name: "https_port",
                fieldLabel: _TT("ORG.OPENHAB.Instance", 'main', 'https_port'),
                allowBlank: false,
                allowDecimals: false,
                maxlength: 5,
                vtype: "port",
                value: ORG.OPENHAB.HTTPS_PORT
            }, {
                xtype: "syno_checkbox",
                name: "do_restart",
                checked: true,
                boxLabel: _TT("ORG.OPENHAB.Instance", 'main', 'do_restart')
            }]
        }, a);
        this.owner = a.owner;
        this.callParent([config]);
    },
    applyForm: function() {
        this.setStatusBusy({
            text: _TT("ORG.OPENHAB.Instance", "message", "apply_form")
        });
        Ext.Ajax.request({
            url: ORG.OPENHAB.CGI_OPENHAB,
            method: 'GET',
            params: Ext.apply({ action: "save" }, this.form.getValues()),
            scope: this,
            success: function(response, opts) {
                this.owner.getMsgBox().alert(this.owner.title,_TT("ORG.OPENHAB.Instance", "message", "form_apply_success"));
                this.clearStatusBusy();
                this.requestPorts();
            },
            failure: function(response, opts) {
                this.owner.getMsgBox().alert(this.owner.title, _T("error", "error_unknown"));
                this.clearStatusBusy();
            }
        });
    },
    checkDirty: function() {
        var b = false;
        var a = this.getForm().getValues();

        this.params = {};

        if (this.getForm().findField("http_port").isDirty()) {
            b = true;
            this.params.http_port = a.http_port;
        }
        if (this.getForm().findField("https_port").isDirty()) {
            b = true;
            this.params.https_port = a.https_port;
        }

        return b;
    },
    initEvents: function() {
        this.callParent(arguments);
        this.mon(this, 'afterlayout', function() {
            this.requestPorts();
        }, this, {single: true});
    },
    isPortsValid: function() {
        var a = this.getForm().getValues();
        if ((a.http_port === a.https_port) && (undefined !== a.http_port)) {
            this.getForm().findField("https_port").markInvalid(_TT("ORG.OPENHAB.Instance", "message", "err_equal_http_https"));
            return false;
        }
        return true;
    },
    onSave: function() {
        if (_S("is_admin")) {
            if (!this.checkDirty()) {
                this.setStatusError({
                    text:_T("error", "nochange_subject"),
                    clear: true
                });
                return;
            }
            if (!this.getForm().isValid() || !this.isPortsValid()) {
                this.setStatusError({
                    text: _T("common", "forminvalid"),
                    clear: true
                });
                return;
            }
            this.applyForm();
        }
    },
    onReset: function() {
        this.getForm().reset();
    },
    requestPorts: function() {
        this.setStatusBusy();
        var onSuccess = function(response, opts) {
            var data = Ext.decode(response.responseText).data;
            this.getForm().setValues(data);
            this.clearStatusBusy();
        };
        Ext.Ajax.request({
            url: ORG.OPENHAB.CGI_OPENHAB,
            method: 'GET',
            params: { action: "load" },
            scope: this,
            success: onSuccess,
            failure: function(response, opts) {
                this.owner.getMsgBox().alert(this.owner.title, _T("error", "error_unknown"));
                this.clearStatusBusy();
            }
        });
    }
});

Ext.define('ORG.OPENHAB.Manager', {
    extend: 'SYNO.SDS.AppWindow',
    appInstance: null,
    mainPanel: null,
    constructor: function(a) {
        this.appInstance = a.appInstance;
        this.mainPanel = new ORG.OPENHAB.SettingPanel({owner: this});

        var config = Ext.apply({
            resizable: false,
            maximizable: false,
            minimizable: true,
            width: 475,
            height: 300,
            dsmStyle: 'v5',
            layout: 'fit',
            items: [
                this.mainPanel
            ]
        }, a);

        this.callParent([config]);
    }
});
