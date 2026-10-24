(() => {
  'use strict';
  const normalize = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase('de').replace(/ß/g, 'ss').trim().replace(/\s+/g, ' ');
  const sourceKey = source => source && typeof source === 'object' &&
    ['kind', 'ref', 'claim'].every(key => typeof source[key] === 'string' && source[key].length)
    ? JSON.stringify([source.kind, source.ref, source.claim]) : null;

  function preflight(candidate, seed) {
    const errors = [];
    const required = ['candidate_id', 'title', 'summary', 'type', 'primary_category',
      'categories', 'priority', 'maturity', 'scope', 'sources', 'status'];
    for (const key of required) {
      if (!Object.prototype.hasOwnProperty.call(candidate, key)) errors.push('Pflichtfeld fehlt: ' + key);
    }
    const categories = new Set((window.MASTERBOOK_CATEGORIES || []).flatMap(c => [c.id, c.label]));
    const relationTypes = new Set((window.MASTERBOOK_RELATIONSHIP_TYPES || []).map(r => r.id));
    if (!categories.has(candidate.primary_category)) errors.push('Unbekannte Hauptkategorie');
    if (!Array.isArray(candidate.categories)) errors.push('Kategorien müssen eine Liste sein');
    else for (const category of candidate.categories) {
      if (!categories.has(category)) errors.push('Unbekannte Kategorie: ' + category);
    }
    if (candidate.relationships !== undefined && !Array.isArray(candidate.relationships)) {
      errors.push('Beziehungen müssen eine Liste sein');
    }
    const relationships = Array.isArray(candidate.relationships) ? candidate.relationships : [];
    for (const rel of relationships) {
      if (!rel || !relationTypes.has(rel.type)) errors.push('Unbekannter Beziehungstyp: ' + (rel && rel.type));
    }
    if (candidate.type === 'goldene_regel' && candidate.maturity !== 'E5') errors.push('Goldene Regel erfordert E5');
    if (!Array.isArray(candidate.sources) || candidate.sources.length === 0) {
      errors.push('Mindestens eine Quelle ist erforderlich');
    }
    const sourceKeys = new Set((Array.isArray(candidate.sources) ? candidate.sources : [])
      .map(sourceKey).filter(Boolean));
    const title = normalize(candidate.title);
    const duplicate = seed.find(entry => {
      if (title && normalize(entry.title) === title) return true;
      if (candidate.type !== entry.type || sourceKeys.size === 0) return false;
      return (Array.isArray(entry.sources) ? entry.sources : []).some(source => sourceKeys.has(sourceKey(source)));
    });
    const conflicts = relationships.filter(rel => rel && rel.type === 'widerspricht' && rel.target_id)
      .map(rel => rel.target_id);
    const result = errors.length ? 'BLOCKED' : conflicts.length ? 'CONFLICT'
      : duplicate ? 'DUPLICATE' : 'READY';
    return {result, errors, warnings: [], possible_duplicate_of: duplicate ? duplicate.id : null,
      conflict_with: conflicts, candidate_id: candidate.candidate_id};
  }
  window.PROVOWARE_PREFLIGHT = preflight;
})();
