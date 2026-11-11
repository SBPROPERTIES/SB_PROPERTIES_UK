/* Formspree AJAX flow: only a confirmed successful response is a conversion. */
(() => {
  'use strict';
  document.querySelectorAll('form[action^="https://formspree.io/f/"]').forEach(form => {
    if (form.dataset.enquiryBound) return;
    form.dataset.enquiryBound = 'true';
    let pending = false;
    let completed = false;
    const status = document.createElement('p');
    status.className = 'form-note';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    form.appendChild(status);
    form.addEventListener('submit', async event => {
      event.preventDefault();
      if (pending || completed || !form.reportValidity()) return;
      pending = true;
      const buttons = [...form.querySelectorAll('[type="submit"]')];
      buttons.forEach(button => { button.disabled = true; });
      status.textContent = 'Sending your enquiry…';
      const data = new FormData(form);
      let measurement;
      try {
        measurement = window.sbpMeasurement?.snapshot();
        if (measurement?.adCode) data.set('Ad code', measurement.adCode);
      } catch (_) {}
      try {
        const response = await fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
        if (!response.ok) throw new Error('Formspree did not accept the enquiry');
        completed = true;
        status.textContent = 'Thank you! Your enquiry has been sent. We’ll get back to you within 24 hours.';
        // Keep this isolated: a blocked or broken Pixel cannot turn success into failure.
        try { if (measurement) window.sbpMeasurement?.lead(measurement); } catch (_) {}
        form.reset();
      } catch (_) {
        status.textContent = 'Your enquiry could not be confirmed. Please try again, or call 07367079485.';
        buttons.forEach(button => { button.disabled = false; });
      } finally { pending = false; }
    });
  });
})();
