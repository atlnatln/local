function showWinOverlay(stars) {
  $('overlayTitle').textContent = t('congrats');
  $('overlayStars').textContent = '⭐'.repeat(stars) + '☆'.repeat(3 - stars);
  var msgs = t('winMsgs');
  $('overlayMsg').textContent = Array.isArray(msgs) ? msgs[stars - 1] : 'Good job!';
  $('btnNext').style.display = state.levelIdx < levels.length - 1 ? '' : 'none';
  overlay.classList.add('active');
}
function updateStarsDisplay() {
  var prog = state.progress[state.levelIdx];
  var s = prog ? prog.stars : 0;
  $('starsDisplay').textContent = '⭐'.repeat(s) + '☆'.repeat(3 - s);
}
function showAllComplete() {
  console.info('[Game] showAllComplete called');
  var totalStars = 0;
  var maxStars = levels.length * 3;
  for (var k in state.progress) {
    if (state.progress[k].stars) totalStars += state.progress[k].stars;
  }
  $('allCompleteTitle').textContent = t('allCompleteTitle');
  $('allCompleteMsg').textContent = t('allCompleteMsg');
  $('totalStarsText').textContent = '⭐ ' + totalStars + ' / ' + maxStars;
  $('totalStarsText').style.display = '';
  $('allCompleteSpinner').style.display = 'none';
  $('btnFinish').style.display = '';
  allComplete.classList.add('active');

  notifyAndroid('allComplete', {
    totalLevels: levels.length,
    totalCompleted: Object.keys(state.progress).length,
    totalStars: totalStars,
    maxStars: maxStars,
    byLevel: state.progress
  });
  clearGameState();
}
function showRenewalLoading() {
  console.info('[Game] showRenewalLoading');
  $('allCompleteTitle').textContent = t('renewalLoading');
  $('allCompleteMsg').textContent = t('renewalLoadingMsg');
  $('totalStarsText').style.display = 'none';
  $('allCompleteSpinner').style.display = 'block';
  $('btnFinish').style.display = 'none';
  allComplete.classList.add('active');
}
/* ── Pause Overlay ──────────────────────────────────────── */
function showPause() {
  if (state.running) return;
  $('pauseOverlay').classList.add('active');
}
function hidePause() {
  $('pauseOverlay').classList.remove('active');
}

function showRenewalError() {
  console.info('[Game] showRenewalError');
  $('allCompleteTitle').textContent = t('error');
  $('allCompleteMsg').textContent = t('errorMsg');
  $('totalStarsText').style.display = 'none';
  $('allCompleteSpinner').style.display = 'none';
  $('btnFinish').style.display = '';
  allComplete.classList.add('active');
}

/* ── Tutorial Overlay ───────────────────────────────────── */
let tutorialSteps = [];
let tutorialIndex = 0;
let tutorialClickHandler = null;

function getTutorialKey(levelIdx) {
  return 'sy_tutorial_' + (window.currentSetId || 'default') + '_' + levelIdx;
}
function isTutorialShown(levelIdx) {
  try { return localStorage.getItem(getTutorialKey(levelIdx)) === '1'; } catch(e) { return false; }
}
function markTutorialShown(levelIdx) {
  try { localStorage.setItem(getTutorialKey(levelIdx), '1'); } catch(e) {}
}
function showTutorial(steps) {
  if (!steps || steps.length === 0) return;
  tutorialSteps = steps;
  tutorialIndex = 0;
  $('tutorialOverlay').style.display = 'block';
  $('tutorialOverlay').classList.add('active');
  renderTutorialStep();
  // Kullanıcı herhangi bir yere tıklayınca next step
  tutorialClickHandler = function() { nextTutorialStep(); };
  document.addEventListener('click', tutorialClickHandler);
}
function renderTutorialStep() {
  const step = tutorialSteps[tutorialIndex];
  const bubble = $('tutorialBubble');
  const pointer = $('tutorialPointer');
  const text = $('tutorialText');
  if (!step) { dismissTutorial(); return; }

  const target = document.querySelector(step.target);
  if (!target) { dismissTutorial(); return; }

  text.textContent = step.text;
  const rect = target.getBoundingClientRect();
  const px = rect.left + rect.width / 2;
  const py = rect.top + rect.height / 2;

  pointer.style.left = px + 'px';
  pointer.style.top = py + 'px';

  const bubbleH = 80;
  const offset = 20;
  let bx = px - 130;
  let by = rect.top - bubbleH - offset;
  let above = false;

  if (by < 10) {
    by = rect.bottom + offset;
    above = true;
  }
  if (bx < 10) bx = 10;
  if (bx + 260 > window.innerWidth - 10) bx = window.innerWidth - 270;

  bubble.style.left = bx + 'px';
  bubble.style.top = by + 'px';
  if (above) bubble.classList.add('above');
  else bubble.classList.remove('above');
}
function nextTutorialStep() {
  tutorialIndex++;
  if (tutorialIndex >= tutorialSteps.length) {
    dismissTutorial();
  } else {
    renderTutorialStep();
  }
}
function dismissTutorial() {
  $('tutorialOverlay').classList.remove('active');
  $('tutorialOverlay').style.display = 'none';
  if (tutorialClickHandler) {
    document.removeEventListener('click', tutorialClickHandler);
    tutorialClickHandler = null;
  }
  tutorialSteps = [];
  tutorialIndex = 0;
}

/* ── Achievement Toast ──────────────────────────────────── */
const ACHIEVEMENT_DEFS = {
  first_win: { icon: '🏆', name: 'İlk Zafer' },
  perfect_3: { icon: '⭐', name: 'Mükemmel' },
  speedster: { icon: '⚡', name: 'Hızlı' },
  no_mistake: { icon: '🎯', name: 'Tek Atış' },
  ten_levels: { icon: '💪', name: 'Dayanıklı' },
};

function showAchievementToast(id) {
  const def = ACHIEVEMENT_DEFS[id];
  if (!def) return;
  const toast = document.createElement('div');
  toast.className = 'achievement-toast';
  toast.textContent = def.icon + ' ' + def.name;
  document.body.appendChild(toast);
  setTimeout(function() { toast.remove(); }, 3600);
}
