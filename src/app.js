(() => {
  const entries = window.MASTERBOOK_SEED || [];
  let view = 'all';
  const cards = document.getElementById('cards');
  const search = document.getElementById('search');
  const count = document.getElementById('count');
  const detail = document.getElementById('detail');

  const esc = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

  function matches(entry, query) {
    const haystack = [entry.id, entry.type, entry.title, entry.summary, entry.primary_category, ...entry.categories, ...entry.tags, ...entry.projects, entry.priority, entry.maturity, entry.status].join(' ').toLowerCase();
    return !query || haystack.includes(query.toLowerCase());
  }

  function visible(entry) {
    return view === 'all' || entry.priority === view || entry.type === view;
  }

  function show(id) {
    const entry = entries.find(item => item.id === id);
    if (!entry) return;
    detail.innerHTML = `
      <h2>${esc(entry.id)}</h2>
      <h3>${esc(entry.title)}</h3>
      <p><strong>Was ist das?</strong><br>${esc(entry.summary)}</p>
      <p><strong>Warum wichtig?</strong><br>Priorität ${esc(entry.priority)} · Reife ${esc(entry.maturity)}</p>
      <p><strong>Was soll ich tun?</strong><br>${entry.status === 'standard' ? 'Als gültigen Standard berücksichtigen.' : 'Als bestätigten Wissenseintrag berücksichtigen; keine automatische Hochstufung.'}</p>
      <p><strong>Kategorien</strong><br>${esc([entry.primary_category, ...entry.categories].join(' · '))}</p>
      <p><strong>Quelle</strong><br>${esc(entry.sources.map(source => source.ref).join(' · '))}</p>`;
  }

  function render() {
    const query = search.value.trim();
    const filtered = entries.filter(entry => visible(entry) && matches(entry, query));
    count.textContent = `${filtered.length} Einträge`;
    cards.innerHTML = filtered.map(entry => `
      <article class="card" tabindex="0" data-id="${esc(entry.id)}">
        <h3>${esc(entry.id)} · ${esc(entry.title)}</h3>
        <p>${esc(entry.summary)}</p>
        <div class="chips">
          <span class="chip">${esc(entry.type)}</span>
          <span class="chip">${esc(entry.priority)}</span>
          <span class="chip">${esc(entry.maturity)}</span>
          <span class="chip">${esc(entry.primary_category)}</span>
        </div>
      </article>`).join('');

    cards.querySelectorAll('.card').forEach(card => {
      const open = () => show(card.dataset.id);
      card.addEventListener('click', open);
      card.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open();
        }
      });
    });
  }

  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-view]').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    view = button.dataset.view;
    render();
  }));
  search.addEventListener('input', render);
  render();
})();
