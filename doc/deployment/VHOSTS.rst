Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess pta_export-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/pta_export/log/apache2/error.log"
        CustomLog "/srv/sites/pta_export/log/apache2/access.log" common

        WSGIProcessGroup pta_export-<target>

        Alias /media "/srv/sites/pta_export/media/"
        Alias /static "/srv/sites/pta_export/static/"

        WSGIScriptAlias / "/srv/sites/pta_export/src/pta_export/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-pta_export-<target>]
    user = <user>
    command = /srv/sites/pta_export/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/pta_export/src/pta_export/wsgi/wsgi_<target>.py
    home = /srv/sites/pta_export/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/pta_export/log/uwsgi_err.log
    stdout_logfile = /srv/sites/pta_export/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_pta_export_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/pta_export/log/nginx-access.log;
      error_log /srv/sites/pta_export/log/nginx-error.log;

      location /500.html {
        root /srv/sites/pta_export/src/pta_export/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/pta_export/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/pta_export/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_pta_export_<target>;
      }
    }
