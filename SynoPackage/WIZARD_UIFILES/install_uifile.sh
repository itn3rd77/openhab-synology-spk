#!/bin/sh
#
# MIT License
#
# Copyright (c) 2018 Ingo Theiss <ingo.theiss@i-matrixx.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

PKG_STR_WIZARD_INSTALL_TITLE="Please specify the openHAB network settings"
PKG_STR_HTTP_PORT="HTTP port"
PKG_STR_HTTP_PORT_DEFAULT="48080"
PKG_STR_HTTPS_PORT="HTTPS port"
PKG_STR_HTTPS_PORT_DEFAULT="48443"
PKG_STR_INVALID_PORT="The port number must be from 1 to 65535."
PKG_STR_LISTEN_INET_ADDR="Listen address"

##
#  NAME
#    create_listen_addr_store
#  SYNOPSIS
#    Build a list of all ip addresses for selection
#  FUNCTION
#    This function is responsible for building list for all ip addresses to listen on.
#  INPUTS
#    -
#  RESULT
#    A list of ip addresses consumable by an Ext.data.ArrayStore
##
function create_listen_addr_store()
{
    # A list with all ip addresses for selection
    local listen_addr_list="[\"0.0.0.0\"], [\"127.0.0.1\"]"
    # Add all ip addresses with scop global to the list
    listen_addr_list+="$(ip -o -f inet addr show | awk '/scope global/ {split($4,addr,"/*"); print " ,[\"" addr[1] "\"]"}' | sort)"

    printf "${listen_addr_list}"
}

##
#  NAME
#    create_install_settings_step
#  SYNOPSIS
#    Build an installation wizard step
#  FUNCTION
#    This function is responsible for building an installation wizard step.
#  INPUTS
#    -
#  RESULT
#    Text consumable by the Synology wizard
##
function create_install_settings_step()
{
    local step=""
    # The default is to listen on all interfaces
    local default_inet_addr="0.0.0.0"
    # A list with possible listen addresses
    local inet_addr_store="$(create_listen_addr_store)"

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
            "type": "combobox",
            "subitems": [{
                "key": "pkgwizard_inet_addr",
                "desc": "${PKG_STR_LISTEN_INET_ADDR}",
                "editable": false,
                "mode": "local",
                "value": "${default_inet_addr}",
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

    if [[ -n "${steps}" ]]
    then
        printf "[${steps}]\n"
    fi
}

##
#  NAME
#    get_install_wizard_steps
#  SYNOPSIS
#    Create an install wizard step
#  FUNCTION
#    This function is responsible for building an an install wizard step.
#  INPUTS
#    -
#  RESULT
#    Text consumable by the Synology wizard
##
function get_install_wizard_steps()
{
    local steps="$(create_install_settings_step)"

    if [[ -n "${steps}" ]]
    then
        printf "[${steps}]\n"
    fi
}

typeset install_wizard_steps="$(get_install_wizard_steps)"

if [[ -z "${get_install_wizard_steps}" ]]
then
    exit 0
fi

printf "${install_wizard_steps}\n" > ${SYNOPKG_TEMP_LOGFILE}

exit 0
