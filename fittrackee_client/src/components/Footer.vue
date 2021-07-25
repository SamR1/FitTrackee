<template>
  <div id="footer">
    <div class="footer-items">
      <div class="footer-item"><strong>FitTrackee</strong> vx.xx</div>
      <div class="footer-item bullet">•</div>
      <div class="footer-item">
        <a
          href="https://github.com/SamR1/FitTrackee"
          target="_blank"
          rel="noopener noreferrer"
        >
          source code
        </a>
        under
        <a
          href="https://choosealicense.com/licenses/gpl-3.0/"
          target="_blank"
          rel="noopener noreferrer"
        >
          GPLv3 </a
        >license
      </div>
      <div class="footer-item bullet">•</div>
      <div class="footer-item">
        <a
          href="https://samr1.github.io/FitTrackee/"
          target="_blank"
          rel="noopener noreferrer"
        >
          documentation
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  #footer {
    display: flex;

    bottom: 0;
    position: absolute;
    width: 100%;

    background: white;
    color: #8b8c8c;
    font-size: 0.9em;

    a {
      text-decoration: none;
    }

    .footer-items {
      display: flex;
      align-content: center;
      justify-content: center;

      width: 100%;

      .footer-item {
        padding: 10px 10px;

        text-align: center;
      }
    }

    @media screen and (max-width: 550px) {
      .footer-items {
        font-size: 0.85em;

        .footer-item {
          padding: 5px 5px;
        }

        .bullet {
          padding: 5px 0;
        }
      }
    }
  }
</style>
