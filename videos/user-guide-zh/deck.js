(function () {
  /**
   * PocketBudJet user-guide deck — tap pulse timing on play (HHH deck.js parity).
   * Main playback lives in index.html; this ensures resume-from-pause schedules pulses.
   */
  document.addEventListener('DOMContentLoaded', function () {
    var playBtn = document.getElementById('playPauseBtn');
    if (!playBtn || playBtn.__pbjTapPulseWired) return;
    playBtn.__pbjTapPulseWired = true;

    playBtn.addEventListener('click', function () {
      var label = document.getElementById('speedLabel');
      if (!label || label.textContent !== 'Auto-playing') return;
      var active = document.querySelector('.slide.active');
      if (!active) return;
      var idx = parseInt(active.getAttribute('data-index'), 10);
      if (isNaN(idx)) return;
      if (window.PBJWalkthrough && window.PBJWalkthrough.scheduleTapPulse) {
        window.PBJWalkthrough.scheduleTapPulse(idx);
      }
    }, true);
  });
})();
