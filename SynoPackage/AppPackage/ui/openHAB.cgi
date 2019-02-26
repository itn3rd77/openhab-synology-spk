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

# Source common definitions
. /var/packages/openHAB/scripts/common

# Source setting from Synology openHAB WebUI
. ${OPENHAB_SYNOLOGY_ENV}

# Script name
typeset SCRIPT_NAME="${0##*/}"

# Query parameters
typeset -A query_parameters

##
#  NAME
#    handle_request
#  SYNOPSIS
#    Processes HTTP requests
#  FUNCTION
#    This function is responsible for processing HTTP requests incl. file upload.
#    After processing the query paramters are available in the global array 'query_parameters'
#  INPUTS
#    Various CGI environment variables
#  RESULT
#    -
##
function handle_request
{
	# The JSON response 'success' value
	local result="true"
	# The result message
	local message="form_apply_ok"
	# Return code
	local -i rc=0

	# Handling a POST request
	if [[ "${REQUEST_METHOD}" = "POST" && -n "${CONTENT_LENGTH}" ]]
	then
		# Handling a file upload
		if [[ "${CONTENT_TYPE}" =~ ^multipart/form-data\;\ *boundary=([^\;]+) ]]
		then
			# The boundary delimiter
			local boundary="--${BASH_REMATCH[1]}"
			# The first line with the boundary
			local boundary_line
			# The line containing the Content-Disposition
			local content_disposition_line
			# The line the Content-Type
			local content_type_line
			# Empty line before the content
			local empty_line

			# Read multipart information
			read boundary_line
			read content_disposition_line
			read content_type_line
			read empty_line

			# Remove newline from variable
			boundary_line="${boundary_line//[$'\r\n']}"
			content_disposition_line="${content_disposition_line//[$'\r\n']}"
			content_type_line="${content_type_line//[$'\r\n']}"

			local upload_file_tmp="/dev/null"

			# Extract field name and optional filename from 'Content-Disposition'
			if [[ "${content_disposition_line}" =~ ^Content-Disposition:\ *form-data\;\ *name=\"([^\"]+)\"(\;\ *filename=\"([^\"]+)\")? ]]
			then
				local action="${BASH_REMATCH[1]}"
				local upload_filename="${BASH_REMATCH[3]}"
				local filename="${upload_filename%.*}"
				local file_extension="${upload_filename##*.}"

				upload_file_tmp="/tmp/${filename//[^[:alnum:]]/_}.${file_extension}"
			fi

			# binary-read until boundary
			sed -n -e "{:loop p; n;/^${boundary}/q; b loop}" >"${upload_file_tmp}"
			# remove last \r\n
			truncate -s -2 "${upload_file_tmp}"

			if [[ -s "${upload_file_tmp}" ]]
			then
				result="false"
				message="upload_file_error"
			fi

			# Set QUERY_STRING for further processing of the request
			QUERY_STRING="action=${action}&filename=${upload_file_tmp}"
		elif [[ -z "${QUERY_STRING}" ]]
		then
			read -n ${CONTENT_LENGTH} QUERY_STRING
		fi
	fi

	# Finally parse the query string
	local -a query_string
	local OIFS=${IFS}

	IFS="=&";query_string=(${QUERY_STRING});IFS="${OIFS}"

	for (( i=0; i<${#query_string[@]}; i+=2 ))
	do
		query_parameters[${query_string[i]}]=$(url_decode ${query_string[i+1]})
	done

	return 0
}

##
#  NAME
#    send_response
#  SYNOPSIS
#    Send HTTP response in JSON format
#  FUNCTION
#    This function is responsible for sending a HTTP JSON response.
#  INPUTS
#    -c		- Content-type of the response (defaults to "application/json")
#    -p		- Additional payload besides the mandatory "success" element
#    -r     - Result of the mandatory "success" element (true or false)
#  RESULT
#    HTTP response written to stdout
##
function send_response
{
	# JSON 'success' value
	local result="false"
	# Payload data to add
	local payload
	# The content type to send
	local content_type="application/json"
	# Position of the next command line argument
	local OPTIND

	while getopts ":c:p:r:" opt
	do
		case "$opt" in
			c )
				content_type="${OPTARG}"
				;;
			p )
				payload="${OPTARG}"
				;;
			r )
				result="${OPTARG}"
				;;
			\? )
				payload="$(printf '"message": "%s"' "Invalid option: -${OPTARG}")"
				result="false"
				break
				;;
			: )
				payload="$(printf '"message": "%s"' "Option -${OPTARG} requires an argument")"
				result="false"
				break
				;;
		esac
	done

	shift $((OPTIND-1))

	# Print header information
	printf 'Content-type: %s; charset="UTF-8"\n\n' "${content_type}"

	# Print JSON response
	printf '{'

	# Add the payload to the response
	if [[ -n "${payload}" ]]
	then
		printf '%s,' "${payload}"
	fi

	printf '"success": %s' "${result}"
	printf '}'

	exit 0
}

##
#  NAME
#    url_decode
#  SYNOPSIS
#    Decode URL parameters
#  FUNCTION
#    This function is responsible for decoding the URL parameters.
#  INPUTS
#    $1		- URL paramter to decode
#  RESULT
#    The decoded URL parameter
##
function url_decode
{
	local url_encoded="${1//+/ }"
	printf '%b' "${url_encoded//%/\\x}"
}

##
#  NAME
#    restart_openhab
#  SYNOPSIS
#    Restart openHAB
#  FUNCTION
#    This function is responsible for restarting the openHAB instance.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function restart_openhab {
	# Return code
	local -i rc=0

	# NOTE: The CGI is run as root. To run openHAB with the correct user account we must use synopkgctl to restart.
	#		If using start-stop-status openHAB will run as root!!!
	${BIN_SYNOPKGCTL} stop ${PACKAGE_NAME} > /dev/null 2>&1 && ${BIN_SYNOPKGCTL} start ${PACKAGE_NAME} > /dev/null 2>&1
	rc=${?}

	return ${rc}
}

##
#  NAME
#    http_ports_handler
#  SYNOPSIS
#    Return the stored http ports
#  FUNCTION
#    This function returns the stored http ports stored inside the file derived by the variable ${OPENHAB_SYNOLOGY_ENV}.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function http_ports_handler
{
	# Return code
	local -i rc=0

	# Response data
	local payload="$(printf '"data": {"http_port": "%s", "https_port": "%s"}' "${OPENHAB_HTTP_PORT}" "${OPENHAB_HTTPS_PORT}")"

	send_response -r "true" -p "${payload}"
	rc=${?}

	return ${rc}
}

##
#  NAME
#    network_settings_handler
#  SYNOPSIS
#    Save network settings from Synology openHAB WebUI
#  FUNCTION
#    This function is responsible storing the network settings from Synology openHAB WebUI
#    to the file derived by the variable ${OPENHAB_SYNOLOGY_ENV}.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function network_settings_handler
{
	# The JSON response 'success' value
	local result="true"
	# The result message
	local message="form_apply_ok"
	# Return code
	local -i rc=0

    # Save submitted settings
    local http_port_cfg="$(printf 'export OPENHAB_HTTP_PORT="%s"' "${query_parameters[http_port]}")"
    sed -i "/export OPENHAB_HTTP_PORT.*/c\\${http_port_cfg}" ${OPENHAB_SYNOLOGY_ENV} > /dev/null 2>&1
    
    local https_port_cfg="$(printf 'export OPENHAB_HTTPS_PORT="%s"' "${query_parameters[https_port]}")"
    sed -i "/export OPENHAB_HTTPS_PORT.*/c\\${https_port_cfg}" ${OPENHAB_SYNOLOGY_ENV} > /dev/null 2>&1
    
    local http_address_cfg="$(printf 'export OPENHAB_HTTP_ADDRESS="%s"' "${query_parameters[http_address]}")"
    sed -i "/export OPENHAB_HTTP_ADDRESS.*/c\\${http_address_cfg}" ${OPENHAB_SYNOLOGY_ENV} > /dev/null 2>&1

	# The CGI is run as root. Change owner to package.
	${BIN_CHOWN} ${PACKAGE_NAME}:${PACKAGE_NAME} ${OPENHAB_SYNOLOGY_ENV} > /dev/null 2>&1

	# Change adminport inside INFO
	sed -i "s|adminport=\"\([0-9]*\)\"|adminport=\"${https_port}\"|g" ${PACKAGE_LOCATION}/INFO > /dev/null 2>&1
	rc=${?}

	if [[ ${rc} != 0 ]]
	then
		result="false"
		message="adminport_err"
	fi

	# Update port config
	sed -i "s|dst.ports=\"${OPENHAB_HTTP_PORT}/tcp\"|dst.ports=\"${http_port}/tcp\"|g; s|dst.ports=\"${OPENHAB_HTTPS_PORT}/tcp\"|dst.ports=\"${https_port}/tcp\"|g" ${PACKAGE_TARGET_LOCATION}/etc/openHAB.sc > /dev/null 2>&1
	rc=${?}

	if [[ ${rc} != 0 ]]
	then
		result="false"
		message="protocol_file_err"
	fi

	${BIN_SERVICETOOL} --install-configure-file --package ${PACKAGE_TARGET_LOCATION}/etc/openHAB.sc > /dev/null 2>&1
	rc=${?}

	if [[ ${rc} != 0 ]]
	then
		result="false"
		message="protocol_file_err"
	fi

	# Restart openHAB
	if [[ "${result}" == "true" ]]
	then
		restart_openhab
		rc=${?}

		if [[ ${rc} != 0 ]]
		then
			result="false"
			message="openhab_restart_err"
		fi
	fi

	# Response data
	local payload="$(printf '"message": "%s"' "${message}")"

	send_response -r "${result}" -p "${payload}"
	rc=${?}

	return ${rc}
}

##
#  NAME
#    version_properties_handler
#  SYNOPSIS
#    Return content of openHAB version.properties
#  FUNCTION
#    This function is responsible for returning the content of openHAB version.properties.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function version_properties_handler
{
	# The JSON response 'success' value
	local result="true"
	# The result message
	local message="version_properties_ok"
	# Return code
	local -i rc=0
	# Content of openHAB version.properties
	local version_properties=""
	
	if [[ -f ${PACKAGE_TARGET_LOCATION}/src/userdata/etc/version.properties ]]
	then
		version_properties="$(<${PACKAGE_TARGET_LOCATION}/src/userdata/etc/version.properties)"
	else
		result="false"
		message="version_properties_err"	
	fi

	# Response data
	local payload="$(printf '"message": "%s", "data": {"version_properties": "%s"}' "${message}" "${version_properties//$'\n'/\\n}")"

	send_response -r "${result}" -p "${payload}"
	rc=${?}

	return ${rc}
}

##
#  NAME
#    http_address_handler
#  SYNOPSIS
#    Return a list of network addresses to use as the openHAB listening address
#  FUNCTION
#    This function is responsible for returning a list of network addresses to use as the openHAB listening address.
#    The special addresses '0.0.0.0' and '127.0.0.1' are returned per default. Additionaly all addresses from the ip command
#    with scope 'global' are returned.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function http_address_handler
{
	# Return code
	local -i rc=0
	# Number of objects in the JSON data field
	local total=1
	# Flag to indicate if the address is selected per default
	local isDefault="false"
	# The final objects for the JSON data field
	local address_store=""
	# An array with all ip addresses for selection
	local inet_addr_list=(0.0.0.0 127.0.0.1)

	# Add all ip addresses with scop global to the list
	inet_addr_list+=($(ip -o -f inet addr show | awk '/scope global/ {split($4,addr,"/*"); print addr[1]}' | sort))

	# Built the JSON objects for the JSON data field
	for inet_addr in "${inet_addr_list[@]}"
	do
		[[ "${OPENHAB_HTTP_ADDRESS}" == "${inet_addr}" ]] && isDefault="true"

		if [[ -z "${address_store}" ]]
		then
			address_store="{\"http_address\":\"${inet_addr}\",\"default\":${isDefault}}"
		else
			address_store+=",{\"http_address\":\"${inet_addr}\",\"default\":${isDefault}}"
		fi

		# Reset default flag
		isDefault="false"

		(( total++ ))
	done

	# Response data
	local payload="$(printf '"total": "%s", "data": [%s]' "${total}" "${address_store}")"

	send_response -r "true" -p "${payload}"
	rc=${?}

	return ${rc}
}

##
#  NAME
#    cacert_handler
#  SYNOPSIS
#    Add a CA certificate to the openHAB Java trust store
#  FUNCTION
#    This function is responsible for adding a uploaded CA certificate to the openHAB Java trust store.
#    After adding the certificate to the trust store a restart of openHAB is performed.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function cacert_handler
{
	# JSON response 'success' value
	local result="true"
	# JSON result message
	local message="form_apply_ok"
	# Absolue path of the uploaded certificate
	local ca_cert="${query_parameters[filename]}"
	# Absolute path to the JAVA trust store
	local key_store="${PACKAGE_TARGET_LOCATION}/src/userdata/etc/openhab-truststore.jks"
	# Standard error output
	local stderr=""
	# Return code
	local -i rc=0

	# Check if uploaded certificate is processible
	stderr="$(openssl x509 -in "${ca_cert}" -text -noout > /dev/null)"
	rc=${?}

	if [[ ${rc} == 0 ]]
	then
        # The alias for the trust store is build upon the CN
        cert_alias="$(openssl x509 -in ${ca_cert} -text -noout 2> /dev/null | grep "Subject:")"
        cert_alias="${cert_alias##* CN=}"
        cert_alias="${cert_alias%%,*}"

		${BIN_JAVA_KEYTOOL} -delete -alias "${cert_alias}" -keystore "${key_store}" -storepass "changeit" > /dev/null 2>&1
		stderr="$(${BIN_JAVA_KEYTOOL} -import -noprompt -trustcacerts -file "${ca_cert}" -alias "${cert_alias}" -keystore "${key_store}" -storepass "changeit" > /dev/null)"
		rc=${?}

		if [[ ${rc} == 0 ]]
		then
			# The JAVA_OPTS_TRUSTSTORE setting is inserted at line 4. REMEMBER TO CHANGE IN CASE MORE OPTIONS ARE ADDED!
			local java_trust_store_cfg="$(printf 'export JAVA_OPTS_TRUSTSTORE="%s"' "-Djavax.net.ssl.trustStore=${key_store} -Djavax.net.ssl.trustStorePassword=changeit")"
			sed -i "/export JAVA_OPTS_TRUSTSTORE/d;4s|^|${java_trust_store_cfg}\n|" ${OPENHAB_SYNOLOGY_ENV}  > /dev/null 2>&1

			# The CGI is run as root. Change owner to package.
			${BIN_CHOWN} ${PACKAGE_NAME}:${PACKAGE_NAME} ${OPENHAB_SYNOLOGY_ENV} ${key_store} > /dev/null 2>&1
		else
			# keytool import failed
			result="false"
			message="keytool_import_failed"
			logger -p user.error -t ${SCRIPT_NAME} "Failed to to import ${ca_cert} into Java trust store ${key_store}: ${stderr}"
		fi
	else
		# uploaded certificate was not processible
		result="false"
		message="cacert_check_failed"
		logger -p user.error -t ${SCRIPT_NAME} "The uploaded certificate ${ca_cert} is not valid: ${stderr}"
	fi

	# Restart openHAB
	if [[ "${result}" == "true" ]]
	then
		restart_openhab
		rc=${?}

		if [[ ${rc} != 0 ]]
		then
			result="false"
			message="openhab_restart_err"
		fi
	fi

	# Delete temporary upload file
	rm -f "${ca_cert}"

	# Response data
	local payload="$(printf '"error_message": "%s"' "${message}")"

	send_response -c "text/html" -r "${result}" -p "${payload}"
	rc=${?}

	return ${rc}
}

##
#  NAME
#    delete_ca_trust_store_handler
#  SYNOPSIS
#    Delete the openHAB Java trust store
#  FUNCTION
#    This function is responsible for deleteting the openHAB Java trust store.
#    After deleting the trust store a restart of openHAB is performed.
#  INPUTS
#    -
#  RESULT
#    0		- on success
#    >0		- on error
##
function delete_cacert_handler
{
	# JSON response 'success' value
	local result="true"
	# JSON result message
	local message="delete_ca_trust_store_ok"
	# Absolute path to the Java trust store
	local key_store="${PACKAGE_TARGET_LOCATION}/src/userdata/etc/openhab-truststore.jks"
	# Standard error output
	local stderr=""
	# Return code
	local -i rc=0

	# Delete Java trust store
	if [[ -f ${key_store} ]]
	then
		stderr="$(rm ${key_store} > /dev/null)"
		rc=${?}
	fi

	if [[ ${rc} == 0 ]]
	then
		# Delete JAVA_OPTS_TRUSTSTORE export from file
		sed -i '/export JAVA_OPTS_TRUSTSTORE/d' ${OPENHAB_SYNOLOGY_ENV}
	else
		result="false"
		message="delete_cacert_err"
		logger -p user.error -t ${SCRIPT_NAME} "Failed to remove Java trust store ${key_store}: ${stderr}"
	fi

	# Restart openHAB
	if [[ "${result}" == "true" ]]
	then
		restart_openhab
		rc=${?}

		if [[ ${rc} != 0 ]]
		then
			result="false"
			message="openhab_restart_err"
		fi
	fi

	# Response data
	local payload="$(printf '"error_message": "%s"' "${message}")"

	send_response -r "${result}" -p "${payload}"
	rc=${?}

	return ${rc}
}

# Authentication check
typeset auth_user="$(/usr/syno/synoman/webman/modules/authenticate.cgi)"

if [[ ${?} != 0 ]]
then
	logger -p user.error -t ${SCRIPT_NAME} "User not authenticated"
	send_response -r "false"
	exit
fi

# Process the request
handle_request

# Get 'action' parameter
typeset action="${query_parameters[action]}"
# Derive the handler name from the action
typeset function_name="${action}_handler"

if [[ "$(type -t ${function_name})" == "function" ]]
then
	${function_name}
else
	logger -p user.error -t ${SCRIPT_NAME} "Unknown action parameter received: ${action}"
	send_response -r "false"
fi

exit 0