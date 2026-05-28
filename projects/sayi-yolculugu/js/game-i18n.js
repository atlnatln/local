const I18N = {
  tr: {
    levelBadge: 'Seviye {n}',
    commands: 'Komutlar',
    program: 'Programın',
    run: '▶ Çalıştır',
    congrats: '🎉 Tebrikler!',
    retry: '🔄 Tekrar',
    next: '▶ Sonraki',
    levelSelect: 'Seviye Seç',
    close: 'Kapat',
    allCompleteTitle: '🏆 Harika!',
    allCompleteMsg: 'Tüm seviyeleri tamamladın!',
    renewalLoading: '⏳ Yeni seviyeler hazırlanıyor...',
    renewalLoadingMsg: 'Yapay zeka yeni bulmacalar üretiyor, lütfen bekleyin.',

    error: '⚠️ Hata',
    errorMsg: 'Yeni seviyeler hazırlanırken bir sorun oluştu. Lütfen tekrar dene.',
    failTitle: '😕 Hedefine ulaşamadın',
    failValueMsg: 'Sayın {playerVal} — ama hedef {targetVal} olmalıydı.',
    failPosMsg: 'Doğru konuma ulaşamadın. Tekrar dene!',
    winMsgs: ['İyi iş! 💪', 'Harika! 🌟', 'Mükemmel! 🏆'],
    finish: 'Tamam',
    targetDesc: 'Hedefe ulaş!',
    cmdCount: '{current} / {max}',
  },
  en: {
    levelBadge: 'Level {n}',
    commands: 'Commands',
    program: 'Your Program',
    run: '▶ Run',
    congrats: '🎉 Congratulations!',
    retry: '🔄 Retry',
    next: '▶ Next',
    levelSelect: 'Select Level',
    close: 'Close',
    allCompleteTitle: '🏆 Great Job!',
    allCompleteMsg: 'You completed all levels!',
    renewalLoading: '⏳ Preparing new levels...',
    renewalLoadingMsg: 'AI is generating new puzzles, please wait.',

    error: '⚠️ Error',
    errorMsg: 'Something went wrong while preparing new levels. Please try again.',
    failTitle: "😕 You didn't reach the target",
    failValueMsg: 'Your number is {playerVal} — but target should be {targetVal}.',
    failPosMsg: "You didn't reach the right position. Try again!",
    winMsgs: ['Good job! 💪', 'Great! 🌟', 'Excellent! 🏆'],
    finish: 'OK',
    targetDesc: 'Reach the target!',
    cmdCount: '{current} / {max}',
  }
};

let currentLocale = 'tr';

function t(key, vars = {}) {
  const dict = I18N[currentLocale] || I18N['tr'];
  let text = dict[key] || I18N['tr'][key] || key;
  Object.entries(vars).forEach(([k, v]) => {
    text = text.replace(new RegExp('\\{' + k + '\\}', 'g'), v);
  });
  return text;
}

function setLocale(locale) {
  currentLocale = I18N[locale] ? locale : 'tr';
}
