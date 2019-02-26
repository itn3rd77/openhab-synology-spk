Ext.ns("ORG.OPENHAB");

ORG.OPENHAB.APP_WIDTH=990;
ORG.OPENHAB.APP_HEIGHT=560;
ORG.OPENHAB.CGI_OPENHAB = "/webman/3rdparty/openHAB/openHAB.cgi";
ORG.OPENHAB.HTTP_PORT = "48080";
ORG.OPENHAB.HTTPS_PORT = "48443";

Ext.define("ORG.OPENHAB.Instance", {
    extend: "SYNO.SDS.AppInstance",
    appWindowName: "ORG.OPENHAB.Manager",
    constructor: function() {
        this.callParent(arguments);
    }
});

Ext.define("ORG.OPENHAB.Manager", {
    extend: "SYNO.SDS.PageListAppWindow",
    constructor: function(a) {
        var config = Ext.apply({
            width: ORG.OPENHAB.APP_WIDTH,
            height: ORG.OPENHAB.APP_HEIGHT,
			minWidth: ORG.OPENHAB.APP_WIDTH,
			minHeight: ORG.OPENHAB.APP_HEIGHT,
			activePage: "ORG.OPENHAB.OverviewPanel",
            listItems: [{
				iconCls: "icon-overview",
				text: "Overview",
				fn: "ORG.OPENHAB.OverviewPanel"
			},{
				iconCls: "icon-setting",
				text: "Network",
				fn: "ORG.OPENHAB.NetworkPanel"
			}, {
				iconCls: "icon-security",
				text: "Security",
				fn: "ORG.OPENHAB.SecurityPanel"
			}]
        }, a);

        this.callParent([config]);
    }
});

Ext.define("ORG.OPENHAB.OverviewPanel", {
	extend: "SYNO.SDS.Utils.FormPanel",
    constructor: function(a) {
        var config = Ext.apply({
			autoWidth: true,
			border: false,
            items: [{
				xtype: "syno_fieldset",
				title: _TT("ORG.OPENHAB.Instance", "overview", "overview_title"),
				itemId: "overviewfieldset",
				name: "overviewfieldset",
				id: "overviewfieldset",
				items: [{
					  xtype: "syno_displayfield",
					  htmlEncode: false,
					  style: "margin-bottom:8px",
					  value: _TT("ORG.OPENHAB.Instance", "overview", "overview_desc")
				},{
					xtype: "syno_textarea",
					name: "version_properties",
					hideLabel: true,
					style: {
						"fontFamily": "courier new",
						"fontSize": "12px"
					},
					anchor: "100%",
					readOnly: true,
					grow: true,
					growMax: 500
				}]
			}]
        }, a);
        this.owner = a.owner;
        this.callParent([config]);
    },
    initEvents: function() {
        this.callParent(arguments);
        this.mon(this, "afterlayout", function() {
            this.requestVersionProperties();
        }, this, {single: true});
    },
    requestVersionProperties: function() {
        this.setStatusBusy();
        var onSuccess = function(response, opts) {
			var result = Ext.decode(response.responseText);
			if (result.success === true) {
				var data = Ext.decode(response.responseText).data;
				this.getForm().setValues(data);
			} else {
				this.owner.getMsgBox().alert(this.owner.title, _TT("ORG.OPENHAB.Instance", "overview", "version_properties_err"));
			}			
            this.clearStatusBusy();
        };
        Ext.Ajax.request({
            url: ORG.OPENHAB.CGI_OPENHAB,
            method: "POST",
            params: { action: "version_properties" },
            scope: this,
            success: onSuccess,
            failure: function(response, opts) {
                this.owner.getMsgBox().alert(this.owner.title, _T("error", "error_unknown"));
                this.clearStatusBusy();
            }
        });
    }
})

Ext.define("ORG.OPENHAB.NetworkPanel", {
    extend: "SYNO.SDS.Utils.FormPanel",
    constructor: function(a) {
        var config = Ext.apply({
            autoWidth: true,
			border: false,
            trackResetOnLoad: true,
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
				xtype: "syno_fieldset",
				title: _TT("ORG.OPENHAB.Instance", "network", "network_ports_title"),
				itemId: "network_ports_fieldset",
				name: "network_ports_fieldset",
				id: "network_ports_fieldset",
				items: [{
					  xtype: "syno_displayfield",
					  htmlEncode: false,
					  style: "margin-bottom:8px",
					  value: _TT("ORG.OPENHAB.Instance", "network", "network_ports_desc")
				},{
					xtype: "syno_numberfield",
					name: "http_port",
					fieldLabel: _TT("ORG.OPENHAB.Instance", "network", "network_ports_http"),
					allowBlank: false,
					allowDecimals: false,
					maxlength: 5,
					vtype: "port",
					value: ORG.OPENHAB.HTTP_PORT
				}, {
					xtype: "syno_numberfield",
					name: "https_port",
					fieldLabel: _TT("ORG.OPENHAB.Instance", "network", "network_ports_https"),
					allowBlank: false,
					allowDecimals: false,
					maxlength: 5,
					vtype: "port",
					value: ORG.OPENHAB.HTTPS_PORT
				}]
			}, {
				xtype: "syno_fieldset",
				title: _TT("ORG.OPENHAB.Instance", "network", "network_interfaces_title"),
				itemId: "network_interface_fieldset",
				name: "network_interface_fieldset",
				id: "network_interface_fieldset",
				items: [{
					  xtype: "syno_displayfield",
					  htmlEncode: false,
					  style: "margin-bottom:8px",
					  value: _TT("ORG.OPENHAB.Instance", "network", "network_interfaces_desc")
				},{
					xtype: "syno_combobox",
					name: "http_address",
					fieldLabel: _TT("ORG.OPENHAB.Instance", "network", "network_interfaces_selection"),
					editable: false,
					valueField: "http_address",
					displayField: "http_address",
					triggerAction : 'all',
					mode: 'local',
					store: new Ext.data.JsonStore({
		                url: ORG.OPENHAB.CGI_OPENHAB,
		                baseParams: {
							action: "http_address"
						},
		                root: "data",					
                		fields: [
                			{ name:"http_address", type:"string" },
                			{ name:"default", type:"boolean" }
                		]
                    }),
                    listeners: {
                        scope: this,
                        afterRender: this.setDefaultValue
                    }
				}]
			}]				
        }, a);
        this.owner = a.owner;
        this.callParent([config]);
    },
    setDefaultValue: function(combobox) {
        combobox.getStore().on("load", function(store, records) {
            var idx = store.find("default", "true");
            var form = this.getForm();

            combobox.setValue(store.getAt(idx).get(combobox.valueField));
            form.setValues(form.getValues());            
        }, this);
        combobox.getStore().load();
    },
    applyForm: function() {
        this.setStatusBusy({text: _TT("ORG.OPENHAB.Instance", "message", "apply_form")});
        Ext.Ajax.request({
            url: ORG.OPENHAB.CGI_OPENHAB,
            method: "POST",
            params: Ext.apply({ action: "network_settings" }, this.form.getValues()),
            scope: this,
            success: function(response, opts) {
                var payload = Ext.decode(response.responseText);
                this.owner.getMsgBox().alert(this.owner.title, _TT("ORG.OPENHAB.Instance", "message", payload.message));
                this.clearStatusBusy();
                this.requestPorts();
				
				var form = this.getForm();
				form.setValues(form.getValues());
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

        if (this.getForm().findField("http_address").isDirty()) {
            b = true;
            this.params.http_address = a.http_address;
        }

        return b;
    },
    initEvents: function() {
        this.callParent(arguments);
        this.mon(this, "afterlayout", function() {
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
        	this.appWin.getMsgBox().confirm(this.title, _TT("ORG.OPENHAB.Instance", "network", "network_confirm_apply"), function(c) {
        		if ("yes"=== c) {
                    this.applyForm();
                }
            }, this)
        }
    },
    onReset: function() {
        this.getForm().reset();
    },
    requestPorts: function() {
        this.setStatusBusy();
        Ext.Ajax.request({
            url: ORG.OPENHAB.CGI_OPENHAB,
            method: "POST",
            params: { action: "http_ports" },
            scope: this,
            success: function(response, opts) {
                this.getForm().setValues(Ext.decode(response.responseText).data);
                this.clearStatusBusy();
            },
            failure: function(response, opts) {
                this.owner.getMsgBox().alert(this.owner.title, _T("error", "error_unknown"));
                this.clearStatusBusy();
            }
        });
    }
});

Ext.define("ORG.OPENHAB.SecurityPanel", {
    extend: "Ext.form.FormPanel",
    constructor: function(a) {
        var config = Ext.apply({
            border: false,
            fileUpload: true,
            trackResetOnLoad: true,
            url: ORG.OPENHAB.CGI_OPENHAB,
            buttons: [{
                xtype: "syno_button",
                btnStyle: "blue",
                text: _T("common", "apply"),
                handler: this.onUpload,
                scope: this
            }, {
                xtype: "syno_button",
                text: _T("common", "cancel"),
                handler: this.onCancel,
                scope: this
            }],
            items: [{
				xtype: "syno_fieldset",
				title: _TT("ORG.OPENHAB.Instance", "security", "trust_ca_certs"),
				itemId: "trust_ca_certs_fieldset",
				name: "trust_ca_certs_fieldset",
				id: "trust_ca_certs_fieldset",
				items: [{
					  xtype: "syno_displayfield",
					  htmlEncode: false,
					  style: "margin-bottom:8px",
					  value: _TT("ORG.OPENHAB.Instance", "security", "trust_ca_certs_desc")
				}, {
				    xtype: "syno_filebutton",
				    itemId: "ca_file",
				    id: "ca_file",
                    name: "cacert",
                    fieldLabel: _TT("ORG.OPENHAB.Instance", "security", "trust_ca_certs_filebutton"),
				}]
			}, {
				xtype: "syno_fieldset",
				itemId: "delete_trust_store_fieldset",
				name: "delete_trust_store_fieldset",
				id: "delete_trust_store_fieldset",
				items: [{
					  xtype: "syno_displayfield",
					  htmlEncode: false,
					  style: "margin-bottom:8px",
					  value: _TT("ORG.OPENHAB.Instance", "security", "delete_trust_store_desc")
				},{
					xtype: "syno_button",
					btnStyle: "red",
					text: _TT("ORG.OPENHAB.Instance", "security", "form_delete_trust_store"),
					handler: this.onDelete,
					scope: this				
				}]
			}]
        }, a);
        this.owner = a.owner;
        this.callParent([config]);
		this.mon(this.getForm(), "actioncomplete", this.actionComplete, this);
		this.mon(this.getForm(), "actionfailed", this.actionFailed, this)        
    },
    actionComplete: function(f, a) {
        this.owner.clearStatusBusy();
		this.getForm().reset();
        this.owner.getMsgBox().alert(this.owner.title, _TT("ORG.OPENHAB.Instance", "message", "form_apply_ok"));
    },
    actionFailed: function(f, a) {
        this.owner.clearStatusBusy();
		this.owner.getMsgBox().alert(this.owner.title, this.getErrorMessage(a.result));
    },
    getErrorMessage: function(r) {
        switch(r.error_message) {
            case "cacert_check_failed":
                return _TT("ORG.OPENHAB.Instance", "security", "cacert_check_failed");
            case "keytool_import_failed":
                return _TT("ORG.OPENHAB.Instance", "security", "keytool_import_failed");
            case "openhab_restart_err":
                return _TT("ORG.OPENHAB.Instance", "message", "openhab_restart_err");
            case "delete_cacert_err":
                return _TT("ORG.OPENHAB.Instance", "message", "delete_cacert_err");
			default:
                return _T("error", "error_unknown");
        }
    },
    onDelete: function() {
        if (_S("is_admin")) {
        	this.appWin.getMsgBox().confirm(this.title, _TT("ORG.OPENHAB.Instance", "security", "security_confirm_delete"), function(c) {
        		if ("yes"=== c) {
					this.owner.setStatusBusy();
					Ext.Ajax.request({
						url: ORG.OPENHAB.CGI_OPENHAB,
						method: "POST",
						params: { action: "delete_cacert" },
						scope: this,
						success: function(response, opts) {
							var result = Ext.decode(response.responseText);
							if (result.success === true) {
								this.owner.getMsgBox().alert(this.owner.title, _TT("ORG.OPENHAB.Instance", "message", "form_apply_ok"));
							} else {
								this.owner.getMsgBox().alert(this.owner.title, this.getErrorMessage(result));
							}
							this.owner.clearStatusBusy();
						},
						failure: function(response, opts) {
							this.owner.clearStatusBusy();
							this.owner.getMsgBox().alert(this.owner.title, _T("error", "error_unknown"));
						}
					});
                }
            }, this)
        }
    },
    onCancel: function() {
        this.getForm().reset();
    },
    onUpload: function() {
		if (! Ext.getCmp("ca_file").getValue()) {
			this.owner.getMsgBox().alert(this.owner.title, _TT("ORG.OPENHAB.Instance", "security", "no_cacert_selected"));
		    return;
	    }
	    this.owner.setStatusBusy();
        this.getForm().doAction("apply");
    }
});
