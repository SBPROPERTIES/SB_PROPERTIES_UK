(() => {
  // Preview and development traffic must not contaminate the production property.
  if (!['sbproperties.uk', 'www.sbproperties.uk'].includes(location.hostname)) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=G-HMFSX14PT5';
  document.head.appendChild(script);
  window.gtag('js', new Date());
  window.gtag('config', 'G-HMFSX14PT5');
})();
