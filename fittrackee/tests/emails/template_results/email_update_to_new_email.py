# flake8: noqa

expected_en_text_body = """Hi test,

You recently requested to change your email address for your FitTrackee account. Use the link below to confirm this address.

Verify your email: http://localhost/email-update?token=xxx

For security, this request was received from a Linux device using Firefox.
If this email change wasn't initiated by you, please ignore this email.

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Vous avez récemment demandé la modification de l'adresse email associée à votre compte sur FitTrackee.
Cliquez sur le lien ci-dessous pour confirmer cette adresse email.

Vérifier l'adresse email : http://localhost/email-update?token=xxx

Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
Si vous n'êtes pas à l'origine de cette modification, vous pouvez ignorer cet e-mail.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """  <body>
    <span class="preheader">Use this link to confirm email change.</span>
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
                        <p>You recently requested to change your email address for your FitTrackee account. Use the button below to confirm this address.</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/email-update?token=xxx" class="f-fallback button button--green" target="_blank">Verify your email</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          For security, this request was received from a Linux device using Firefox.
                          If this email change wasn't initiated by you, please ignore this email.
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">If you’re having trouble with the button above, copy and paste the URL below into your web browser.</p>
                              <p class="f-fallback sub">http://localhost/email-update?token=xxx</p>
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
    <span class="preheader">Utiliser ce lien pour confirmer cette adresse email.</span>
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
                        <p>Vous avez récemment demandé la modification de l'adresse email associée à votre compte sur FitTrackee.
                          Cliquez sur le bouton ci-dessous pour confirmer cette adresse email.
                        </p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/email-update?token=xxx" class="f-fallback button button--green" target="_blank">Vérifier l'adresse email</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
                          Si vous n'êtes pas à l'origine de cette modification, vous pouvez ignorer cet e-mail.
                        </p>
                        <p>Merci,
                          <br>L'équipe FitTrackee</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">Si vous avez des problèmes avec le bouton, vous pouvez copier et coller le lien suivant dans votre navigateur</p>
                              <p class="f-fallback sub">http://localhost/email-update?token=xxx</p>
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
