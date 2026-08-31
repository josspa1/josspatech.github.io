/**
 * HHH user-manual deck — PBJ-parity transcript + chapter jump.
 * Keeps HHH timed tap pulses via shared walkthrough.js.
 */
(function () {
  // Longer gaps so viewers can follow taps / reorient between steps.
  var CHANGE_BUFFER_MS = 900;
  var SAME_BUFFER_MS = 450;
  var FALLBACK_WPM_MS = 380;
  var MIN_FALLBACK_MS = 1500;
  var MAX_FALLBACK_MS = 12000;
  var SLIDE_DURATION = 8000;

  var slides = document.querySelectorAll('.slide');
  var dotsContainer = document.getElementById('dots');
  var playBtn = document.getElementById('playPauseBtn');
  var voiceBtn = document.getElementById('voiceBtn');
  var prevBtn = document.getElementById('prevBtn');
  var nextBtn = document.getElementById('nextBtn');
  var speedLabel = document.getElementById('speedLabel');
  var tapStart = document.getElementById('tapToStart');
  var narrationPanel = document.getElementById('narrationPanel');
  var transcriptBody = document.getElementById('transcriptBody');
  var chapterBtns = document.querySelectorAll('.chapter-btn');

  var recordMode = /[?&]record=1/.test(location.search);
  if (recordMode) document.body.classList.add('record-mode');

  // Prefer live chapter pills over stale CHAPTER_STARTS constants.
  var CHAPTER_STARTS = Array.prototype.map.call(chapterBtns, function (btn) {
    return parseInt(btn.getAttribute('data-slide'), 10) || 0;
  });
  if (!CHAPTER_STARTS.length && typeof window.CHAPTER_STARTS !== 'undefined') {
    CHAPTER_STARTS = window.CHAPTER_STARTS.slice();
  }

  var audioBase = typeof AUDIO_BASE !== 'undefined' ? AUDIO_BASE : 'audio/';
  var lastSlide = typeof LAST_SLIDE !== 'undefined' ? LAST_SLIDE : slides.length - 1;
  var narration = typeof NARRATION !== 'undefined' ? NARRATION : [];

  var slideSentences = [];
  var allSentences = [];
  var current = 0;
  var playing = false;
  var audioUnlocked = false;
  var voiceEnabled = true;
  var slideAudio = null;
  var timer = null;
  var advanceTimeout = null;
  var sentenceInterval = null;
  var audioHighlightReady = false;
  var userScrolling = false;
  var scrollIdleTimer = null;

  function splitSentences(text) {
    return String(text)
      .split(/(?<=[.!?])\s+/)
      .map(function (s) { return s.trim(); })
      .filter(Boolean);
  }

  function appendSentenceSpan(para, text, slideIdx, sentIdx) {
    if (sentIdx > 0) para.appendChild(document.createTextNode(' '));
    var span = document.createElement('span');
    span.className = 'transcript-sentence';
    span.setAttribute('data-slide', String(slideIdx));
    span.setAttribute('data-sentence', String(sentIdx));
    span.textContent = text;
    para.appendChild(span);
  }

  function buildTranscript() {
    if (!transcriptBody) return;
    transcriptBody.innerHTML = '';
    slideSentences = [];
    allSentences = [];
    narration.forEach(function (text, slideIdx) {
      var para = document.createElement('p');
      para.className = 'transcript-para' + (slideIdx === 0 ? ' current' : '');
      para.setAttribute('data-slide', String(slideIdx));
      para.setAttribute('data-index', String(slideIdx));
      splitSentences(text).forEach(function (part, si) {
        appendSentenceSpan(para, part, slideIdx, si);
      });
      transcriptBody.appendChild(para);
      slideSentences[slideIdx] = Array.from(para.querySelectorAll('.transcript-sentence'));
      allSentences = allSentences.concat(slideSentences[slideIdx]);
    });
  }

  function updateChapterActive(slideIdx) {
    if (!chapterBtns.length) return;
    chapterBtns.forEach(function (btn) { btn.classList.remove('active'); });
    var active = chapterBtns[0];
    for (var i = CHAPTER_STARTS.length - 1; i >= 0; i--) {
      if (slideIdx >= CHAPTER_STARTS[i]) {
        active = chapterBtns[i];
        break;
      }
    }
    if (active) active.classList.add('active');
    try {
      if (window.parent && window.parent !== window) {
        window.parent.postMessage({
          type: 'jt-guide-chapter',
          slide: slideIdx,
          label: active ? (active.textContent || '').trim() : ''
        }, '*');
      }
    } catch (e) { /* ignore */ }
  }

  function stopSentenceTimer() {
    clearInterval(sentenceInterval);
    sentenceInterval = null;
  }

  function stopAudio() {
    if (slideAudio) {
      slideAudio.onended = null;
      slideAudio.onerror = null;
      slideAudio.ontimeupdate = null;
      slideAudio.onloadedmetadata = null;
      slideAudio.pause();
      slideAudio.removeAttribute('src');
      try { slideAudio.load(); } catch (e) { /* ignore */ }
      slideAudio = null;
    }
    clearTimeout(advanceTimeout);
    stopSentenceTimer();
    audioHighlightReady = false;
  }

  function resetSlideSentences(slideIdx) {
    allSentences.forEach(function (span) {
      span.classList.remove('active');
      var s = parseInt(span.getAttribute('data-slide'), 10);
      if (s < slideIdx) span.classList.add('past');
      else span.classList.remove('past');
    });
  }

  function setActiveSentence(slideIdx, sentIdx) {
    allSentences.forEach(function (span) {
      span.classList.remove('active');
      var s = parseInt(span.getAttribute('data-slide'), 10);
      var n = parseInt(span.getAttribute('data-sentence'), 10);
      if (s < slideIdx || (s === slideIdx && n < sentIdx)) span.classList.add('past');
      else span.classList.remove('past');
    });
    var spans = slideSentences[slideIdx];
    if (!spans || !spans.length) return;
    var idx = Math.min(sentIdx, spans.length - 1);
    var active = spans[idx];
    active.classList.add('active');
    if (!userScrolling && narrationPanel) {
      var panelRect = narrationPanel.getBoundingClientRect();
      var elRect = active.getBoundingClientRect();
      if (elRect.top < panelRect.top + 40 || elRect.bottom > panelRect.bottom - 40) {
        active.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }

  function syncSentenceToAudio(slideIdx) {
    if (!slideAudio || !slideAudio.duration || !playing || !audioHighlightReady) return;
    var spans = slideSentences[slideIdx];
    if (!spans || !spans.length) return;
    var idx = Math.min(
      Math.floor((slideAudio.currentTime / slideAudio.duration) * spans.length),
      spans.length - 1
    );
    setActiveSentence(slideIdx, idx);
  }

  function startSentenceSync(slideIdx, durationMs) {
    stopSentenceTimer();
    var spans = slideSentences[slideIdx];
    if (!spans || !spans.length) return;
    var idx = 0;
    var perMs = Math.max(400, durationMs / spans.length);
    setActiveSentence(slideIdx, 0);
    sentenceInterval = setInterval(function () {
      if (!playing) return;
      idx += 1;
      if (idx >= spans.length) {
        stopSentenceTimer();
        return;
      }
      setActiveSentence(slideIdx, idx);
    }, perMs);
  }

  function slideImgKey(i) {
    var s = slides[i];
    if (!s) return '';
    var img = s.querySelector('img[src]');
    if (img) return img.getAttribute('src') || '';
    return 'placeholder:' + i;
  }

  function advanceDelayMs(fromIndex) {
    var idx = fromIndex !== undefined ? fromIndex : current;
    var next = idx < lastSlide ? idx + 1 : 0;
    return slideImgKey(idx) === slideImgKey(next) ? SAME_BUFFER_MS : CHANGE_BUFFER_MS;
  }

  function estimateReadMs(i) {
    if (narration[i]) {
      var words = String(narration[i]).split(/\s+/).filter(Boolean).length;
      return Math.min(MAX_FALLBACK_MS, Math.max(MIN_FALLBACK_MS, words * FALLBACK_WPM_MS));
    }
    return 4000;
  }

  function scheduleAdvance(ms) {
    clearTimeout(advanceTimeout);
    advanceTimeout = setTimeout(function () {
      if (!playing) return;
      if (current < lastSlide) {
        goTo(current + 1);
      } else {
        playing = false;
        if (playBtn) playBtn.innerHTML = '&#9654;';
        if (speedLabel) speedLabel.textContent = 'Finished';
        stopAudio();
      }
    }, ms);
  }

  function playSlideAudio(i) {
    stopAudio();
    if (!voiceEnabled) {
      startSentenceSync(i, estimateReadMs(i));
      scheduleAdvance(estimateReadMs(i) + advanceDelayMs(i));
      return;
    }
    if (!playing) return;
    startSentenceSync(i, SLIDE_DURATION);
    slideAudio = new Audio(audioBase + 'slide-' + i + '.mp3');
    slideAudio.loop = false;
    slideAudio.volume = 1;
    slideAudio.ontimeupdate = function () {
      audioHighlightReady = true;
      syncSentenceToAudio(i);
    };
    slideAudio.onloadedmetadata = function () {
      if (!slideAudio || !slideAudio.duration || !isFinite(slideAudio.duration)) return;
      startSentenceSync(i, Math.max(1500, slideAudio.duration * 1000));
    };
    slideAudio.onended = function () {
      if (!playing || !voiceEnabled) return;
      scheduleAdvance(advanceDelayMs(i));
    };
    slideAudio.onerror = function () {
      scheduleAdvance(estimateReadMs(i) + advanceDelayMs(i));
    };
    var p = slideAudio.play();
    if (p && typeof p.then === 'function') {
      p.then(function () {
        audioUnlocked = true;
        audioHighlightReady = true;
        if (tapStart) tapStart.classList.add('hidden');
      }).catch(function () {
        scheduleAdvance(estimateReadMs(i) + advanceDelayMs(i));
      });
    }
  }

  function goTo(index) {
    index = Math.max(0, Math.min(index, lastSlide));
    if (window.PBJWalkthrough && window.PBJWalkthrough.clearTapPulse) {
      window.PBJWalkthrough.clearTapPulse();
    }
    slides.forEach(function (s, j) { s.classList.toggle('active', j === index); });
    if (dotsContainer && dotsContainer.children.length) {
      Array.prototype.forEach.call(dotsContainer.children, function (d, j) {
        d.classList.toggle('active', j === index);
      });
    }
    current = index;
    updateChapterActive(current);
    resetSlideSentences(current);
    if (window.PBJWalkthrough && window.PBJWalkthrough.syncTranscriptSlide) {
      window.PBJWalkthrough.syncTranscriptSlide(current);
    } else if (transcriptBody) {
      transcriptBody.querySelectorAll('.transcript-para').forEach(function (p) {
        p.classList.toggle('current', parseInt(p.getAttribute('data-slide'), 10) === current);
      });
    }
    if (playing) {
      if (speedLabel) {
        speedLabel.textContent = current === lastSlide ? 'Last step' : 'Auto-playing';
      }
      if (voiceEnabled) playSlideAudio(current);
      else {
        startSentenceSync(current, estimateReadMs(current));
        scheduleAdvance(estimateReadMs(current) + advanceDelayMs(current));
      }
      if (window.PBJWalkthrough && window.PBJWalkthrough.scheduleTapPulse) {
        window.PBJWalkthrough.scheduleTapPulse(current);
      }
    } else {
      stopAudio();
      clearTimeout(timer);
      // Keep the current sentence gold-highlighted while paused / on load
      setActiveSentence(current, 0);
    }
  }

  function startPlayback() {
    audioUnlocked = true;
    playing = true;
    if (tapStart) tapStart.classList.add('hidden');
    if (playBtn) playBtn.innerHTML = '&#10074;&#10074;';
    if (speedLabel) speedLabel.textContent = 'Auto-playing';
    goTo(current);
  }

  // Build dots if empty (some HHH builds omit them)
  if (dotsContainer && !dotsContainer.children.length) {
    for (var di = 0; di <= lastSlide; di++) {
      (function (i) {
        var dot = document.createElement('div');
        dot.className = 'dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('data-slide', String(i));
        dot.addEventListener('click', function () { goTo(i); });
        dotsContainer.appendChild(dot);
      })(di);
    }
  } else if (dotsContainer) {
    Array.prototype.forEach.call(dotsContainer.children, function (d) {
      d.addEventListener('click', function () {
        goTo(parseInt(d.getAttribute('data-slide') || d.dataset.slide, 10));
      });
    });
  }

  if (playBtn) {
    playBtn.addEventListener('click', function () {
      if (!audioUnlocked) {
        startPlayback();
        return;
      }
      playing = !playing;
      if (playing) {
        playBtn.innerHTML = '&#10074;&#10074;';
        if (speedLabel) speedLabel.textContent = 'Auto-playing';
        goTo(current);
      } else {
        playBtn.innerHTML = '&#9654;';
        if (speedLabel) speedLabel.textContent = 'Paused';
        stopAudio();
        clearTimeout(timer);
        if (window.PBJWalkthrough && window.PBJWalkthrough.clearTapPulse) {
          window.PBJWalkthrough.clearTapPulse();
        }
      }
    });
  }

  if (tapStart) tapStart.addEventListener('click', startPlayback);

  if (voiceBtn) {
    voiceBtn.addEventListener('click', function () {
      voiceEnabled = !voiceEnabled;
      voiceBtn.classList.toggle('muted', !voiceEnabled);
      if (!voiceEnabled) {
        stopAudio();
        if (playing) {
          startSentenceSync(current, estimateReadMs(current));
          scheduleAdvance(estimateReadMs(current) + advanceDelayMs(current));
        }
      } else if (playing) {
        playSlideAudio(current);
      }
    });
  }

  chapterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var idx = parseInt(btn.getAttribute('data-slide'), 10);
      if (isNaN(idx)) return;
      jumpToSlide(idx);
    });
  });

  function jumpToSlide(idx) {
    idx = Math.max(0, Math.min(idx, lastSlide));
    if (!audioUnlocked || !playing) {
      current = idx;
      startPlayback();
      return;
    }
    goTo(idx);
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      jumpToSlide(current - 1);
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      jumpToSlide(current + 1);
    });
  }

  if (transcriptBody) {
    transcriptBody.addEventListener('click', function (e) {
      var target = e.target;
      if (!target || !target.closest) return;
      var slideEl = target.closest('[data-slide]');
      if (!slideEl || !transcriptBody.contains(slideEl)) return;
      var idx = parseInt(slideEl.getAttribute('data-slide'), 10);
      if (isNaN(idx)) return;
      jumpToSlide(idx);
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') jumpToSlide(current + 1);
    if (e.key === 'ArrowLeft') jumpToSlide(current - 1);
    if (e.key === ' ') {
      e.preventDefault();
      if (playBtn) playBtn.click();
    }
  });

  if (narrationPanel) {
    narrationPanel.addEventListener('scroll', function () {
      userScrolling = true;
      clearTimeout(scrollIdleTimer);
      scrollIdleTimer = setTimeout(function () { userScrolling = false; }, 2500);
    }, { passive: true });
  }

  function jumpFromHash() {
    var hash = location.hash || '';
    var m = hash.match(/^#chapter=(\d+)$/);
    if (!m) return;
    var slide = parseInt(m[1], 10);
    if (isNaN(slide) || slide < 0 || slide > lastSlide) return;
    if (!audioUnlocked) startPlayback();
    goTo(slide);
  }
  window.addEventListener('hashchange', jumpFromHash);

  buildTranscript();
  setActiveSentence(0, 0);
  goTo(0);
  jumpFromHash();
  if (window.initWalkthroughSlides) window.initWalkthroughSlides();
  if (recordMode) startPlayback();

  window.addEventListener('message', function (e) {
    var data = e && e.data;
    if (!data || data.type !== 'jt-guide-goto') return;
    var idx = parseInt(data.slide, 10);
    if (isNaN(idx)) return;
    jumpToSlide(idx);
  });
})();
