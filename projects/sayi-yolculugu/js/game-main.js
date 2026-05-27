const $ = id => document.getElementById(id);
const gridEl = $('grid');
const playerEl = $('player');
const cmdPalette = $('cmdPalette');
const cmdQueue = $('cmdQueue');
const cmdCount = $('cmdCount');
const overlay = $('overlay');
const levelSelect = $('levelSelect');
const allComplete = $('allComplete');

function initGame(levelsJson) {
  // Yeni set yüklendiğinde tamamlama ekranını gizle
  allComplete.classList.remove('active');
  try {
    console.info('[Game] initGame called');
    const data = typeof levelsJson === 'string' ? JSON.parse(levelsJson) : levelsJson;
    levels = data.levels || data;
    const completedIds = data.completed_level_ids || [];
    console.info('[Game] levels count=' + levels.length + ' completedIds=' + JSON.stringify(completedIds));

    // Locale ve forceClear
    if (data.locale) {
      setLocale(data.locale);
    }
    if (data.forceClear) {
      clearGameState();
    }

    window.currentSetId = data.version || data.set_id || null;
    currentSignature = getSetSignature(data);

    state.levelIdx = 0;
    state.progress = {};

    // Her zaman signature değişmişse veya forceClear varsa temizle
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (data.forceClear || parsed.signature !== currentSignature) {
          clearGameState();
        }
      } catch(e) {
        clearGameState();
      }
    }

    // Tamamlanan seviyeleri state.progress'e yükle ve ilk eksik seviyeyi bul
    if (completedIds.length > 0) {
      levels.forEach(function(lv, i) {
        var lvId = lv.id != null ? lv.id : (i + 1);
        if (completedIds.indexOf(lvId) !== -1) {
          state.progress[i] = { completed: true, stars: 1 };
        }
      });
      // İlk tamamlanmamış seviyeye atla
      var firstUncompleted = levels.length; // varsayılan: hepsi tamamlandı
      for (var i = 0; i < levels.length; i++) {
        if (!state.progress[i] || !state.progress[i].completed) {
          firstUncompleted = i;
          break;
        }
      }
      // Hepsi tamamlandıysa levelIdx'yi levels.length yap (loadLevel showAllComplete göstersin)
      state.levelIdx = firstUncompleted < levels.length ? firstUncompleted : levels.length;
    }

    // localStorage'den kaldığı yerden devam et
    const restored = restoreGameState(currentSignature);
    if (restored) {
      const targetIdx = restored.levelIdx;
      if (targetIdx >= 0 && targetIdx < levels.length) {
        var lvId = levels[targetIdx].id != null ? levels[targetIdx].id : (targetIdx + 1);
        var isCompleted = completedIds.indexOf(lvId) !== -1;
        if (!isCompleted) {
          state.levelIdx = targetIdx;
          state.queue = restored.queue || [];
          state.attempts = restored.attempts || 0;
          if (restored.progress) {
            Object.keys(restored.progress).forEach(function(k) {
              var idx = parseInt(k);
              if (!state.progress[idx] || (restored.progress[idx].stars > state.progress[idx].stars)) {
                state.progress[idx] = restored.progress[idx];
              }
            });
          }
        } else {
          clearGameState();
        }
      }
    }
  } catch(e) {
    levels = [];
  }
  if (levels.length === 0) return;

  // Statik UI metinlerini locale'e göre güncelle
  document.querySelector('.cmd-panel h3').textContent = t('commands');
  document.querySelector('.cmd-queue-label h3').textContent = t('program');
  $('btnRun').textContent = t('run');
  $('btnRetry').textContent = t('retry');
  $('btnNext').textContent = t('next');
  document.querySelector('.level-select-card h2').textContent = t('levelSelect');
  $('btnCloseLevels').textContent = t('close');
  $('btnFinish').textContent = t('finish');
  $('btnBuyCredits').textContent = t('buyCredits');

  loadLevel();
}

// Called from Android
window.initGame = initGame;
$('btnRun').addEventListener('click', runProgram);
$('btnClear').addEventListener('click', function() { if (!state.running) { state.queue = []; renderQueue(); saveGameState(); } });
$('btnUndo').addEventListener('click', function() { if (!state.running) { state.queue.pop(); renderQueue(); saveGameState(); } });
$('btnReset').addEventListener('click', function() { if (!state.running) { state.queue = []; state.attempts = 0; loadLevel(); saveGameState(); } });
$('btnRetry').addEventListener('click', function() {
  overlay.classList.remove('active');
  state.queue = [];
  state.attempts = 0;
  loadLevel();
  saveGameState();
});
$('btnNext').addEventListener('click', function() {
  overlay.classList.remove('active');
  if (state.levelIdx < levels.length - 1) {
    state.levelIdx++;
    state.queue = [];
    state.attempts = 0;
    loadLevel();
    saveGameState();
  } else {
    showAllComplete();
  }
});
$('btnFinish').addEventListener('click', function() {
  allComplete.classList.remove('active');
  notifyAndroid('finish', {});
});
$('btnBuyCredits').addEventListener('click', function() {
  notifyAndroid('buyCredits', {});
});
$('btnLevels').addEventListener('click', showLevelSelect);
$('btnCloseLevels').addEventListener('click', function() { levelSelect.classList.remove('active'); });
