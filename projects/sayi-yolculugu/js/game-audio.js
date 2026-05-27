/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — Audio Engine (HTML5 <audio>)
   ═══════════════════════════════════════════════════════════ */

(function() {
  'use strict';

  const AUDIO_PATH = 'audio/';

  const SOUNDS = {
    click:  { src: AUDIO_PATH + 'click.wav',  vol: 0.5 },
    bump:   { src: AUDIO_PATH + 'bump.wav',   vol: 0.6 },
    success:{ src: AUDIO_PATH + 'success.wav',vol: 0.5 },
  };

  const BGM = { src: AUDIO_PATH + 'bgm.wav', vol: 0.15 };

  let bgmEl = null;
  let muted = false;
  let loaded = false;

  function loadSettings() {
    try {
      const raw = localStorage.getItem('sy_settings');
      if (raw) {
        const s = JSON.parse(raw);
        if (typeof s.audio === 'boolean') muted = !s.audio;
      }
    } catch (e) {}
  }

  function saveSettings() {
    try {
      const raw = localStorage.getItem('sy_settings');
      const s = raw ? JSON.parse(raw) : {};
      s.audio = !muted;
      localStorage.setItem('sy_settings', JSON.stringify(s));
    } catch (e) {}
  }

  function play(name) {
    if (muted) return;
    const cfg = SOUNDS[name];
    if (!cfg) return;
    try {
      const el = new Audio(cfg.src);
      el.volume = cfg.vol;
      el.play().catch(function(){});
    } catch (e) {}
  }

  function playBGM() {
    if (muted || bgmEl) return;
    try {
      bgmEl = new Audio(BGM.src);
      bgmEl.volume = BGM.vol;
      bgmEl.loop = true;
      bgmEl.play().catch(function(){});
    } catch (e) {}
  }

  function stopBGM() {
    if (bgmEl) {
      try {
        bgmEl.pause();
        bgmEl.currentTime = 0;
      } catch (e) {}
      bgmEl = null;
    }
  }

  function setMuted(v) {
    muted = !!v;
    saveSettings();
    if (muted) {
      stopBGM();
    } else {
      playBGM();
    }
  }

  function isMuted() {
    return muted;
  }

  loadSettings();

  window.AudioEngine = {
    play: play,
    playBGM: playBGM,
    stopBGM: stopBGM,
    setMuted: setMuted,
    isMuted: isMuted
  };
})();
