#!/bin/sh

PKG_STR_WIZARD_INSTALL_TITLE="Please specify the openHAB network settings"
PKG_STR_HTTP_PORT="HTTP port"
PKG_STR_HTTP_PORT_DEFAULT="48080"
PKG_STR_HTTPS_PORT="HTTPS port"
PKG_STR_HTTPS_PORT_DEFAULT="48443"
PKG_STR_INVALID_PORT="The port number must be from 1 to 65535."
PKG_STR_FORCE_INET_ADDR_DESC="Enable this option to disables openHAB automatic network interface detection."
PKG_STR_FORCE_INET_ADDR="Enforce listen address"

create_inet_addr_store()
{
    local inet_addr_store=""

    for inet_addr in $(ip -o -f inet addr show | awk '/scope global/ {print $4}')
    do
	if [ -z ${inet_addr_store} ]
	then
            inet_addr_store="${inet_addr}"
        else
            inet_addr_store="${inet_addr_store},${inet_addr}"
        fi
    done

    printf "${inet_addr_store}\n"
}

create_install_settings_step()
{
    local step=""
    local primary_inet_addr="$(ip -o -f inet addr show | awk '/scope global/ {print $4}' | head -1)"
    local inet_addr_store=$(create_inet_addr_store)

    step="$(/bin/cat <<-EOF
    {
        "step_title": "${PKG_STR_WIZARD_INSTALL_TITLE}",
        "items": [{
            "type": "textfield",
            "subitems": [{
                "key": "pkgwizard_http_port",
                "desc": "${PKG_STR_HTTP_PORT}",
                "defaultValue": "${PKG_STR_HTTP_PORT_DEFAULT}",
                "invalidText": "${PKG_STR_INVALID_PORT}",
                "validator": {
                    "allowBlank": false,
		    "minLength": 1,
		    "maxLength": 5,
		    "fn": "{
		        var port = parseInt(arguments[0]);
			var regExp = new RegExp('^[0-9]*$');
			var isValid = ((arguments[0].match(regExp)) && (0 < port) && (65536 > port));

			return isValid;
		    }"
                }   
            },{
                "key": "pkgwizard_https_port",
                "desc": "${PKG_STR_HTTPS_PORT}",
                "defaultValue": "${PKG_STR_HTTPS_PORT_DEFAULT}",
                "invalidText": "${PKG_STR_INVALID_PORT}",
                "validator": {
                    "allowBlank": false,
		    "minLength": 1,
		    "maxLength": 5,
		    "fn": "{
		        var port = parseInt(arguments[0]);
			var regExp = new RegExp('^[0-9]*$');
			var isValid = ((arguments[0].match(regExp)) && (0 < port) && (65536 > port));

			return isValid;
		    }"
                }   
           }]
        },{
            "type": "multiselect",
            "desc": "${PKG_STR_FORCE_INET_ADDR_DESC}",
            "subitems": [{
                "key": "pkgwizard_force_inet_addr",
                "desc": "${PKG_STR_FORCE_INET_ADDR}"
	    }]
        },{
   	    "type": "combobox",
   	    "subitems": [{
                "key": "pkgwizard_inet_addr",
                "editable": false,
                "mode": "local",
                "value": "${primary_inet_addr}",
                "valueField": "inet_addr",
                "displayField": "inet_addr",
                "store": {
                    "xtype": "arraystore",
                    "fields": ["inet_addr"],
                    "data": [${inet_addr_store}]
                }
            }]
        }]
    }
EOF
)"

    printf "${step}\n"
}
    
get_install_wizard_steps()
{
    local steps="$(create_install_settings_step)"

    if [ -n "${steps}" ]
    then
        printf "[${steps}]\n"
    fi
}

install_wizard_steps="$(get_install_wizard_steps)"

if [ -z "${install_wizard_steps}" ]
then
    exit 0
fi

printf "${install_wizard_steps}\n" > ${SYNOPKG_TEMP_LOGFILE}

exit 0
