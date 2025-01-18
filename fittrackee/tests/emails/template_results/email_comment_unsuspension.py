# flake8: noqa

expected_en_text_body = """Hi test,

The suspension on your comment has been lifted, it is visible again.

Reason: some reason

Comment: comment text

Link: http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW

The FitTrackee Team
http://localhost"""

expected_en_text_body_without_reason = """Hi test,

The suspension on your comment has been lifted, it is visible again.

Comment: comment text

Link: http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW

The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

La suspension de votre commentaire a été levée, il est visible à nouveau.

Raison : some reason

Commentaire : comment text

Lien : http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW

L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """<body>
    <span class="preheader">The suspension on your comment has been lifted, it is visible again.</span>
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
                        <p>The suspension on your comment has been lifted, it is visible again.</p>
                        <p><strong>Reason:</strong> some reason</p>
                        <table class="body-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td>
                              <img class="user-picture" src="http://localhost/img/user.png" alt="">
                              <strong>test</strong>
                            </td>
                          </tr>
                          <tr>
                            <td>comment text</td>
                          </tr>
                          <tr>
                            <td class="content-date"><a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW" target="_blank">07/14/2024 - 07:32:47</a></td>
                          </tr>
                        </table>
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
    <span class="preheader">La suspension de votre commentaire a été levée, il est visible à nouveau.</span>
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
                        <p>La suspension de votre commentaire a été levée, il est visible à nouveau.</p>
                        <p><strong>Raison :</strong> some reason</p>
                        <table class="body-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td>
                              <img class="user-picture" src="http://localhost/img/user.png" alt="">
                              <strong>test</strong>
                            </td>
                          </tr>
                          <tr>
                            <td>comment text</td>
                          </tr>
                          <tr>
                            <td class="content-date"><a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW" target="_blank">07/14/2024 - 07:32:47</a></td>
                          </tr>
                        </table>
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
    <span class="preheader">The suspension on your comment has been lifted, it is visible again.</span>
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
                        <p>The suspension on your comment has been lifted, it is visible again.</p>
                        
                        <table class="body-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td>
                              <img class="user-picture" src="http://localhost/img/user.png" alt="">
                              <strong>test</strong>
                            </td>
                          </tr>
                          <tr>
                            <td>comment text</td>
                          </tr>
                          <tr>
                            <td class="content-date"><a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW" target="_blank">07/14/2024 - 07:32:47</a></td>
                          </tr>
                        </table>
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
