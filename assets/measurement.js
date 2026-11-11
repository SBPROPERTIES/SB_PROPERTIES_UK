/* Shared, opt-in OpenAI advertising measurement. No enquiry data is passed here. */
(() => {
  'use strict';
  if (window.sbpMeasurement) return;
  const choiceKey = 'sbp-ad-consent-v1';
  const codeKey = 'sbp-ad-code';
  const read = (store, key) => { try { return window[store].getItem(key); } catch (_) { return null; } };
  const write = (store, key, value) => { try { value === null ? window[store].removeItem(key) : window[store].setItem(key, value); } catch (_) {} };
  let consent = read('localStorage', choiceKey) === 'accepted';
  let started = false;
  let adCode = null;
  let revision = 0;
  const call = (...args) => { try { window.oaiq?.(...args); } catch (_) { /* Measurement must never affect an enquiry. */ } };
  function captureCode() {
    if (!consent) return;
    const value = new URLSearchParams(location.search).get('utm_content');
    adCode = value && /^[a-zA-Z0-9_-]{1,100}$/.test(value) ? value : read('sessionStorage', codeKey);
    if (adCode) write('sessionStorage', codeKey, adCode);
  }
  function start() {
    if (started || !consent) return;
    started = true;
    if (!window.oaiq) {
      const q = function () { q.q.push(arguments); };
      q.q = [];
      window.oaiq = q;
    }
    call('consent', false);
    call('init', { pixelId: 'TZqiQtfCoQV3xkSd8woaE3', debug: false });
    call('consent', true);
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://bzrcdn.openai.com/sdk/oaiq.min.js';
    document.head.appendChild(script);
  }
  function apply(value) {
    consent = value === 'accepted';
    revision++;
    if (consent) { captureCode(); if (started) call('consent', true); else start(); }
    else {
      adCode = null;
      write('sessionStorage', codeKey, null);
      // Remove queued conversions too if consent is withdrawn before the SDK arrives.
      if (Array.isArray(window.oaiq?.q)) window.oaiq.q = window.oaiq.q.filter(args => args[0] !== 'measure');
      call('consent', false);
      for (const name of ['__oppref', '__obref']) {
        document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax`;
        document.cookie = `${name}=; Max-Age=0; Path=/; Domain=${location.hostname}; SameSite=Lax`;
      }
    }
  }
  window.sbpMeasurement = {
    snapshot: () => ({ consent, revision, adCode: consent ? adCode : null }),
    lead: snapshot => {
      if (consent && snapshot.consent && snapshot.revision === revision) call('measure', 'lead_created', { type: 'customer_action' });
    }
  };
  if (consent) { captureCode(); start(); }
  else write('sessionStorage', codeKey, null);
  window.addEventListener('storage', event => {
    if (event.key === choiceKey || event.key === null) apply(read('localStorage', choiceKey));
  });
  window.addEventListener('pageshow', event => {
    if (event.persisted) apply(read('localStorage', choiceKey));
  });
  const panel = document.createElement('section');
  panel.id = 'advertising-consent';
  panel.setAttribute('aria-label', 'Advertising measurement preferences');
  panel.innerHTML = '<h2>Advertising measurement</h2><p>May we use the OpenAI Pixel to measure which ads lead to enquiries? It uses cookies and may securely hash supported contact details entered on this site for matching. With your permission, we also include the ad code with your enquiry. Your form works either way. <a href="/privacy/#advertising">Privacy and cookies</a></p><div><button type="button" data-choice="accepted">Accept tracking</button><button type="button" data-choice="declined">Decline tracking</button></div>';
  panel.hidden = ['accepted', 'declined'].includes(read('localStorage', choiceKey));
  const settings = document.createElement('button');
  settings.type = 'button';
  settings.id = 'advertising-settings';
  settings.textContent = 'Cookie settings';
  settings.setAttribute('aria-controls', panel.id);
  settings.onclick = () => { panel.hidden = false; panel.querySelector('button').focus(); };
  panel.querySelectorAll('button').forEach(button => button.onclick = () => {
    write('localStorage', choiceKey, button.dataset.choice);
    apply(button.dataset.choice);
    panel.hidden = true;
    settings.focus();
  });
  document.body.append(panel, settings);
})();
