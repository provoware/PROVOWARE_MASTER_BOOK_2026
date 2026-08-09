(() => {
  const entries = window.MASTERBOOK_SEED || [];
  const inbox = (window.KNOWLEDGE_INBOX && window.KNOWLEDGE_INBOX.items) || [];
  let view = 'all';
  const cards = document.getElementById('cards');
  const search = document.getElementById('search');
  const count = document.getElementById('count');
  const detail = document.getElementById('detail');

  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const norm = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase('de').trim().replace(/\s+/g, ' ');

  function preflight(candidate) {
    const errors = [];
    const required = ['candidate_id','title','summary','type','primary_category','categories','priority','maturity','scope','sources','status'];
    for (const key of required) {
      if (!(key in candidate)) errors.push(`Pflichtfeld fehlt: ${key}`);
    }
    if (!candidate.sources || candidate.sources.length === 0) errors.push('Mindestens eine Quelle ist erforderlich');
    if (candidate.type === 'goldene_regel' && candidate.maturity !== 'E5') errors.push('Goldene Regel erfordert E5');

    const duplicate = entries.find(entry => norm(entry.title) === norm(candidate.title));
    const conflicts = (candidate.relationships || [])
      .filter(rel => rel.type === 'widerspricht' && rel.target_id)
      .map(rel => rel.target_id);

    let result = 'READY';
    if (errors.length) result = 'BLOCKED';
    else if (conflicts.length) result = 'CONFLICT';
    else if (duplicate) result = 'DUPLICATE';

    return {
      result,
      errors,
      possible_duplicate_of: duplicate ? duplicate.id : null,
      conflict_with: conflicts
    };
  }

  function matches(entry, query) {
    const haystack = [entry.id, entry.type, entry.title, entry.summary, entry.primary_category, ...(entry.categories || []), ...(entry.tags || []), ...(entry.projects || []), entry.priority, entry.maturity, entry.status].join(' ').toLowerCase();
    return !query || haystack.includes(query.toLowerCase());
  }

  function visible(entry) {
    return view === 'all' || entry.priority === view || entry.type === view;
  }

  function showEntry(id) {
    const entry = entries.find(item => item.id === id);
    if (!entry) return;
    detail.innerHTML = `
      <h2>${esc(entry.id)}</h2>
      <h3>${esc(entry.title)}</h3>
      <p><strong>Was ist das?</strong><br>${esc(entry.summary)}</p>
      <p><strong>Warum wichtig?</strong><br>Priorität ${esc(entry.priority)} · Reife ${esc(entry.maturity)}</p>
      <p><strong>Was soll ich tun?</strong><br>${entry.status === 'standard' ? 'Als gültigen Standard berücksichtigen.' : 'Als bestätigten Wissenseintrag berücksichtigen; keine automatische Hochstufung.'}</p>
      <p><strong>Kategorien</strong><br>${esc([entry.primary_category, ...(entry.categories || [])].join(' · '))}</p>
      <p><strong>Quelle</strong><br>${esc((entry.sources || []).map(source => source.ref).join(' · '))}</p>`;
  }

  function showInbox(id) {
    const candidate = inbox.find(item => item.candidate_id === id);
    if (!candidate) return;
    const check = preflight(candidate);
    const reason = check.result === 'READY'
      ? 'Die deterministische Basisprüfung fand keinen Blocker.'
      : check.result === 'DUPLICATE'
        ? `Exakter Titel bereits vorhanden: ${check.possible_duplicate_of}.`
        : check.result === 'CONFLICT'
          ? `Expliziter Widerspruch zu: ${check.conflict_with.join(', ')}.`
          : check.errors.join(' · ');
    detail.innerHTML = `
      <h2>${esc(candidate.candidate_id)}</h2>
      <h3>${esc(candidate.title)}</h3>
      <p><strong>Vorprüfung</strong><br><span class="status status-${esc(check.result.toLowerCase())}">${esc(check.result)}</span></p>
      <p><strong>Was ist das?</strong><br>${esc(candidate.summary)}</p>
      <p><strong>Warum dieser Zustand?</strong><br>${esc(reason)}</p>
      <p><strong>Was soll ich tun?</strong><br>${check.result === 'READY' ? 'Kann später zur manuellen Übernahme angeboten werden.' : check.result === 'DUPLICATE' ? 'Bestehenden Eintrag prüfen und bevorzugt ergänzen.' : check.result === 'CONFLICT' ? 'Widerspruch fachlich prüfen; nicht automatisch auflösen.' : 'Nicht übernehmen, bis die Blocker behoben sind.'}</p>
      <p><strong>Reife / Priorität</strong><br>${esc(candidate.maturity)} · ${esc(candidate.priority)}</p>
      <p><strong>Quelle</strong><br>${esc((candidate.sources || []).map(source => source.ref).join(' · '))}</p>`;
  }

  function bindCards(handler, key) {
    cards.querySelectorAll('.card').forEach(card => {
      const open = () => handler(card.dataset[key]);
      card.addEventListener('click', open);
      card.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open();
        }
      });
    });
  }

  function renderInbox() {
    const query = search.value.trim().toLowerCase();
    const filtered = inbox.filter(candidate => {
      const check = preflight(candidate);
      const haystack = [candidate.candidate_id,candidate.title,candidate.summary,candidate.type,candidate.primary_category,candidate.priority,candidate.maturity,check.result].join(' ').toLowerCase();
      return !query || haystack.includes(query);
    });
    count.textContent = `${filtered.length} Eingangskandidaten`;
    cards.innerHTML = filtered.map(candidate => {
      const check = preflight(candidate);
      return `
        <article class="card" tabindex="0" data-candidate-id="${esc(candidate.candidate_id)}">
          <div class="card-head"><h3>${esc(candidate.candidate_id)} · ${esc(candidate.title)}</h3><span class="status status-${esc(check.result.toLowerCase())}">${esc(check.result)}</span></div>
          <p>${esc(candidate.summary)}</p>
          <div class="chips">
            <span class="chip">${esc(candidate.type)}</span>
            <span class="chip">${esc(candidate.priority)}</span>
            <span class="chip">${esc(candidate.maturity)}</span>
          </div>
        </article>`;
    }).join('');
    bindCards(showInbox, 'candidateId');
  }

  function renderEntries() {
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
    bindCards(showEntry, 'id');
  }

  function render() {
    if (view === 'inbox') renderInbox();
    else renderEntries();
  }

  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-view]').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    view = button.dataset.view;
    detail.innerHTML = view === 'inbox'
      ? '<h2>Wissenseingang</h2><p>Nur lesen: Vorprüfzustände werden sichtbar erklärt. Es erfolgt keine Übernahme oder Datenänderung.</p>'
      : '<h2>Eintrag wählen</h2><p>Was ist das? Warum wichtig? Was soll ich tun?</p>';
    render();
  }));

  search.addEventListener('input', render);
  render();
})();
