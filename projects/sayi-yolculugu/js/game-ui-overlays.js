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
  $('btnBuyCredits').style.display = 'none';
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
  $('btnBuyCredits').style.display = 'none';
  allComplete.classList.add('active');
}
function showCreditRequired() {
  console.info('[Game] showCreditRequired');
  $('allCompleteTitle').textContent = t('creditRequired');
  $('allCompleteMsg').textContent = t('creditRequiredMsg');
  $('totalStarsText').style.display = 'none';
  $('allCompleteSpinner').style.display = 'none';
  $('btnFinish').style.display = 'none';
  $('btnBuyCredits').style.display = '';
  allComplete.classList.add('active');
}
function showRenewalError() {
  console.info('[Game] showRenewalError');
  $('allCompleteTitle').textContent = t('error');
  $('allCompleteMsg').textContent = t('errorMsg');
  $('totalStarsText').style.display = 'none';
  $('allCompleteSpinner').style.display = 'none';
  $('btnFinish').style.display = '';
  $('btnBuyCredits').style.display = 'none';
  allComplete.classList.add('active');
}
