# flake8: noqa

expected_en_text_body = """Hi Test,

Your appeal on your warning has been rejected.

Workout: workout title

Link: http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/

The FitTrackee Team
http://localhost"""

expected_fr_text_body = """Bonjour Test,

Votre appel sur votre avertissement été rejeté.

Séance : workout title

Lien : http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/

L'équipe FitTrackee
http://localhost"""

expected_en_html_body = """<body>
    <span class="preheader">Your appeal has been rejected.</span>
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
                        <p>Your appeal on your warning has been rejected.</p>
                        
                        
                        <p>Workout:</p>
                        <table class="body-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td>
                              <img class="user-picture" src="http://localhost/img/user.png" alt="">
                              <strong>Test</strong>
                            </td>
                          </tr>
                          <tr>
                            <td>workout title</td>
                          </tr>
                          <tr>
                            <td><img class="map" src="http://localhost/workouts/map/ZxB8qgyrcSY6ynNzerfirW" alt=""></td>
                           </tr>
                          <tr>
                            <td class="content-date"><a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/" target="_blank">07/14/2024 - 07:32:47</a></td>
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
    <span class="preheader">Votre appel a été rejeté.</span>
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
                        <p>Votre appel sur votre avertissement été rejeté.</p>
                        
                        
                        <p>Séance :</p>
                        <table class="body-content" width="100%" cellpadding="0" cellspacing="0" role="presentation">
                          <tr>
                            <td>
                              <img class="user-picture" src="http://localhost/img/user.png" alt="">
                              <strong>Test</strong>
                            </td>
                          </tr>
                          <tr>
                            <td>workout title</td>
                          </tr>
                          <tr>
                            <td><img class="map" src="http://localhost/workouts/map/ZxB8qgyrcSY6ynNzerfirW" alt=""></td>
                           </tr>
                          <tr>
                            <td class="content-date"><a href="http://localhost/workouts/CVsE8ERggQcHc7PcCdwGHC/" target="_blank">07/14/2024 - 07:32:47</a></td>
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
