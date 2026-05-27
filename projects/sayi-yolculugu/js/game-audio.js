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

  function playLevelComplete() {
    if (muted) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const now = ctx.currentTime;
      const notes = [
        { f: 523.25, d: 0.10, t: 0.00 },   // C5 — dı
        { f: 523.25, d: 0.10, t: 0.12 },   // C5 — dı
        { f: 523.25, d: 0.10, t: 0.24 },   // C5 — dı
        { f: 659.25, d: 0.12, t: 0.36 },   // E5 — dıt
        { f: 523.25, d: 0.10, t: 0.52 },   // C5 — dı
        { f: 659.25, d: 0.14, t: 0.64 },   // E5 — dıt
      ];
      notes.forEach(function(n) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.frequency.value = n.f;
        osc.type = 'sine';
        gain.gain.setValueAtTime(0.25, now + n.t);
        gain.gain.exponentialRampToValueAtTime(0.001, now + n.t + n.d);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + n.t);
        osc.stop(now + n.t + n.d);
      });
      setTimeout(function() { ctx.close(); }, 1500);
    } catch (e) {}
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
    isMuted: isMuted,
    playLevelComplete: playLevelComplete
  };
})();
