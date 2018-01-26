# openHAB Synology DiskStation Package

A Synology DiskStation Package for [openHAB](http://www.openhab.org/) exploiting the latest features from Synology DSM 6.0 and onwards. That also means **no** support for Synology DSM versions below 6.0.

**What you can expect:**

* An installation wizard that let you configure the HTTP and HTTPS ports for openHAB
* A [shared folder](https://www.synology.com/en-global/knowledgebase/DSM/help/DSM/AdminCenter/file_share_desc) named *openhab* for all user editable configurations files
* Integration within *Hyper Backup* like native Synology packages
* Usage of [privilege specification](https://developer.synology.com/developer-guide/privilege/privilege_specification.html) to reduce security risks
* Certificate mangement through Synyology DSM. You can create your own certificate from within Synology DSM or get a free Let's Encrypt certificate. No need to manually fiddle around with certificates. Only a few clicks and [openHAB](http://www.openhab.org/) is secured by a trusted and free Let's Encrypt certificate!
* Log rotation managed under the hood by Synology DSM
* An openHAB application integrated in Synology DSM to change the HTTP and HTTPS ports later on

**Accessing openHAB log files**

By default Synology DSM does not enable the following of symbolic links on SMB shares, so access to the openHAB log files is restricted to using an ssh session to the DSM server. If you're using VSCode for editing your rules it is useful to have direct access to the event and openHAB logs within the Code editor so you can see the direct results of your changes.
Accessing the log files via the SMB share can be enabled by opening the DSM Control Panel and applying the following settings to the SMB Files Services Advanced Settings:
- Enable: Allow symbolic links within shared folders
- Enable: Allow symbolic links across shared folders

NOTE: Enabling these options can allow unprivileged users may be able to access the target shared folders of symbolic links
The logs directory can then be accessed by adding a symbolic link on the server:
```shell
ssh <user>@<dsmserver>
cd /volume1/openHAB
sudo ln -s /var/packages/openHAB/target/src/userdata/logs logs
```

Follow the link to  download the latest [openHAB packages](http://spk.i-matrixx.de/?fulllist=true).
Feedback is highly appreciated!
