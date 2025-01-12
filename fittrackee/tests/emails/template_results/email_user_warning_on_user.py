# flake8: noqa

expected_en_text_body = """Hi Test,

You received a warning.

Reason: some reason

If you think this is an error, you can appeal:
http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal

Thanks,
The FitTrackee Team
http://localhost"""

expected_en_text_body_without_reason = """Hi Test,

You received a warning.

If you think this is an error, you can appeal:
http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour Test,

Vous avez reçu un avertissement.

Raison : some reason

Si vous pensez qu'il s'agit d'une erreur, vous pouvez faire appel :
http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """<body>
    <span class="preheader">You received a warning.</span>
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
                        <h1>Hi Test,</h1>
                        <p>You received a warning.</p>
                        <p>Reason: some reason</p>
                        
                        
                        <p>If you think this is an error, you can appeal:</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal" class="f-fallback button button--green" target="_blank">Appeal</a>
                                  </td>
                                </tr>
                               </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">If you're having trouble with the button above, copy and paste the URL below into your web browser.</p>
                              <p class="f-fallback sub">http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal</p>
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
  </body>"""

expected_fr_html_body = """<body>
    <span class="preheader">Vous avez reçu un avertissement.</span>
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
                        <h1>Bonjour Test,</h1>
                        <p>Vous avez reçu un avertissement.</p>
                        <p>Raison : some reason</p>
                        
                        
                        <p>Si vous pensez qu'il s'agit d'une erreur, vous pouvez faire appel :</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal" class="f-fallback button button--green" target="_blank">Faire appel</a>
                                  </td>
                                </tr>
                               </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          
                        </p>
                        <p>Merci,
                          <br>L'équipe FitTrackee</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">Si vous avez des problèmes avec le bouton, vous pouvez copier et coller le lien suivant dans votre navigateur.</p>
                              <p class="f-fallback sub">http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal</p>
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
  </body>"""

expected_en_html_body_without_reason = """<body>
    <span class="preheader">You received a warning.</span>
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
                        <h1>Hi Test,</h1>
                        <p>You received a warning.</p>
                        
                        
                        
                        <p>If you think this is an error, you can appeal:</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td align="center">
                              <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                                <tr>
                                  <td align="center">
                                    <a href="http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal" class="f-fallback button button--green" target="_blank">Appeal</a>
                                  </td>
                                </tr>
                               </table>
                            </td>
                          </tr>
                        </table>
                        <p>
                          
                        </p>
                        <p>Thanks,
                          <br>The FitTrackee Team</p>
                        <table class="body-sub" role="presentation">
                          <tr>
                            <td>
                              <p class="f-fallback sub">If you're having trouble with the button above, copy and paste the URL below into your web browser.</p>
                              <p class="f-fallback sub">http://localhost/profile/warning/mf2FVvtogeMCoJV4yS8Cnp/appeal</p>
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
  </body>"""
