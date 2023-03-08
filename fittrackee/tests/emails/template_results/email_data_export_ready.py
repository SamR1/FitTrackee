# flake8: noqa

expected_en_text_body = """Hi test,

You have requested an export of your account on FitTrackee.
The archive is now ready to be downloaded from your account.

Download your archive: http://localhost/profile/edit/account
If you did not request the export, please change your password immediately or contact your administrator if your account is locked.

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Vous avez demandé un export des données de votre compte sur FitTrackee.
L'archive est maintenant prête à être téléchargée depuis votre compte.

Télécharger votre archive: http://localhost/profile/edit/account
Si vous n'êtes pas à l'origine de cette demande, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """  <body>
    <span class="preheader">A download link is available in your account.</span>
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
                        <p>You have requested an export of your account on FitTrackee. The archive is now ready to be downloaded from your account.</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/profile/edit/account" class="f-fallback button button--green" target="_blank">Download your archive</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          If you did not request the export, please change your password immediately or contact your administrator if your account is locked.
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">If you're having trouble with the button above, copy and paste the URL below into your web browser.</p>
                              <p class="f-fallback sub">http://localhost/profile/edit/account</p>
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
    <span class="preheader">Un lien de téléchargement est disponible dans votre compte.</span>
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
                        <p>Vous avez demandé un export des données de votre compte sur FitTrackee. L'archive est maintenant prête à être téléchargée depuis votre compte.</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/profile/edit/account" class="f-fallback button button--green" target="_blank">Télécharger votre archive</a>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          Si vous n'êtes pas à l'origine de cette demande, veuillez changer votre mot de passe immédiatement ou contacter l'administrateur si votre compte est bloqué.
                        </p>
                        <p>Merci,
                          <br>L'équipe FitTrackee</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">Si vous avez des problèmes avec le bouton, vous pouvez copier et coller le lien suivant dans votre navigateur.</p>
                              <p class="f-fallback sub">http://localhost/profile/edit/account</p>
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
