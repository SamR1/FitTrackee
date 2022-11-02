Third-party applications
########################
(*new in 0.7.0*)

FitTrackee provides a REST API (see `documentation <api/index.html>`__) whose
most endpoints require authentication/authorization.

To allow a third-party application to interact with API endpoints, an
`OAuth2 <https://datatracker.ietf.org/doc/html/rfc6749>`_ client can be created
in user settings ('apps' tab).

.. warning::
  OAuth2 endpoints requiring authentication are not accessible by third-party
  applications (`documentation <api/oauth2.html>`__), only by FitTrackee
  client (first-party application).

FitTrackee supports only `Authorization Code <https://datatracker.ietf.org/doc/html/rfc6749#section-1.3.1>`_
flow (with `PKCE <https://datatracker.ietf.org/doc/html/rfc7636>`_ support).
It allows to exchange an authorization code for an access token.
The client ID and secret must be sent in the POST body.
It is recommended to use PKCE to provide a better security.

Scopes
~~~~~~

The following scopes are available:

- ``application:write``: grants write access to application configuration (only for users with administration rights),
- ``profile:read``: grants read access to auth endpoints,
- ``profile:write``: grants write access to auth endpoints,
- ``users:read``: grants read access to users endpoints,
- ``users:write``: grants write access to users endpoints,
- ``workouts:read``: grants read access to workouts-related endpoints,
- ``workouts:write``: grants write access to workouts-related endpoints.


Flow
~~~~

- The user creates an App (client) on FitTrackee for a third-party application.

  .. figure:: _images/fittrackee_screenshot-07.png
   :alt: OAuth2 client creation on FitTrackee

  | After registration, the client id and secret are shown.
  | They must be stored in the 3rd-party application by the user.

- | The 3rd-party app needs to redirect to FitTrackee, in order for the user to authorize the 3rd-party app to access user data on FitTrackee.

  .. figure:: _images/fittrackee_screenshot-08.png
   :alt: App authorization on FitTrackee

  | The authorization URL is ``https://<FITTRACKEE_HOST>/profile/apps/authorize``.
  | The required parameters are:

  - ``client_id``: the client id displayed after registration
  - ``response_type``:  ``code``, since FitTrackee only supports Authorization Code flow.
  - ``scope``: scopes separated with space.

  | and optional parameters:

  - ``state``: unique value to prevent cross-site request forgery

  | For PKCE, the following parameters are mandatory:

  - ``code_challenge``: string generated from a code verifier
  - ``code_challenge_method``: method used to create challenge, for instance "S256"

  | Example for PKCE:
  | `https://<FITTRACKEE_HOST>/profile/apps/authorize?response_type=code&client_id=<CLIENT_ID>&scope=profile%3Aread+workouts%3Awrite&state=<STATE>&code_challenge=<CODE_CHALLENGE>&code_challenge_method=S256`


- | After the authorization, FitTrackee redirects to the 3rd-party app, so the 3rd-party app can get the authorization code from the redirect URL and then fetches an access token with the client id and secret (endpoint `/api/oauth/token <https://samr1.github.io/FitTrackee/api/oauth2.html#post--api-oauth-token>`_).
  | Example of a redirect URL:
  | `https://example.com/callback?code=<AUTHORIZATION_CODE>&state=<STATE>`


.. note::
  OAuth2 support is implemented with `Authlib <https://docs.authlib.org/en/latest/>`_ library.

.. warning::
  | If FitTrackee is running behind a proxy, the ``X-Forwarded-Proto`` header must be set.
  | For instance for `nginx`:

  .. code-block::

     proxy_set_header  X-Forwarded-Proto $scheme;

Resources
~~~~~~~~~

Some resources about OAuth 2.0:

- `OAuth 2.0 Simplified <https://www.oauth.com>`_ by `Aaron Parecki <https://aaronparecki.com>`_ (example for `authorization code flow with PKCE <https://www.oauth.com/oauth2-servers/server-side-apps/example-flow/>`_)
- `Web App Example of OAuth 2 web application flow <https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html>`_ with Requests-OAuthlib (python)
- `OAuth 2 Session <https://docs.authlib.org/en/latest/client/oauth2.html#oauth-2-session>`_ with Authlib (python)
- `Minimal example of an application interacting with FitTrackee <https://codeberg.org/SamR1/ft-oauth-client>`_ (python)