# flake8: noqa

expected_en_text_body = """Hi test,

You recently requested to change your email address for your FitTrackee account to: new.email@example.com

For security, this request was received from a Linux device using Firefox.
If this email change wasn't initiated by you, please change your password immediately or contact your administrator if your account is locked.

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Vous avez récemment demandé la modification de l'adresse email associée à votre compte sur FitTrackee vers : new.email@example.com

Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
Si vous n'êtes pas à l'origine de cette modification, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """  <body>
    <span class="preheader">Your email is being updated.</span>
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
                        <p>You recently requested to change your email address for your FitTrackee account to:</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    new.email@example.com
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          For security, this request was received from a Linux device using Firefox.
                          If this email change wasn't initiated by you, please change your password immediately or contact your administrator if your account is locked.
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        
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
    <span class="preheader">Votre adresse email est en cours de mise à jour.</span>
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
                        <p>Vous avez récemment demandé la modification de l'adresse email associée à votre compte sur FitTrackee vers :</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    new.email@example.com
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
                          Si vous n'êtes pas à l'origine de cette modification, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.
                        </p>
                        <p>Merci,
                          <br>L'équipe FitTrackee</p>
                        
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
