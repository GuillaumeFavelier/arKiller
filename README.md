Albion Online Killboard Bot
===========================

Self_hosted Discord bot written in Python that provides a killboard for the selected alliance.

Installation instructions
-------------------------

The only requirements are the following python packages:
`json requests time datetime sys configparser collections`

Most of them should be installed by default but if it's not the case you can follow a standard installation procedure by using `python-pip`:

`pip install package_name_here`

Configuration
-------------

You can use the file `example.cfg` as a template. The only required properties are the alliance name and the webhook URL.

* alliance

Name of the input alliance that will used as a source for events.

* webhook

Webhook URL to the discord text channel used as killboard.

* avatar

URL to a customized avatar image used in embed object.

* package_size

Number of elements to fetch for one request.

* sleep_time

Time in seconds between fetching informations.

Usage
-----

On Linux or Windows:

`python bot.py my_config.cfg`


To-Do list
----------
- [ ] Add informations for assist kills.
- [ ] Improve error handling in network requests.
- [ ] Add a filter for guild instead of alliance.
