#!/bin/bash

source /pkgscripts/include/pkg_util.sh

package="openHAB"
displayname="openHAB"
version="2.2.0-0004"
firmware="6.0-7312"
arch="noarch"
beta="no"
maintainer="Ingo Theiss"
maintainer_url="https://github.com/itheiss/openhab-synology-spk"
adminprotocol="https"
adminurl="/start/index"
adminport="48443"
install_dep_packages="Java8"
install_replace_packages="openHAB<2.2.0"
helpurl="https://github.com/itheiss/openhab-synology-spk"
report_url="https://github.com/itheiss/openhab-synology-spk"
silent_install="yes"
silent_upgrade="yes"
dsmuidir="ui"
dsmappname="ORG.OPENHAB.Instance"
description="openHAB - a vendor and technology agnostic open source automation software for your home."
description_enu="openHAB - a vendor and technology agnostic open source automation software for your home."
description_ger="openHAB - eine Hersteller- und technologieunabhängige Open-Source-Automatisierungssoftware für Ihr Zuhause."

[ "$(caller)" != "0 NULL" ] && return 0
pkg_dump_info
