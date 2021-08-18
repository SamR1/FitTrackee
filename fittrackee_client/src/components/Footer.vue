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
  @import '~@/scss/base';

  #footer {
    display: flex;

    bottom: 0;
    position: fixed;
    width: 100%;

    background: var(--footer-background-color);
    color: var(--footer-color);
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

        border-top: solid 1px var(--footer-border-color);
        text-align: center;
      }
    }

    @media screen and (max-width: $x-small-limit) {
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
