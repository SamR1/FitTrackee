# flake8: noqa

expected_en_text_body = """Hi test,

Your account has been reactivated.
You can now use all the features on FitTrackee.

Reason: some reason

The FitTrackee Team
http://localhost"""

expected_en_text_body_without_reason = """Hi test,

Your account has been reactivated.
You can now use all the features on FitTrackee.

The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Votre compte a été réactivé.
Vous pouvez désormais utiliser toutes les fonctionnalités de FitTrackee.

Raison : some reason

L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """<body>
    <span class="preheader">Your account has been reactivated. You can now use all the features on FitTrackee.</span>
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
                        <p>Your account has been reactivated. You can now use all the features on FitTrackee.</p>
                        <p>Reason: some reason</p>
                        <p>
                          
                        </p>
                        <p>The FitTrackee Team</p>
                        
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
    <span class="preheader">Votre compte a été réactivé. Vous pouvez désormais utiliser toutes les fonctionnalités de FitTrackee.</span>
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
                        <p>Votre compte a été réactivé. Vous pouvez désormais utiliser toutes les fonctionnalités de FitTrackee.</p>
                        <p>Raison : some reason</p>
                        <p>
                          
                        </p>
                        <p>L'équipe FitTrackee</p>
                        
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
    <span class="preheader">Your account has been reactivated. You can now use all the features on FitTrackee.</span>
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
                        <p>Your account has been reactivated. You can now use all the features on FitTrackee.</p>
                        
                        <p>
                          
                        </p>
                        <p>The FitTrackee Team</p>
                        
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
