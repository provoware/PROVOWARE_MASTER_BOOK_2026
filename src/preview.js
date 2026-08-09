(() => {
  const seed = window.MASTERBOOK_SEED || [];
  const inbox = (window.KNOWLEDGE_INBOX && window.KNOWLEDGE_INBOX.items) || [];
  const list = document.getElementById('candidate-list');
  const plan = document.getElementById('plan');
  const detail = document.getElementById('detail');
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const norm = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase('de').trim().replace(/\s+/g,' ');

  function preflight(candidate) {
    const errors = [];
    if (!candidate.sources || candidate.sources.length === 0) errors.push('Mindestens eine Quelle ist erforderlich');
    if (candidate.type === 'goldene_regel' && candidate.maturity !== 'E5') errors.push('Goldene Regel erfordert E5');
    const duplicate = seed.find(entry => norm(entry.title) === norm(candidate.title));
    const conflicts = (candidate.relationships || []).filter(r => r.type === 'widerspricht' && r.target_id).map(r => r.target_id);
    if (errors.length) return {result:'BLOCKED', errors, duplicate:null, conflicts};
    if (conflicts.length) return {result:'CONFLICT', errors, duplicate:null, conflicts};
    if (duplicate) return {result:'DUPLICATE', errors, duplicate:duplicate.id, conflicts};
    return {result:'READY', errors, duplicate:null, conflicts};
  }

  function stable(value) {
    if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
    if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k)+':'+stable(value[k])).join(',') + '}';
    return JSON.stringify(value);
  }

  async function hashObject(value) {
    if (!globalThis.crypto || !crypto.subtle) return null;
    const bytes = new TextEncoder().encode(stable(value));
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    return 'sha256:' + Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2,'0')).join('');
  }

  function nextId(type) {
    const prefix = {automatisierung:'AUTO',regel:'RULE',standard:'STD',goldene_regel:'GOLD',beobachtung:'OBS',erkenntnis:'ERK',fehler:'ERROR',anti_pattern:'ANTI',wenn_dann:'WHEN',notiz:'NOTE',offene_frage:'OPEN',entscheidung:'DEC'}[type] || 'ENTRY';
    const nums = seed.map(e => new RegExp('^'+prefix+'-(\\d+)$').exec(e.id)).filter(Boolean).map(m => Number(m[1]));
    return `${prefix}-${String(Math.max(0,...nums)+1).padStart(3,'0')}`;
  }

  async function show(candidate) {
    const check = preflight(candidate);
    if (check.result !== 'READY') {
      plan.innerHTML = `<h2>PREVIEW_BLOCKED</h2><p><strong>${esc(candidate.candidate_id)}</strong> erzeugt keinen Create-Plan.</p><p>Grund: ${esc(check.result)}</p>`;
      detail.innerHTML = '<h2>Undo</h2><p>NOT_APPLICABLE – es wurde kein Zielzustand erzeugt.</p>';
      return;
    }
    const after = {
      id: nextId(candidate.type), type:candidate.type, title:candidate.title, summary:candidate.summary,
      primary_category:candidate.primary_category, categories:[...(candidate.categories||[])], tags:[...(candidate.tags||[])],
      projects:[...(candidate.projects||['PROVOWARE Knowledge & Project Intelligence'])], priority:candidate.priority,
      maturity:candidate.maturity, scope:candidate.scope, automatable:Boolean(candidate.automatable),
      status:['E0','E1'].includes(candidate.maturity) ? 'neu' : 'bestaetigt', revision:1, sources:[...(candidate.sources||[])]
    };
    const hash = await hashObject(after);
    plan.innerHTML = `<h2>PREVIEW_READY</h2><p><strong>Operation:</strong> create</p><p><strong>Ziel-ID:</strong> ${esc(after.id)}</p><p><strong>Titel:</strong> ${esc(after.title)}</p><p><strong>SHA-256:</strong> ${hash ? esc(hash) : 'BLOCKED – Web-Crypto in diesem Kontext nicht verfügbar'}</p><p><strong>Delta:</strong> neu · PREVIEW_ONLY</p>`;
    detail.innerHTML = `<h2>Undo-Vorschau</h2><p><strong>Operation:</strong> delete_created_entry</p><p><strong>Ziel:</strong> ${esc(after.id)}</p><p><strong>Status:</strong> PREVIEW_ONLY</p><p>Es wurde nichts gespeichert.</p>`;
  }

  list.innerHTML = inbox.map(c => { const s=preflight(c).result; return `<button data-id="${esc(c.candidate_id)}">${esc(c.candidate_id)} · ${esc(s)}</button>`; }).join('');
  list.querySelectorAll('button').forEach(button => button.addEventListener('click', () => show(inbox.find(c => c.candidate_id === button.dataset.id))));
})();
