function isAndroid() { return typeof Android !== 'undefined'; }

function notifyAndroid(event, data) {
  console.info('[Game] notifyAndroid: ' + event + ' data=' + JSON.stringify(data));
  if (isAndroid()) {
    try { Android.onGameEvent(event, JSON.stringify(data)); } catch(e) { console.error('[Game] notifyAndroid error: ' + e); }
  }
}
