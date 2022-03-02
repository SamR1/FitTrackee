# flake8: noqa

expected_en_text_body = """Hi test,

You recently requested to reset your password for your FitTrackee account. Use the link below to reset it. This password reset link is only valid for 3 seconds.

Reset your password: http://localhost/password-reset?token=xxx

For security, this request was received from a Linux device using Firefox.
If you did not request a password reset, please ignore this email.

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Vous avez récemment demandé la réinitialisation du mot de passe de votre compte sur FitTrackee.
Cliquez sur le lien ci-dessous pour le réinitialiser. Ce lien n'est valide que pendant 3 secondes.

Réinitialiser le mot de passe : http://localhost/password-reset?token=xxx

Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
Si vous n'avez pas demandé de réinitialisation, vous pouvez ignorer cet e-mail.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """  <body>
    <span class="preheader">Use this link to reset your password. The link is only valid for 3 seconds.</span>
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
                        <p>You recently requested to reset your password for your account. Use the button below to reset it.
                          <strong>This password reset link is only valid for 3 seconds.</strong>
                        </p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/password-reset?token=xxx" class="f-fallback button button--green" target="_blank">Reset your password</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          For security, this request was received from a Linux device using Firefox.
                          If you did not request a password reset, please ignore this email.
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">If you’re having trouble with the button above, copy and paste the URL below into your web browser.</p>
                              <p class="f-fallback sub">http://localhost/password-reset?token=xxx</p>
                            </td>
                          </tr>
                        </table>
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
    <span class="preheader">Utiliser ce lien pour réinitialiser le mot de passe. Ce lien n'est valide que pendant 3 secondes.</span>
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
                        <h1>Bonjour  test,</h1>
                        <p>Vous avez récemment demandé la réinitialisation du mot de passe de votre compte sur FitTrackee.
                          Cliquez sur le bouton ci-dessous pour le réinitialiser.
                          <strong>Cette réinitialisation n'est valide que pendant 3 secondes.</strong>
                        </p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/password-reset?token=xxx" class="f-fallback button button--green" target="_blank">Réinitialiser le mot de passe</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
                          Si vous n'avez pas demandé de réinitialisation, vous pouvez ignorer cet e-mail.
                        </p>
                        <p>Merci,
                          <br>L'équipe FitTrackee</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">Si vous avez des problèmes avec le bouton, vous pouvez copier et coller le lien suivant dans votre navigateur</p>
                              <p class="f-fallback sub">http://localhost/password-reset?token=xxx</p>
                            </td>
                          </tr>
                        </table>
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
