/* ═══════════════════════════════════════════════════════════
   Sayı Yolculuğu — UI Overlays
   ═══════════════════════════════════════════════════════════ */

import { dispatch, getState } from './store.js';
import { getLevels } from './state.js';
import { $ } from './utils.js';

export function updateStarsDisplay(stars) {
  const state = getState();
  const prog = (state.progress[state.ageGroup] || {})[state.levelIdx];
  const s = stars || (prog ? prog.stars : 0);
  let txt = '';
  for (let i = 0; i < 3; i++) txt += (i < s) ? '★' : '☆';
  $('starsDisplay').textContent = txt;
}

export function showWinOverlay(stars) {
  const state = getState();
  const levels = getLevels();
  const overlay = $('overlay');
  $('overlayTitle').textContent = '🎉 Tebrikler!';
  $('overlayTitle').style.color = '#00d68f';

  const s1 = document.getElementById('s1');
  const s2 = document.getElementById('s2');
  const s3 = document.getElementById('s3');

  s1.textContent = stars >= 1 ? '★' : '☆';
  s2.textContent = stars >= 2 ? '★' : '☆';
  s3.textContent = stars >= 3 ? '★' : '☆';
  s1.className = stars >= 1 ? 'star-anim' : '';
  s2.className = stars >= 2 ? 'star-anim' : '';
  s3.className = stars >= 3 ? 'star-anim' : '';
  s1.style.animationDelay = '0s';
  s2.style.animationDelay = '0.15s';
  s3.style.animationDelay = '0.3s';

  const msgs = ['İyi iş! Devam et! 💪', 'Harika! Çok iyi gidiyorsun! 🌟', 'Mükemmel! Tam puan! 🏆'];
  $('overlayMsg').textContent = msgs[stars - 1];
  $('btnNext').style.display = state.levelIdx < levels.length - 1 ? '' : 'none';
  overlay.classList.add('active');
}

export function showLevelSelect(onSelect) {
  const state = getState();
  const levels = getLevels();
  const prog = state.progress[state.ageGroup] || {};
  const grid = $('levelGrid');
  grid.innerHTML = '';

  levels.forEach((lv, i) => {
    const cell = document.createElement('button');
    cell.className = 'level-cell';

    const unlocked = i === 0 || (prog[i - 1] && prog[i - 1].completed);
    if (!unlocked) cell.classList.add('locked');
    if (prog[i] && prog[i].completed) cell.classList.add('completed');
    if (i === state.levelIdx) cell.classList.add('current');

    if (!unlocked) {
      cell.innerHTML = '🔒';
    } else {
      const num = document.createElement('span');
      num.className = 'level-num';
      num.textContent = i + 1;
      cell.appendChild(num);
      if (prog[i]) {
        const stars = document.createElement('span');
        stars.className = 'lc-stars';
        let txt = '';
        for (let s = 0; s < 3; s++) txt += (s < prog[i].stars) ? '★' : '☆';
        stars.textContent = txt;
        cell.appendChild(stars);
      }
    }

    if (unlocked) {
      cell.addEventListener('click', () => {
        dispatch({ type: 'SET_LEVEL_IDX', payload: i });
        $('levelSelect').classList.remove('active');
        if (onSelect) onSelect(i);
      });
    }

    grid.appendChild(cell);
  });

  $('levelSelect').classList.add('active');
}

export function hideOverlay() {
  $('overlay').classList.remove('active');
}

export function hideLevelSelect() {
  $('levelSelect').classList.remove('active');
}

export function showLeaderboard(entries, period) {
  const overlay = $('leaderboardOverlay');
  const list = $('leaderboardList');
  list.innerHTML = '';

  if (!entries || entries.length === 0) {
    list.innerHTML = '<p style="text-align:center;color:var(--text-dim);">Henüz veri yok.</p>';
  } else {
    entries.forEach((entry, i) => {
      const row = document.createElement('div');
      row.className = 'level-cell';
      row.style.display = 'flex';
      row.style.justifyContent = 'space-between';
      row.style.padding = '8px 12px';
      row.style.marginBottom = '4px';
      const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
      row.innerHTML = `<span>${medal} ${entry.child_name}</span><span>⭐ ${entry.total_stars} • ${entry.score} puan</span>`;
      list.appendChild(row);
    });
  }

  document.querySelectorAll('#leaderboardOverlay .age-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.period === period);
  });

  overlay.classList.add('active');
}

export function hideLeaderboard() {
  $('leaderboardOverlay').classList.remove('active');
}
