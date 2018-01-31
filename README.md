# openHAB Synology DiskStation Package

A Synology DiskStation Package for [openHAB](http://www.openhab.org/) exploiting the latest features from Synology DSM 6.0 and onwards. That also means **no** support for Synology DSM versions below 6.0.

**What you can expect:**

* An installation wizard that let you configure the HTTP and HTTPS ports for openHAB
* A [shared folder](https://www.synology.com/en-global/knowledgebase/DSM/help/DSM/AdminCenter/file_share_desc) named *openhab* for all user editable configurations files and log files for easy research
* Integration within *Hyper Backup* like native Synology packages
* Usage of [privilege specification](https://developer.synology.com/developer-guide/privilege/privilege_specification.html) to reduce security risks
* Certificate mangement through Synyology DSM. You can create your own certificate from within Synology DSM or get a free Let's Encrypt certificate. No need to manually fiddle around with certificates. Only a few clicks and [openHAB](http://www.openhab.org/) is secured by a trusted and free Let's Encrypt certificate!
* Daily log rotation managed by openHAB with a custom logging configuration
* An openHAB application integrated in Synology DSM to change the HTTP and HTTPS ports later on

**openHAB directory layout**

If you want to get your hands dirty and are addicted working with the command line here is the directory layout of the openHAB package on your Synology NAS:

![openHAB directory layout](openhab_synopkg_layout.png)

**Download Synology openHAB packages**

Follow the link to download the latest [openHAB packages](http://spk.i-matrixx.de/?fulllist=true). Please download the desired package manually and do **NOT** add the location as a repository.
Feedback is highly appreciated!
