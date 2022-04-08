# flake8: noqa

expected_en_text_body = """Hi test,

The password for your FitTrackee account has been changed.

For security, this request was received from a Linux device using Firefox.
If this password change wasn't initiated by you, please change your password immediately or contact your administrator if your account is locked.

Thanks,
The FitTrackee Team
http://localhost"""

expected_en_text_body_without_security = """Hi test,

The password for your FitTrackee account has been changed.

If this password change wasn't initiated by you, please change your password immediately or contact your administrator if your account is locked.

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Le mot de passe de votre compte FitTrackee a été modifié.

Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
Si vous n'êtes pas à l'origine de cette modification, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_fr_text_body_without_security = """Bonjour test,

Le mot de passe de votre compte FitTrackee a été modifié.

Si vous n'êtes pas à l'origine de cette modification, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """  <body>
    <span class="preheader">Your password has been changed.</span>
    <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0" role="presentation">
      <tr>
        <td align="center">
          <table class="email-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
            <tr>
              <td class="email-masthead">
                <a href="http://localhost" class="f-fallback email-masthead-name">
                FitTrackee
              </a>
              </td>
            </tr>
            <tr>
              <td class="email-body" width="100%" cellpadding="0" cellspacing="0">
                <table class="email-body-inner" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell">
                      <div class="f-fallback">
                        <h1>Hi test,</h1>
                        <p>The password for your FitTrackee account has been changed.</p>
                        <p>
                          For security, this request was received from a Linux device using Firefox.
                          If this password change wasn't initiated by you, please change your password immediately or contact your administrator if your account is locked.
                        </p>
                        <p>Thanks,
                          <br>
                          The FitTrackee Team
                        </p>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td>
                <table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell" align="center">
                      <p class="f-fallback sub align-center">&copy; FitTrackee.</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

expected_en_html_body_without_security = """  <body>
    <span class="preheader">Your password has been changed.</span>
    <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0" role="presentation">
      <tr>
        <td align="center">
          <table class="email-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
            <tr>
              <td class="email-masthead">
                <a href="http://localhost" class="f-fallback email-masthead-name">
                FitTrackee
              </a>
              </td>
            </tr>
            <tr>
              <td class="email-body" width="100%" cellpadding="0" cellspacing="0">
                <table class="email-body-inner" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell">
                      <div class="f-fallback">
                        <h1>Hi test,</h1>
                        <p>The password for your FitTrackee account has been changed.</p>
                        <p>
                          If this password change wasn't initiated by you, please change your password immediately or contact your administrator if your account is locked.
                        </p>
                        <p>Thanks,
                          <br>
                          The FitTrackee Team
                        </p>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td>
                <table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell" align="center">
                      <p class="f-fallback sub align-center">&copy; FitTrackee.</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

expected_fr_html_body = """  <body>
    <span class="preheader">Votre mot de passe a été modifié.</span>
    <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0" role="presentation">
      <tr>
        <td align="center">
          <table class="email-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
            <tr>
              <td class="email-masthead">
                <a href="http://localhost" class="f-fallback email-masthead-name">
                FitTrackee
              </a>
              </td>
            </tr>
            <tr>
              <td class="email-body" width="100%" cellpadding="0" cellspacing="0">
                <table class="email-body-inner" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell">
                      <div class="f-fallback">
                        <h1>Bonjour test,</h1>
                        <p>Le mot de passe de votre compte FitTrackee a été modifié.</p>
                        <p>
                          Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
                          Si vous n'êtes pas à l'origine de cette modification, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.
                        </p>
                        <p>Merci,
                          <br>
                          L'équipe FitTrackee
                        </p>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td>
                <table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell" align="center">
                      <p class="f-fallback sub align-center">&copy; FitTrackee.</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

expected_fr_html_body_without_security = """  <body>
    <span class="preheader">Votre mot de passe a été modifié.</span>
    <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0" role="presentation">
      <tr>
        <td align="center">
          <table class="email-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
            <tr>
              <td class="email-masthead">
                <a href="http://localhost" class="f-fallback email-masthead-name">
                FitTrackee
              </a>
              </td>
            </tr>
            <tr>
              <td class="email-body" width="100%" cellpadding="0" cellspacing="0">
                <table class="email-body-inner" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell">
                      <div class="f-fallback">
                        <h1>Bonjour test,</h1>
                        <p>Le mot de passe de votre compte FitTrackee a été modifié.</p>
                        <p>
                          Si vous n'êtes pas à l'origine de cette modification, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.
                        </p>
                        <p>Merci,
                          <br>
                          L'équipe FitTrackee
                        </p>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td>
                <table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0" role="presentation">
                  <tr>
                    <td class="content-cell" align="center">
                      <p class="f-fallback sub align-center">&copy; FitTrackee.</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""
