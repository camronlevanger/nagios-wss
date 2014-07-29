nagios_wss
==========

A Nagios Web Socket Monitoring Plugin
-------------------------------------

A Nagios NRPE script that allows you to monitor a web socket server using
the WAMP protocol. While it is fairly easy with Nagios to monitor whether
or not your server proccess is running, unfortunately that can't tell us
if that server is available and accepting connections.

With nagios-wss you can actually open a connection to your websocket servers and
have the confidence of knowing that they are responding correctly to your users.

This script is designed to be run on Nagios client servers using the NRPE daemon.

For more information on using Nagios and NRPE visit the following link:

[http://nagios.sourceforge.net/docs/nrpe/](http://nagios.sourceforge.net/docs/nrpe/)

Installation and Usage
----------------------

###Download and Install nagios-wss

####Clone Source and Install Manually
This is a pretty simple option for this small codebase. We will clone the  source into
the directory where we want to keep our Nagios plugins, install the required libraries,
and finally set proper permissions.

	cd /path/to/where/you/want/it
	git clone git@github.com:camronlevanger/nagios-wss.git
	cd nagios-wss
	pip install -r requirements.txt
	chmod +x check_wss_conn.py

Then restart the NRPE service, on Ubuntu that looks like:

	service nagios-nrpe-server restart

####Install Using Pip
Coming Soon

###Add nagios-wss Command to NRPE Client
Now we need to edit our nrpe.cfg file and add our new plugin command.

	vim /etc/nagios/nrpe.cfg

Now add the check_wss_conn command to the list.

	 command[check_wss_conn]=/path/to/where/you/put/it/check_wss_conn.py

By default nagios-wss connects to wss://localhost:8080, if this works for your
setup then the above command config is all that is needed. If that does not reflect
the location of the socket server you need to monitor, you can also pass in the
host as an arg to the command.

To pass args to the command make sure you set in nrpe.cfg

	dont_blame_nrpe=1

And then the host arg is

	-H host_uri

###Add nagios-wss to Nagios Checks on Your Nagios Monitoring Server
Define a new service for nagios-wss

	define service {
		use	generic-service (or your appropriate defined service)
		host_name	name_of_your_client_host
		service_description	Web Socket Server Monitor
		check_command	check_wss_conn
	}

Resart the Nagios host.
