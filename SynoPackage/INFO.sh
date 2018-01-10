#!/bin/bash

source /pkgscripts/include/pkg_util.sh

build_date="$1"
build_number="$2"

package="openHAB"
version="2.2.0-0002"
displayname="openHAB"
maintainer="Ingo Theiss"
maintainer_url="https://github.com/itheiss/openhab-synology-spk"
arch="noarch"
os_min_ver="6.0"
beta="no"
adminprotocol="https"
adminurl="/start/index"
adminport="48443"
install_dep_packages="Java8"
install_replace_packages="openHAB<2.2.0"
helpurl="https://github.com/itheiss/openhab-synology-spk"
silent_install="yes"
silent_upgrade="yes"
dsmuidir="ui"
dsmappname="ORG.OPENHAB.Instance"
description="openHAB - a vendor and technology agnostic open source automation software for your home."
description_enu="openHAB - a vendor and technology agnostic open source automation software for your home."
description_ger="openHAB - eine Hersteller- und technologieunabhaengige Open-Source-Automatisierungssoftware fuer Ihr Zuhause."
[ "$(caller)" != "0 NULL" ] && return 0
pkg_dump_info
