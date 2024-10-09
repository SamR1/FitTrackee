# flake8: noqa

expected_en_text_body = """Hi test,

Your comment has been suspended, it is no longer visible.

Reason: some reason

Comment: comment text

If you think this is an error, you can appeal:
http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW

Thanks,
The FitTrackee Team
http://localhost"""

expected_en_text_body_without_reason = """Hi test,

Your comment has been suspended, it is no longer visible.

Comment: comment text

If you think this is an error, you can appeal:
http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW

Thanks,
The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour test,

Votre commentaire a été suspendu, il n'est plus visible.

Raison : some reason

Commentaire : comment text

Si vous pensez qu'il s'agit d'une erreur, vous pouvez faire appel :
http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW

Merci,
L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """<body>
    <span class="preheader">Your comment has been suspended, it is no longer visible.</span>
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
                        <p>Your comment has been suspended, it is no longer visible.</p>
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
                        <p>If you think this is an error, you can appeal:</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                          <td align="center">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                              <tr>
                                <td align="center">
                                  <a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW" class="f-fallback button button--green" target="_blank">Appeal</a>
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
                              <p class="f-fallback sub">http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW</p>
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
    <span class="preheader">Votre commentaire a été suspendu, il n'est plus visible.</span>
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
                        <p>Votre commentaire a été suspendu, il n'est plus visible.</p>
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
                        <p>Si vous pensez qu'il s'agit d'une erreur, vous pouvez faire appel :</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                          <td align="center">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                              <tr>
                                <td align="center">
                                  <a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW" class="f-fallback button button--green" target="_blank">Faire appel</a>
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
                              <p class="f-fallback sub">http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW</p>
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
    <span class="preheader">Your comment has been suspended, it is no longer visible.</span>
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
                        <p>Your comment has been suspended, it is no longer visible.</p>
                        
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
                        <p>If you think this is an error, you can appeal:</p>
                        <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                          <td align="center">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" role="presentation">
                              <tr>
                                <td align="center">
                                  <a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW" class="f-fallback button button--green" target="_blank">Appeal</a>
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
                              <p class="f-fallback sub">http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/comments/ZxB8qgyrcSY6ynNzerfirW</p>
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
