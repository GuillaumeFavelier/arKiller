Albion Online Killboard Bot
===========================

Python Discord bot that provides a killboard for the selected alliance.

Installation instructions
-------------------------

The only requirements are the following python packages:
`json requests time datetime sys configparser collections`

Most of them should be installed by default but if it's not the case you can follow a standard installation procedure by using `python-pip`:

`pip install package_name_here`

Configuration
-------------

You can use the file `example.cfg` as a template. The only required properties are the alliance name and the webhook URL.

Usage
-----

On Linux or Windows:

`python bot.py my_config.cfg`
