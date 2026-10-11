(() => {
  const controls = document.querySelector('.guide-controls');
  if (!controls) return;
  const search = document.getElementById('guide-search');
  const cards = [...document.querySelectorAll('.guide-result')];
  const filters = [...document.querySelectorAll('[data-guide-filter]')];
  const count = document.querySelector('.guide-count');
  const empty = document.querySelector('.guide-empty');
  let topic = 'all';
  const update = () => {
    const words = search.value.toLocaleLowerCase('en-GB').trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const text = card.textContent.toLocaleLowerCase('en-GB');
      const matches = (topic === 'all' || card.dataset.guideTopic === topic) && words.every(word => text.includes(word));
      card.hidden = !matches;
      if (matches) visible++;
    });
    count.textContent = `Showing ${visible} of ${cards.length} guides`;
    empty.hidden = visible > 0;
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.guideFilter === topic)));
  };
  filters.forEach(button => button.addEventListener('click', () => {
    topic = button.dataset.guideFilter;
    update();
    // Only a fixed topic identifier is measured; free-text searches are not sent.
    if (typeof window.gtag === 'function') window.gtag('event', 'guide_topic_selected', {topic, page_path:location.pathname});
  }));
  search.addEventListener('input', update);
  document.getElementById('guide-reset').addEventListener('click', () => {
    topic = 'all'; search.value = ''; update(); search.focus();
  });
  controls.hidden = false;
})();
