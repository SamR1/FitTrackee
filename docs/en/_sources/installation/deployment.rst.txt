Deployment
##########

.. important::

    This documentation does not detail how to secure a server. Please refer to the documentation and best practices corresponding to your installation and operating system.

| There are several ways to start **FitTrackee** web application and task queue library.
| One way is to use a **systemd** services and **Nginx** to proxy pass to **Gunicorn**.

Examples:

.. warning::
    To adapt depending on your instance configuration and operating system.

- for application: ``fittrackee.service``

.. code-block::

    [Unit]
    Description=FitTrackee service
    After=network.target
    After=postgresql.service
    After=redis.service
    StartLimitIntervalSec=0

    [Service]
    Type=simple
    Restart=always
    RestartSec=1
    User=<USER>
    StandardOutput=journal
    StandardError=journal
    Environment="APP_SECRET_KEY="
    Environment="APP_LOG="
    Environment="UPLOAD_FOLDER="
    Environment="DATABASE_URL="
    Environment="UI_URL="
    Environment="EMAIL_URL="
    Environment="SENDER_EMAIL="
    Environment="REDIS_URL="
    Environment="TILE_SERVER_URL="
    Environment="STATICMAP_SUBDOMAINS="
    Environment="MAP_ATTRIBUTION="
    Environment="WEATHER_API_KEY="
    Environment="STATICMAP_CACHE_DIR="
    WorkingDirectory=/home/<USER>/<FITTRACKEE DIRECTORY>
    ExecStart=/home/<USER>/<FITTRACKEE DIRECTORY>/.venv/bin/gunicorn -b 127.0.0.1:5000 "fittrackee:create_app()" --error-logfile /home/<USER>/<FITTRACKEE DIRECTORY>/gunicorn.log
    Restart=always

    [Install]
    WantedBy=multi-user.target


.. seealso::
    To handle large files, a higher value for `timeout <https://docs.gunicorn.org/en/stable/settings.html#timeout>`__ can be set.

.. seealso::
    More information on deployment with Gunicorn in its `documentation <https://docs.gunicorn.org/en/stable/deploy.html>`__.

- for task queue workers: ``fittrackee_workers.service``

.. code-block::

    [Unit]
    Description=FitTrackee task queue service
    After=network.target
    After=postgresql.service
    After=redis.service
    StartLimitIntervalSec=0

    [Service]
    Type=simple
    Restart=always
    RestartSec=1
    User=<USER>
    StandardOutput=journal
    StandardError=journal
    Environment="FLASK_APP=fittrackee"
    Environment="APP_SECRET_KEY="
    Environment="APP_LOG="
    Environment="UPLOAD_FOLDER="
    Environment="DATABASE_URL="
    Environment="UI_URL="
    Environment="EMAIL_URL="
    Environment="SENDER_EMAIL="
    Environment="REDIS_URL="
    Environment="TASKS_TIME_LIMIT="
    Environment="STATICMAP_CACHE_DIR="
    WorkingDirectory=/home/<USER>/<FITTRACKEE DIRECTORY>
    ExecStart=/home/<USER>/<FITTRACKEE DIRECTORY>/.venv/bin/dramatiq fittrackee.tasks:broker --processes=<NUMBER OF PROCESSES> --log-file=<DRAMATIQ_LOG_FILE_PATH>
    Restart=always

    [Install]
    WantedBy=multi-user.target

.. note::
    Command to be adapted to run queues separately.

.. seealso::
    More information on **Dramatiq** CLI in its `documentation <https://dramatiq.io/guide.html#workers>`__.

- **Nginx** configuration:

.. code-block::

    server {
        listen 443 ssl http2;
        server_name example.com;
        ssl_certificate fullchain.pem;
        ssl_certificate_key privkey.pem;

        ## this parameter controls how large of a file can be
        ## uploaded, and defaults to 1MB. If you change the FitTrackee
        ## settings to allow larger uploads, you'll need to change this
        ## setting by uncommenting the line below and setting the size limit
        ## you want. Set to "0" to prevent nginx from checking the
        ## request body size at all
        # client_max_body_size 1m;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_redirect    default;
            proxy_set_header  Host $host;
            proxy_set_header  X-Real-IP $remote_addr;
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header  X-Forwarded-Host $server_name;
            proxy_set_header  X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 80;
        server_name example.com;
        location / {
            return 301 https://example.com$request_uri;
        }
    }

.. seealso::
    If needed, update configuration to handle larger files (see `client_max_body_size <https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size>`_).
