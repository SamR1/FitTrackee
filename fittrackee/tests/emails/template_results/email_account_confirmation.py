# flake8: noqa

expected_en_text_body = """Hi test,

You have created an account on FitTrackee account. Use the link below to confirm your address email.

Verify your email: http://localhost/account-confirmation?token=xxx

For security, this request was received from a Linux device using Firefox.
If this account creation wasn't initiated by you, please ignore this email.

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Vous avez créé un sur FitTrackee.
Cliquez sur le lien ci-dessous pour confirmer votre adresse email.

Vérifier l'adresse email : http://localhost/account-confirmation?token=xxx

Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
Si vous n'êtes pas à l'origine de la création de ce compte, vous pouvez ignorer cet e-mail.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """  <body>
    <span class="preheader">Use this link to confirm your account.</span>
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
                        <p>You have created an account on FitTrackee account. Use the link below to confirm your address email.</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/account-confirmation?token=xxx" class="f-fallback button button--green" target="_blank">Verify your email</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          For security, this request was received from a Linux device using Firefox.
                          If this account creation wasn't initiated by you, please ignore this email.
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">If you’re having trouble with the button above, copy and paste the URL below into your web browser.</p>
                              <p class="f-fallback sub">http://localhost/account-confirmation?token=xxx</p>
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
    <span class="preheader">Utiliser ce lien pour confirmer votre inscription.</span>
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
                        <p>Vous avez créé un sur FitTrackee.
                          Cliquez sur le lien ci-dessous pour confirmer votre adresse email.
                        </p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/account-confirmation?token=xxx" class="f-fallback button button--green" target="_blank">Vérifier l'adresse email</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          Pour vérification, cette demande a été reçue à partir d'un appareil sous Linux, utilisant le navigateur Firefox.
                          Si vous n'êtes pas à l'origine de la création de ce compte, vous pouvez ignorer cet e-mail.
                        </p>
                        <p>Merci,
                          <br>L'équipe FitTrackee</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">Si vous avez des problèmes avec le bouton, vous pouvez copier et coller le lien suivant dans votre navigateur</p>
                              <p class="f-fallback sub">http://localhost/account-confirmation?token=xxx</p>
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
