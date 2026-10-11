(() => {
  const emit = (name, properties = {}) => {
    if (typeof window.gtag === 'function') window.gtag('event', name, properties);
  };
  const path = window.location.pathname;
  const forms = [...document.querySelectorAll('form.sb-form')];
  forms.forEach(form => {
    let started = false;
    form.addEventListener('input', () => {
      if (!started) { started = true; emit('lead_form_start', {page_path:path}); }
    });
    form.addEventListener('invalid', () => emit('lead_validation_error', {page_path:path}), true);
    form.addEventListener('submit', () => {
      // Preserve the existing native POST and existing email/webhook handlers.
      // A submit attempt is deliberately not counted as a successful enquiry.
      emit('lead_submit_attempt', {page_path:path});
    });
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { emit('lead_form_view', {page_path:path}); observer.unobserve(entry.target); }
      });
    }, {threshold:0.2});
    forms.forEach(form => observer.observe(form));
  }
  document.querySelectorAll('[data-sb-cta]').forEach(link => {
    link.addEventListener('click', () => {
      const destination = new URL(link.href, location.href);
      emit('seller_cta_click', {page_path:path,placement:link.dataset.sbCta,destination_path:destination.pathname});
    });
  });
  document.querySelectorAll('a[href^="tel:"],a[href^="https://wa.me/"]').forEach(link => {
    link.addEventListener('click', () => emit('seller_contact_click', {page_path:path,contact_method:link.href.startsWith('tel:')?'phone':'whatsapp'}));
  });
  const bar = document.querySelector('.sb-mobile-actions');
  const toggleBar = () => {
    if (!bar) return;
    const editing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || '');
    bar.style.display = editing ? 'none' : '';
  };
  document.addEventListener('focusin', toggleBar);
  document.addEventListener('focusout', () => requestAnimationFrame(toggleBar));
  // Record useful interactions without sending answers, search text or contact details.
  document.querySelectorAll('.faq-layout details').forEach((details, index) => {
    let recorded = false;
    details.addEventListener('toggle', () => {
      if (details.open && !recorded) {
        recorded = true;
        emit('seller_faq_open', {page_path:path,question_number:index + 1});
      }
    });
  });
  document.querySelectorAll('form.sb-form details').forEach(details => {
    let recorded = false;
    details.addEventListener('toggle', () => {
      if (details.open && !recorded) {
        recorded = true;
        emit('lead_details_open', {page_path:path});
      }
    });
  });
})();
