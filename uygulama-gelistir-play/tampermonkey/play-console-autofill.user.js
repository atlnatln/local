// ==UserScript==
// @name         Google Play Console - Uygulama Otomatik Oluştur
// @namespace    https://uygulama-gelistir-play
// @version      1.3.0
// @description  Play Console'da yeni uygulama oluşturma ve mağaza girişi formlarını JSON config ile otomatik doldurur. Kayan panel ile config yönetimi sağlar.
// @author       aNKa Dev
// @match        https://play.google.com/console/u/*/developers/*/create-new-app*
// @match        https://play.google.com/console/u/*/developers/*/app-list*
// @match        https://play.google.com/console/u/*/developers/*/app/*/main-store-listing*
// @include      https://play.google.com/console/*create-new-app*
// @include      https://play.google.com/console/*app-list*
// @include      https://play.google.com/console/*main-store-listing*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addStyle
// @grant        GM_setClipboard
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  // ─────────────────────────────────────────────
  // Dil seçenekleri haritası (Play Console değerleri)
  // ─────────────────────────────────────────────
  const LANG_MAP = {
    'tr-TR':  'Türkçe – tr-TR',
    'af':     'Afrikaans – af',
    'am':     'Amharca – am',
    'ar':     'Arapça – ar',
    'sq':     'Arnavutça – sq',
    'az-AZ':  'Azerbaycanca – az-AZ',
    'eu-ES':  'Baskça – eu-ES',
    'be':     'Belarusça – be',
    'bn-BD':  'Bengalce – bn-BD',
    'my-MM':  'Birmanca – my-MM',
    'bg':     'Bulgarca – bg',
    'da-DK':  'Danca – da-DK',
    'id':     'Endonezce – id',
    'hy-AM':  'Ermenice – hy-AM',
    'et':     'Estonca – et',
    'fa':     'Farsça – fa',
    'fa-AE':  'Farsça (BAE) – fa-AE',
    'fa-AF':  'Farsça (Afganistan) – fa-AF',
    'fa-IR':  'Farsça (İran) – fa-IR',
    'fil':    'Filipince – fil',
    'fi-FI':  'Fince – fi-FI',
    'fr-FR':  'Fransızca – fr-FR',
    'fr-CA':  'Fransızca (Kanada) – fr-CA',
    'gl-ES':  'Galiçyaca – gl-ES',
    'ka-GE':  'Gürcüce – ka-GE',
    'gu':     'Güzeratça – gu',
    'hi-IN':  'Hintçe – hi-IN',
    'hr':     'Hırvatça – hr',
    'nl-NL':  'Hollandaca – nl-NL',
    'iw-IL':  'İbranice – iw-IL',
    'en-IN':  'İngilizce (Hindistan) – en-IN',
    'en-SG':  'İngilizce (Singapur) – en-SG',
    'en-ZA':  'İngilizce (Güney Afrika) – en-ZA',
    'en-US':  'İngilizce (ABD) – en-US',
    'en-AU':  'İngilizce (Avustralya) – en-AU',
    'en-GB':  'İngilizce (Birleşik Krallık) – en-GB',
    'en-CA':  'İngilizce (Kanada) – en-CA',
    'es-ES':  'İspanyolca – es-ES',
    'es-US':  'İspanyolca (ABD) – es-US',
    'es-419': 'İspanyolca (Latin Amerika) – es-419',
    'sv-SE':  'İsveççe – sv-SE',
    'it-IT':  'İtalyanca – it-IT',
    'is-IS':  'İzlandaca – is-IS',
    'ja-JP':  'Japonca – ja-JP',
    'ca':     'Katalanca – ca',
    'kk':     'Kazakça – kk',
    'km-KH':  'Khmer – km-KH',
    'ko-KR':  'Korece – ko-KR',
    'ky-KG':  'Kırgızca – ky-KG',
    'lo-LA':  'Laosca – lo-LA',
    'lv':     'Letonca – lv',
    'lt':     'Litvanca – lt',
    'hu-HU':  'Macarca – hu-HU',
    'mk-MK':  'Makedonca – mk-MK',
    'ml-IN':  'Malayalamca – ml-IN',
    'ms':     'Malayca – ms',
    'ms-MY':  'Malayca (Malezya) – ms-MY',
    'mr-IN':  'Marathi – mr-IN',
    'mn-MN':  'Moğolca – mn-MN',
    'ne-NP':  'Nepalce – ne-NP',
    'no-NO':  'Norveçce – no-NO',
    'pa':     'Pencapça – pa',
    'pl-PL':  'Lehçe – pl-PL',
    'pt-BR':  'Portekizce (Brezilya) – pt-BR',
    'pt-PT':  'Portekizce (Portekiz) – pt-PT',
    'rm':     'Romanş – rm',
    'ro':     'Rumence – ro',
    'ru-RU':  'Rusça – ru-RU',
    'si-LK':  'Sinhali – si-LK',
    'sk':     'Slovakça – sk',
    'sl':     'Slovence – sl',
    'sr':     'Sırpça – sr',
    'sw':     'Swahili – sw',
    'ta-IN':  'Tamilce – ta-IN',
    'th':     'Tayca – th',
    'te-IN':  'Teluguca – te-IN',
    'uk':     'Ukraynaca – uk',
    'ur':     'Urduca – ur',
    'vi':     'Vietnamca – vi',
    'el-GR':  'Yunanca – el-GR',
    'cs-CZ':  'Çekçe – cs-CZ',
    'zh-CN':  'Çince (Basitleştirilmiş) – zh-CN',
    'zh-HK':  'Çince (Hong Kong) – zh-HK',
    'zh-TW':  'Çince (Geleneksel) – zh-TW',
    'zu':     'Zuluca – zu',
  };

  // ─────────────────────────────────────────────
  // Varsayılan config şablonu
  // ─────────────────────────────────────────────
  const DEFAULT_CONFIG = {
    appName: '',
    defaultLanguage: 'tr-TR',
    type: 'app',       // 'app' veya 'game'
    pricing: 'free',   // 'free' veya 'paid'
    declarations: {
      developerPoliciesAccepted: true,
      exportLawsAccepted: true,
    },
  };

  // ─────────────────────────────────────────────
  // Stil tanımları
  // ─────────────────────────────────────────────
  GM_addStyle(`
    #ugp-panel {
      position: fixed;
      top: 60px;
      right: 0;
      width: 320px;
      background: #fff;
      border-left: 3px solid #1a73e8;
      border-radius: 8px 0 0 8px;
      box-shadow: -4px 0 20px rgba(0,0,0,0.15);
      z-index: 99999;
      font-family: 'Google Sans', Roboto, sans-serif;
      font-size: 13px;
      transition: transform 0.3s ease;
    }
    #ugp-panel.collapsed {
      transform: translateX(285px);
    }
    #ugp-panel-header {
      background: #1a73e8;
      color: #fff;
      padding: 10px 14px;
      border-radius: 5px 0 0 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
    }
    #ugp-panel-header span { font-weight: 600; font-size: 13px; }
    #ugp-panel-body { padding: 12px; overflow-y: auto; max-height: 80vh; }
    .ugp-field { margin-bottom: 10px; }
    .ugp-field label { display: block; font-weight: 500; color: #3c4043; margin-bottom: 4px; font-size: 12px; }
    .ugp-field input[type="text"],
    .ugp-field select,
    .ugp-field textarea {
      width: 100%;
      border: 1px solid #dadce0;
      border-radius: 4px;
      padding: 6px 8px;
      font-size: 13px;
      box-sizing: border-box;
      outline: none;
    }
    .ugp-field input[type="text"]:focus,
    .ugp-field select:focus { border-color: #1a73e8; }
    .ugp-radio-group { display: flex; gap: 12px; }
    .ugp-radio-group label { display: flex; align-items: center; gap: 5px; font-weight: 400; cursor: pointer; }
    .ugp-checkbox-group label { display: flex; align-items: flex-start; gap: 6px; font-weight: 400; cursor: pointer; line-height: 1.4; }
    .ugp-btn {
      display: block;
      width: 100%;
      padding: 9px;
      border: none;
      border-radius: 4px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 8px;
    }
    .ugp-btn-primary { background: #1a73e8; color: #fff; }
    .ugp-btn-primary:hover { background: #1557b0; }
    .ugp-btn-secondary { background: #f1f3f4; color: #3c4043; }
    .ugp-btn-secondary:hover { background: #dadce0; }
    .ugp-btn-success { background: #34a853; color: #fff; }
    .ugp-btn-success:hover { background: #2d8f47; }
    .ugp-divider { border: none; border-top: 1px solid #e8eaed; margin: 10px 0; }
    .ugp-char-count { font-size: 11px; color: #5f6368; text-align: right; margin-top: 2px; }
    .ugp-status {
      padding: 6px 10px;
      border-radius: 4px;
      margin-top: 8px;
      font-size: 12px;
      display: none;
    }
    .ugp-status.success { background: #e6f4ea; color: #1e8e3e; display: block; }
    .ugp-status.error   { background: #fce8e6; color: #d93025; display: block; }
    .ugp-status.info    { background: #e8f0fe; color: #1967d2; display: block; }
    .ugp-collapse-btn { background: none; border: none; color: #fff; font-size: 16px; cursor: pointer; padding: 0; }
    .ugp-section-title { font-size: 11px; color: #5f6368; text-transform: uppercase; letter-spacing: 0.5px; margin: 10px 0 6px; font-weight: 600; }
    #ugp-json-area { font-family: monospace; font-size: 11px; height: 100px; resize: vertical; }
    .ugp-saved-list { list-style: none; padding: 0; margin: 0; }
    .ugp-saved-list li { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #f1f3f4; }
    .ugp-saved-list li:last-child { border-bottom: none; }
    .ugp-saved-list button { font-size: 11px; padding: 2px 7px; border: 1px solid #dadce0; background: #fff; border-radius: 3px; cursor: pointer; }
    /* ── Mağaza Girişi Paneli ── */
    #ugp-sl-panel {
      position: fixed;
      top: 60px;
      right: 0;
      width: 320px;
      background: #fff;
      border-left: 3px solid #34a853;
      border-radius: 8px 0 0 8px;
      box-shadow: -4px 0 20px rgba(0,0,0,0.15);
      z-index: 99999;
      font-family: 'Google Sans', Roboto, sans-serif;
      font-size: 13px;
      transition: transform 0.3s ease;
    }
    #ugp-sl-panel.collapsed { transform: translateX(285px); }
    #ugp-sl-header {
      background: #34a853;
      color: #fff;
      padding: 10px 14px;
      border-radius: 5px 0 0 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
    }
    #ugp-sl-header span { font-weight: 600; font-size: 13px; }
    #ugp-sl-body { padding: 12px; overflow-y: auto; max-height: 80vh; }
    .ugp-asset-info { font-size: 11px; color: #5f6368; background: #f8f9fa; padding: 8px 10px; border-radius: 4px; line-height: 1.7; border-left: 3px solid #34a853; }
    .ugp-asset-info b { color: #3c4043; }
  `);


  // ─────────────────────────────────────────────
  // Yardımcı: Angular controlled input'a değer yaz
  // ─────────────────────────────────────────────
  function setNativeInputValue(el, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    nativeInputValueSetter.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function waitFor(selector, timeout = 8000) {
    return new Promise((resolve, reject) => {
      const el = document.querySelector(selector);
      if (el) return resolve(el);
      const observer = new MutationObserver(() => {
        const found = document.querySelector(selector);
        if (found) { observer.disconnect(); resolve(found); }
      });
      observer.observe(document.body, { childList: true, subtree: true });
      setTimeout(() => { observer.disconnect(); reject(new Error(`Timeout: ${selector}`)); }, timeout);
    });
  }

  // ─────────────────────────────────────────────
  // Config kaydet / yükle (GM storage)
  // ─────────────────────────────────────────────
  function getSavedConfigs() {
    try { return JSON.parse(GM_getValue('ugp_saved_configs', '{}')) || {}; }
    catch { return {}; }
  }
  function saveConfig(name, config) {
    const all = getSavedConfigs();
    all[name] = config;
    GM_setValue('ugp_saved_configs', JSON.stringify(all));
  }
  function deleteConfig(name) {
    const all = getSavedConfigs();
    delete all[name];
    GM_setValue('ugp_saved_configs', JSON.stringify(all));
  }
  function getLastConfig() {
    try { return JSON.parse(GM_getValue('ugp_last_config', null)) || { ...DEFAULT_CONFIG }; }
    catch { return { ...DEFAULT_CONFIG }; }
  }
  function setLastConfig(config) {
    GM_setValue('ugp_last_config', JSON.stringify(config));
  }

  // ─────────────────────────────────────────────
  // Panel oluştur
  // ─────────────────────────────────────────────
  function buildPanel() {
    const existing = document.getElementById('ugp-panel');
    if (existing) return;

    const lastCfg = getLastConfig();
    const panel = document.createElement('div');
    panel.id = 'ugp-panel';
    panel.innerHTML = `
      <div id="ugp-panel-header">
        <span>🚀 Play Console – Hızlı Kayıt</span>
        <button class="ugp-collapse-btn" id="ugp-toggle-btn" title="Küçült/Büyüt">◀</button>
      </div>
      <div id="ugp-panel-body">

        <div class="ugp-section-title">Uygulama Bilgileri</div>

        <div class="ugp-field">
          <label>Uygulama Adı <span style="color:#d93025">*</span></label>
          <input type="text" id="ugp-app-name" maxlength="30" placeholder="Uygulamanın adı (max 30)" value="${escHtml(lastCfg.appName || '')}">
          <div class="ugp-char-count"><span id="ugp-name-count">${(lastCfg.appName || '').length}</span> / 30</div>
        </div>

        <div class="ugp-field">
          <label>Varsayılan Dil</label>
          <select id="ugp-language">
            ${Object.entries(LANG_MAP).map(([k, v]) =>
              `<option value="${k}" ${lastCfg.defaultLanguage === k ? 'selected' : ''}>${v}</option>`
            ).join('')}
          </select>
        </div>

        <div class="ugp-field">
          <label>Tür</label>
          <div class="ugp-radio-group">
            <label>
              <input type="radio" name="ugp-type" value="app" ${lastCfg.type !== 'game' ? 'checked' : ''}> Uygulama
            </label>
            <label>
              <input type="radio" name="ugp-type" value="game" ${lastCfg.type === 'game' ? 'checked' : ''}> Oyun
            </label>
          </div>
        </div>

        <div class="ugp-field">
          <label>Fiyatlandırma</label>
          <div class="ugp-radio-group">
            <label>
              <input type="radio" name="ugp-pricing" value="free" ${lastCfg.pricing !== 'paid' ? 'checked' : ''}> Ücretsiz
            </label>
            <label>
              <input type="radio" name="ugp-pricing" value="paid" ${lastCfg.pricing === 'paid' ? 'checked' : ''}> Ücretli
            </label>
          </div>
        </div>

        <hr class="ugp-divider">
        <div class="ugp-section-title">Beyanlar</div>

        <div class="ugp-field ugp-checkbox-group">
          <label>
            <input type="checkbox" id="ugp-dev-policy" ${(lastCfg.declarations?.developerPoliciesAccepted) ? 'checked' : ''}>
            Geliştirici Program Politikaları'nı kabul ediyorum
          </label>
        </div>
        <div class="ugp-field ugp-checkbox-group">
          <label>
            <input type="checkbox" id="ugp-export-law" ${(lastCfg.declarations?.exportLawsAccepted) ? 'checked' : ''}>
            ABD ihracat yasalarını kabul ediyorum
          </label>
        </div>

        <hr class="ugp-divider">

        <button class="ugp-btn ugp-btn-primary" id="ugp-fill-btn">⚡ Formu Doldur</button>
        <button class="ugp-btn ugp-btn-success" id="ugp-fill-submit-btn">⚡ Doldur & Oluştur</button>

        <hr class="ugp-divider">
        <div class="ugp-section-title">Config Kaydet / Yükle</div>

        <div class="ugp-field" style="display:flex;gap:6px">
          <input type="text" id="ugp-save-name" placeholder="Config adı (örn: mathlock)" style="flex:1">
          <button class="ugp-btn ugp-btn-secondary" id="ugp-save-btn" style="width:auto;margin:0;padding:6px 10px">Kaydet</button>
        </div>

        <ul class="ugp-saved-list" id="ugp-saved-list"></ul>

        <hr class="ugp-divider">
        <div class="ugp-section-title">JSON İçe/Dışa Aktar</div>
        <textarea id="ugp-json-area" placeholder='{"appName":"...","type":"app",...}'></textarea>
        <div style="display:flex;gap:6px;margin-top:6px">
          <button class="ugp-btn ugp-btn-secondary" id="ugp-json-import-btn" style="margin:0">JSON Uygula</button>
          <button class="ugp-btn ugp-btn-secondary" id="ugp-json-export-btn" style="margin:0">JSON Al</button>
        </div>

        <div class="ugp-status" id="ugp-status"></div>
      </div>
    `;
    document.body.appendChild(panel);
    bindPanelEvents(panel);
    renderSavedList();
  }

  function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function showStatus(msg, type = 'info') {
    const el = document.getElementById('ugp-status');
    if (!el) return;
    el.textContent = msg;
    el.className = `ugp-status ${type}`;
    setTimeout(() => { el.className = 'ugp-status'; }, 4000);
  }

  function readPanelConfig() {
    return {
      appName: document.getElementById('ugp-app-name')?.value?.trim() || '',
      defaultLanguage: document.getElementById('ugp-language')?.value || 'tr-TR',
      type: document.querySelector('input[name="ugp-type"]:checked')?.value || 'app',
      pricing: document.querySelector('input[name="ugp-pricing"]:checked')?.value || 'free',
      declarations: {
        developerPoliciesAccepted: document.getElementById('ugp-dev-policy')?.checked ?? true,
        exportLawsAccepted: document.getElementById('ugp-export-law')?.checked ?? true,
      },
    };
  }

  function applyConfigToPanel(cfg) {
    const nameEl = document.getElementById('ugp-app-name');
    if (nameEl) { nameEl.value = cfg.appName || ''; updateCharCount(); }
    const langEl = document.getElementById('ugp-language');
    if (langEl) langEl.value = cfg.defaultLanguage || 'tr-TR';
    const typeRadio = document.querySelector(`input[name="ugp-type"][value="${cfg.type || 'app'}"]`);
    if (typeRadio) typeRadio.checked = true;
    const pricingRadio = document.querySelector(`input[name="ugp-pricing"][value="${cfg.pricing || 'free'}"]`);
    if (pricingRadio) pricingRadio.checked = true;
    const devPolicy = document.getElementById('ugp-dev-policy');
    if (devPolicy) devPolicy.checked = cfg.declarations?.developerPoliciesAccepted ?? true;
    const exportLaw = document.getElementById('ugp-export-law');
    if (exportLaw) exportLaw.checked = cfg.declarations?.exportLawsAccepted ?? true;
  }

  function renderSavedList() {
    const ul = document.getElementById('ugp-saved-list');
    if (!ul) return;
    const all = getSavedConfigs();
    const keys = Object.keys(all);
    if (keys.length === 0) {
      ul.innerHTML = '<li style="color:#5f6368;font-size:11px">Henüz kayıtlı config yok</li>';
      return;
    }
    ul.innerHTML = keys.map(name => `
      <li>
        <span style="font-size:12px">${escHtml(name)}</span>
        <div style="display:flex;gap:4px">
          <button data-load="${escHtml(name)}">Yükle</button>
          <button data-del="${escHtml(name)}" style="color:#d93025">Sil</button>
        </div>
      </li>
    `).join('');
    ul.querySelectorAll('button[data-load]').forEach(btn => {
      btn.addEventListener('click', () => {
        const cfg = getSavedConfigs()[btn.dataset.load];
        if (cfg) { applyConfigToPanel(cfg); showStatus(`"${btn.dataset.load}" yüklendi`, 'success'); }
      });
    });
    ul.querySelectorAll('button[data-del]').forEach(btn => {
      btn.addEventListener('click', () => {
        deleteConfig(btn.dataset.del);
        renderSavedList();
        showStatus(`"${btn.dataset.del}" silindi`, 'info');
      });
    });
  }

  function updateCharCount() {
    const el = document.getElementById('ugp-app-name');
    const counter = document.getElementById('ugp-name-count');
    if (el && counter) counter.textContent = el.value.length;
  }

  function bindPanelEvents(panel) {
    // Küçült/Büyüt
    document.getElementById('ugp-panel-header').addEventListener('click', (e) => {
      if (e.target.id === 'ugp-toggle-btn' || e.target === e.currentTarget || e.target.tagName === 'SPAN') {
        const collapsed = panel.classList.toggle('collapsed');
        document.getElementById('ugp-toggle-btn').textContent = collapsed ? '▶' : '◀';
      }
    });
    // Karakter sayacı
    document.getElementById('ugp-app-name')?.addEventListener('input', updateCharCount);

    // Formu Doldur
    document.getElementById('ugp-fill-btn')?.addEventListener('click', async () => {
      const cfg = readPanelConfig();
      setLastConfig(cfg);
      if (!window.location.href.includes('create-new-app')) {
        window.location.href = `https://play.google.com/console/u/0/developers/9071363965517112224/create-new-app`;
        return;
      }
      await fillForm(cfg, false);
    });

    // Doldur & Oluştur
    document.getElementById('ugp-fill-submit-btn')?.addEventListener('click', async () => {
      const cfg = readPanelConfig();
      setLastConfig(cfg);
      if (!window.location.href.includes('create-new-app')) {
        window.location.href = `https://play.google.com/console/u/0/developers/9071363965517112224/create-new-app`;
        return;
      }
      await fillForm(cfg, true);
    });

    // Config Kaydet
    document.getElementById('ugp-save-btn')?.addEventListener('click', () => {
      const name = document.getElementById('ugp-save-name')?.value?.trim();
      if (!name) { showStatus('Lütfen bir config adı girin', 'error'); return; }
      const cfg = readPanelConfig();
      saveConfig(name, cfg);
      renderSavedList();
      document.getElementById('ugp-save-name').value = '';
      showStatus(`"${name}" kaydedildi`, 'success');
    });

    // JSON Dışa Aktar
    document.getElementById('ugp-json-export-btn')?.addEventListener('click', () => {
      const cfg = readPanelConfig();
      const json = JSON.stringify(cfg, null, 2);
      document.getElementById('ugp-json-area').value = json;
      GM_setClipboard(json);
      showStatus('JSON panoya kopyalandı', 'success');
    });

    // JSON İçe Aktar
    document.getElementById('ugp-json-import-btn')?.addEventListener('click', () => {
      const raw = document.getElementById('ugp-json-area')?.value?.trim();
      if (!raw) { showStatus('JSON alanı boş', 'error'); return; }
      try {
        const cfg = JSON.parse(raw);
        applyConfigToPanel(cfg);
        showStatus('JSON uygulandı', 'success');
      } catch (e) {
        showStatus('Geçersiz JSON: ' + e.message, 'error');
      }
    });
  }

  // ─────────────────────────────────────────────
  // Ana form doldurma fonksiyonu
  // Play Console Angular Material bileşenlerini (material-radio, material-checkbox) hedefler.
  // ─────────────────────────────────────────────
  async function fillForm(config, autoSubmit = false) {
    showStatus('Form dolduruluyor…', 'info');
    try {
      // ── 1) Uygulama adı ──
      // Angular material textbox: aria-label="Uygulama adı" olan input
      let appNameInput = document.querySelector('input[aria-label="Uygulama adı"]');
      if (!appNameInput) {
        // Fallback: form içindeki ilk text input
        appNameInput = document.querySelector('mat-form-field input, input[maxlength="30"]');
      }
      if (appNameInput && config.appName) {
        appNameInput.focus();
        setNativeInputValue(appNameInput, config.appName);
        await sleep(400);
      } else {
        console.warn('[UGP] Uygulama adı input bulunamadı');
      }

      // ── 2) Varsayılan dil dropdown ──
      // Butonu ARIA label'ından bul: "Varsayılan dil: <mevcut dil>"
      if (config.defaultLanguage) {
        const langBtn = document.querySelector(
          'button[aria-label*="Varsayılan dil"], button[data-label*="Varsayılan dil"]'
        ) || Array.from(document.querySelectorAll('button')).find(
          b => b.textContent.trim().match(/^(İngilizce|Türkçe|Almanca|Fransızca|Arapça|Japonca|Korece|Rusça|Çince|İspanyolca)/)
        );
        if (langBtn) {
          langBtn.click();
          await sleep(900);
          // Açılan listbox/overlay içindeki option'ları tara
          const options = document.querySelectorAll('[role="option"], [role="listbox"] li, .cdk-virtual-scroll-content-wrapper [class*="list-item"]');
          const targetCode = config.defaultLanguage; // örn. "tr-TR"
          let found = false;
          for (const opt of options) {
            if (opt.textContent.includes(targetCode)) {
              opt.click();
              found = true;
              await sleep(400);
              break;
            }
          }
          if (!found) {
            // ESC ile kapat, devam et
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            await sleep(300);
            console.warn('[UGP] Dil seçeneği bulunamadı:', targetCode);
          }
        }
      }

      // ── 3) Uygulama veya Oyun (material-radio) ──
      const typeLabel  = config.type === 'game' ? 'Oyun' : 'Uygulama';
      const matRadios  = document.querySelectorAll('material-radio, mat-radio-button, [role="radio"]');
      for (const r of matRadios) {
        if (r.textContent.trim() === typeLabel) {
          r.click();
          await sleep(250);
          break;
        }
      }

      // ── 4) Ücretsiz veya Ücretli (material-radio) ──
      const priceLabel = config.pricing === 'paid' ? 'Ücretli' : 'Ücretsiz';
      for (const r of matRadios) {
        if (r.textContent.trim() === priceLabel) {
          r.click();
          await sleep(250);
          break;
        }
      }

      // ── 5) Beyanlar (material-checkbox) ──
      // Play Console'da gerçek <input type=checkbox> değil material-checkbox kullanılıyor.
      // aria-label içinde anahtar kelime ara; checked değilse wrapper'a tıkla.
      const matCbs = document.querySelectorAll('material-checkbox, mat-checkbox, [role="checkbox"]');
      for (const cb of matCbs) {
        const ariaLabel = cb.getAttribute('aria-label') || cb.textContent || '';
        const isChecked = cb.getAttribute('aria-checked') === 'true' || cb.classList.contains('mat-checkbox-checked');

        if (!isChecked) {
          if (config.declarations?.developerPoliciesAccepted &&
              (ariaLabel.includes('Geliştirici Program') || ariaLabel.includes('developer policy'))) {
            cb.click();
            await sleep(250);
          }
          if (config.declarations?.exportLawsAccepted &&
              (ariaLabel.includes('ihracat') || ariaLabel.includes('export law'))) {
            cb.click();
            await sleep(250);
          }
        }
      }

      showStatus('✅ Form dolduruldu!', 'success');

      // ── 6) Otomatik gönder ──
      if (autoSubmit) {
        await sleep(800);
        const submitBtn = findSubmitButton();
        if (submitBtn && !submitBtn.disabled) {
          submitBtn.click();
          showStatus('🚀 Form gönderiliyor…', 'info');
        } else {
          showStatus('⚠️ Gönder butonu bulunamadı veya devre dışı — lütfen manuel gönderin', 'error');
        }
      }
    } catch (err) {
      showStatus('Hata: ' + err.message, 'error');
      console.error('[UGP] fillForm hatası:', err);
    }
  }

  function findSubmitButton() {
    return Array.from(document.querySelectorAll('button')).find(
      b => ['Uygulama oluştur', 'Create app', 'Oluştur'].includes(b.textContent.trim())
    ) || null;
  }

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // ─────────────────────────────────────────────
  // Textarea için native value setter (Angular ngModel uyumu)
  // ─────────────────────────────────────────────
  function setNativeTextareaValue(el, value) {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // ─────────────────────────────────────────────
  // Mağaza Girişi (main-store-listing) Paneli
  // ─────────────────────────────────────────────
  function getSlConfig() {
    try { return JSON.parse(GM_getValue('ugp_sl_last', '{}')) || {}; }
    catch { return {}; }
  }
  function setSlConfig(cfg) { GM_setValue('ugp_sl_last', JSON.stringify(cfg)); }

  function showSlStatus(msg, type = 'info') {
    const el = document.getElementById('ugp-sl-status');
    if (!el) return;
    el.textContent = msg;
    el.className = `ugp-status ${type}`;
    setTimeout(() => { el.className = 'ugp-status'; }, 5000);
  }

  function buildSlPanel() {
    if (document.getElementById('ugp-sl-panel')) return;
    const last = getSlConfig();
    const panel = document.createElement('div');
    panel.id = 'ugp-sl-panel';
    panel.innerHTML = `
      <div id="ugp-sl-header">
        <span>📝 Mağaza Girişi</span>
        <button class="ugp-collapse-btn" id="ugp-sl-toggle" title="Küçült/Büyüt">◀</button>
      </div>
      <div id="ugp-sl-body">
        <div class="ugp-section-title">Metin Alanları</div>

        <div class="ugp-field">
          <label>Uygulama Başlığı <span style="color:#d93025">*</span> (max 30)</label>
          <input type="text" id="ugp-sl-title" maxlength="30" placeholder="Başlık"
            value="${escHtml(last.title || '')}">
          <div class="ugp-char-count"><span id="ugp-sl-title-cnt">${(last.title || '').length}</span> / 30</div>
        </div>

        <div class="ugp-field">
          <label>Kısa Açıklama (max 80)</label>
          <textarea id="ugp-sl-short" maxlength="80" rows="3"
            placeholder="Kısa açıklama…">${escHtml(last.shortDescription || '')}</textarea>
          <div class="ugp-char-count"><span id="ugp-sl-short-cnt">${(last.shortDescription || '').length}</span> / 80</div>
        </div>

        <div class="ugp-field">
          <label>Tam Açıklama (max 4000)</label>
          <textarea id="ugp-sl-full" maxlength="4000" rows="7"
            placeholder="Tam açıklama…">${escHtml(last.fullDescription || '')}</textarea>
          <div class="ugp-char-count"><span id="ugp-sl-full-cnt">${(last.fullDescription || '').length}</span> / 4000</div>
        </div>

        <button class="ugp-btn ugp-btn-primary" id="ugp-sl-fill-btn">⚡ Metinleri Doldur</button>
        <button class="ugp-btn ugp-btn-secondary" id="ugp-sl-save-btn">💾 Tarayıcıya Kaydet</button>

        <hr class="ugp-divider">
        <div class="ugp-section-title">Görsel Gereksinimleri</div>
        <div class="ugp-asset-info">
          <b>İkon:</b> 512×512 PNG/JPEG · max 1 MB<br>
          <b>Öne Çıkan Grafik:</b> 1024×500 PNG/JPEG · max 15 MB<br>
          <b>Telefon:</b> min 2 · max 8 ekran görüntüsü<br>
          <b>7" Tablet:</b> isteğe bağlı<br>
          <b>10" Tablet:</b> isteğe bağlı<br>
          <span style="color:#1a73e8">📁 Görselleri manuel yükleyin.</span>
        </div>

        <div class="ugp-status" id="ugp-sl-status"></div>
      </div>
    `;
    document.body.appendChild(panel);

    // Collapse/expand
    document.getElementById('ugp-sl-header').addEventListener('click', (e) => {
      if (e.target.id === 'ugp-sl-toggle' || e.target === e.currentTarget || e.target.tagName === 'SPAN') {
        const collapsed = panel.classList.toggle('collapsed');
        document.getElementById('ugp-sl-toggle').textContent = collapsed ? '▶' : '◀';
      }
    });

    // Karakter sayaçları
    const titleEl = document.getElementById('ugp-sl-title');
    const shortEl = document.getElementById('ugp-sl-short');
    const fullEl  = document.getElementById('ugp-sl-full');
    titleEl?.addEventListener('input', () => {
      document.getElementById('ugp-sl-title-cnt').textContent = titleEl.value.length;
    });
    shortEl?.addEventListener('input', () => {
      document.getElementById('ugp-sl-short-cnt').textContent = shortEl.value.length;
    });
    fullEl?.addEventListener('input', () => {
      document.getElementById('ugp-sl-full-cnt').textContent = fullEl.value.length;
    });

    // Doldur butonu
    document.getElementById('ugp-sl-fill-btn')?.addEventListener('click', async () => {
      const cfg = readSlPanelConfig();
      setSlConfig(cfg);
      await fillStoreListing(cfg);
    });

    // Kaydet butonu
    document.getElementById('ugp-sl-save-btn')?.addEventListener('click', () => {
      setSlConfig(readSlPanelConfig());
      showSlStatus('✅ Kaydedildi', 'success');
    });
  }

  function readSlPanelConfig() {
    return {
      title:            document.getElementById('ugp-sl-title')?.value?.trim() || '',
      shortDescription: document.getElementById('ugp-sl-short')?.value?.trim() || '',
      fullDescription:  document.getElementById('ugp-sl-full')?.value?.trim() || '',
    };
  }

  async function fillStoreListing(config) {
    showSlStatus('Form dolduruluyor…', 'info');
    try {
      // ── 1) Başlık ──
      if (config.title) {
        let titleInput = document.querySelector('input[aria-label*="Uygulama adı"], input[aria-label*="Başlık"], input[aria-label*="Title"]');
        if (!titleInput) {
          // Fallback: ilk text input içinde max 30
          titleInput = document.querySelector('mat-form-field input[maxlength="30"], input[maxlength="30"]');
        }
        if (titleInput) {
          titleInput.focus();
          setNativeInputValue(titleInput, config.title);
          await sleep(400);
        } else {
          console.warn('[UGP-SL] Başlık input bulunamadı');
        }
      }

      // ── 2) Kısa açıklama ──
      if (config.shortDescription) {
        const shortTA = document.querySelector('textarea[aria-label*="Kısa açıklama"], textarea[aria-label*="Short description"], textarea[maxlength="80"]');
        if (shortTA) {
          shortTA.focus();
          setNativeTextareaValue(shortTA, config.shortDescription);
          await sleep(400);
        } else {
          console.warn('[UGP-SL] Kısa açıklama textarea bulunamadı');
        }
      }

      // ── 3) Tam açıklama ──
      if (config.fullDescription) {
        const fullTA = document.querySelector('textarea[aria-label*="Tam açıklama"], textarea[aria-label*="Full description"], textarea[maxlength="4000"]');
        if (fullTA) {
          fullTA.focus();
          setNativeTextareaValue(fullTA, config.fullDescription);
          await sleep(400);
        } else {
          console.warn('[UGP-SL] Tam açıklama textarea bulunamadı');
        }
      }

      showSlStatus('✅ Metinler dolduruldu!', 'success');
    } catch (err) {
      showSlStatus('Hata: ' + err.message, 'error');
      console.error('[UGP-SL] fillStoreListing hatası:', err);
    }
  }

  // ─────────────────────────────────────────────
  // URL parametresiyle store-listing otomatik doldurma
  //
  // Parametreler:
  //   ugpSlFill=1       → tetikleyici (zorunlu)
  //   ugpSlTitle        → uygulama başlığı (max 30)
  //   ugpSlShort        → kısa açıklama (max 80)
  //   ugpSlFull         → tam açıklama (max 4000)
  //   ugpSlSubmit       → 1 → formu kaydet (Taslak Kaydet butonunu tıkla)
  // ─────────────────────────────────────────────
  async function checkSlParams() {
    const params = new URLSearchParams(window.location.search);
    if (!params.has('ugpSlFill')) return;

    await sleep(2500); // Angular yüklensin

    const cfg = {
      title:            params.get('ugpSlTitle') || '',
      shortDescription: params.get('ugpSlShort') || '',
      fullDescription:  params.get('ugpSlFull')  || '',
    };

    // Panel alanlarını güncelle (görsel)
    const titleEl = document.getElementById('ugp-sl-title');
    const shortEl = document.getElementById('ugp-sl-short');
    const fullEl  = document.getElementById('ugp-sl-full');
    if (titleEl) { titleEl.value = cfg.title; document.getElementById('ugp-sl-title-cnt').textContent = cfg.title.length; }
    if (shortEl) { shortEl.value = cfg.shortDescription; document.getElementById('ugp-sl-short-cnt').textContent = cfg.shortDescription.length; }
    if (fullEl)  { fullEl.value  = cfg.fullDescription;  document.getElementById('ugp-sl-full-cnt').textContent  = cfg.fullDescription.length; }

    await fillStoreListing(cfg);

    if (params.get('ugpSlSubmit') === '1') {
      await sleep(800);
      const saveBtn = Array.from(document.querySelectorAll('button')).find(
        b => /Taslak olarak kaydet|Kaydet|Save draft/i.test(b.textContent.trim())
      );
      if (saveBtn && !saveBtn.disabled) {
        saveBtn.click();
        showSlStatus('💾 Taslak kaydediliyor…', 'info');
      }
    }
  }

  // ─────────────────────────────────────────────
  // URL parametresiyle otomatik doldurma
  // Copilot bu URL'yi oluşturur ve navigate eder; betik geri kalanı üstlenir.
  //
  // Parametreler:
  //   ugpAutoFill=1   → tetikleyici (zorunlu)
  //   ugpName         → uygulama adı
  //   ugpLang         → dil kodu (örn. tr-TR)
  //   ugpType         → app | game
  //   ugpPricing      → free | paid
  //   ugpPolicy       → 1 | 0  (Geliştirici Politikası onayı)
  //   ugpExport       → 1 | 0  (İhracat yasaları onayı)
  //   ugpSubmit       → 1      → formu otomatik gönder
  // ─────────────────────────────────────────────
  async function checkAutoFillParams() {
    const params = new URLSearchParams(window.location.search);
    if (!params.has('ugpAutoFill')) return;

    // Angular sayfasının yüklenmesi için yeterli süre bekle
    await sleep(2500);

    const cfg = {
      appName:         params.get('ugpName')    || '',
      defaultLanguage: params.get('ugpLang')    || 'tr-TR',
      type:            params.get('ugpType')    || 'app',
      pricing:         params.get('ugpPricing') || 'free',
      declarations: {
        developerPoliciesAccepted: params.get('ugpPolicy') !== '0',
        exportLawsAccepted:        params.get('ugpExport') !== '0',
      },
    };

    // Paneldeki alanları da güncelle (görsel geri bildirim)
    applyConfigToPanel(cfg);

    await fillForm(cfg, params.get('ugpSubmit') === '1');
  }

  // ─────────────────────────────────────────────
  // Başlat
  // ─────────────────────────────────────────────
  async function init() {
    await sleep(1500); // Angular yüklensin
    const url = window.location.href;
    if (url.includes('main-store-listing')) {
      buildSlPanel();
      await checkSlParams();
    } else {
      buildPanel();
      if (url.includes('create-new-app')) {
        await checkAutoFillParams();
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
