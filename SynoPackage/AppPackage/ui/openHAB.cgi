#!/bin/sh
#
# MIT License
#
# Copyright (c) 2017 Ingo Theiss <ingo.theiss@i-matrixx.de>
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

# Source common definitions
. /var/packages/openHAB/scripts/common

# Source port definitions
. ${OPENHAB_SYNOLOGY_ENV}

# Function get a query string parameter
get_query_param() {
    s='s/^.*'${1}'=\([^&]*\).*$/\1/p;s/%20/ /g'
    echo ${QUERY_STRING} | sed -n "${s}"
}

# Function to load the saved Synology settings
on_load_handler() {
    # Print JSON response
    printf '{'
    printf '"data": {'
    printf '"http_port":"%s",' ${OPENHAB_HTTP_PORT}
    printf '"https_port":"%s"' ${OPENHAB_HTTPS_PORT}
    printf '},'
    printf '"success":true'
    printf '}'
    
    return 0
}

# Function to save the settings from Synology DSM
on_save_handler() {
    # The JSON response 'success' value
    local handler_result="true"

    # Get query/form values
    http_port="$(get_query_param 'http_port')"
    https_port="$(get_query_param 'https_port')"
    do_restart="$(get_query_param 'do_restart')"

    # Save submitted settings
    printf 'export OPENHAB_HTTP_PORT="%s"\n' "${http_port}" > ${OPENHAB_SYNOLOGY_ENV}
    printf 'export OPENHAB_HTTPS_PORT="%s"\n' "${https_port}" >> ${OPENHAB_SYNOLOGY_ENV}

    # The CGI is run as root. Change owner to package.
    ${BIN_CHOWN} ${PACKAGE_NAME}:${PACKAGE_NAME} ${OPENHAB_SYNOLOGY_ENV}

    # Change adminport inside INFO
    sed -i "s/adminport=\"\([0-9]*\)\"/adminport=\"${https_port}\"/g" ${PACKAGE_LOCATION}/INFO

    # Restart openHAB if requested
    if [ ${do_restart} == "true" ]
    then
        # NOTE: The CGI is run as root. To run openHAB with the correct user account we must use synopkgctl to restart app.
        #       If using start-stop-status openHAB will run as root!!!
        ${BIN_SYNOPKGCTL} stop ${PACKAGE_NAME} &>/dev/null && ${BIN_SYNOPKGCTL} start ${PACKAGE_NAME} &>/dev/null
        if [ $? -ne 0 ]
        then
            handler_result="false"
        fi
    fi
    
    # Print JSON response
    printf '{'
    printf '"success":%s' ${handler_result}
    printf '}'
    
    return 0
}

# Print header information
printf 'Content-type: application/json; charset="UTF-8"\n\n'

# Authentication check
auth_user="$(/usr/syno/synoman/webman/modules/authenticate.cgi)"

if [ $? -ne 0 ]
then
    # Print JSON response
    printf '{'
    printf '"success":false'
    printf '}'

    exit 
fi

# Get 'action' parameter
action="$(get_query_param 'action')"

# Print response depending on 'action' parameter
case "${action}" in
    load)
        on_load_handler
        ;;
    save)
        on_save_handler
        ;;
    *)
        # Print JSON response
        printf '{'
        printf '"success":false'
        printf '}'
        ;;        
esac

