#!/bin/bash

source /pkgscripts/include/pkg_util.sh

build_number="$1"

package="openHAB"
version="2.3.0-${build_number}"
displayname="openHAB"
maintainer="Ingo Theiss"
maintainer_url="https://github.com/itheiss/openhab-synology-spk"
arch="noarch"
os_min_ver="6.0"
beta="yes"
adminprotocol="https"
adminurl="/start/index"
adminport="48443"
install_dep_packages="Java8"
install_replace_packages="openHAB<2.3.0"
helpurl="https://github.com/itheiss/openhab-synology-spk"
silent_install="yes"
silent_upgrade="yes"
dsmuidir="ui"
dsmappname="ORG.OPENHAB.Instance"
description="openHAB - a vendor and technology agnostic open source automation software for your home."
description_enu="openHAB - a vendor and technology agnostic open source automation software for your home."
description_ger="openHAB - eine Hersteller- und technologieunabhängige Open-Source-Automatisierungssoftware für Ihr Zuhause."
[ "$(caller)" != "0 NULL" ] && return 0
pkg_dump_info
