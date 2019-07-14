Administrator
#############


`JSON.parse: unexpected character at line 1 column 1 of the JSON data`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On the **Network Tab**, if the requests are made to `http://localhost:3000/undefined/api`, that means the environnement variable **REACT_APP_API_URL** is not initialized.

Check if **Makefile.custom.config** file exists and **REACT_APP_API_URL** is correctly initialized (see `example <https://github.com/SamR1/FitTrackee/blob/master/Makefile.custom.config.example>`__), and rebuild the client.
