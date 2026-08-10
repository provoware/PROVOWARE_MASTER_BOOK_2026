window.KNOWLEDGE_INBOX = {
  schema_version: '1.0',
  items: [
    {
      candidate_id: 'INBOX-001',
      title: 'Knowledge Delta pro Iteration protokollieren',
      summary: 'Jede Iteration soll maschinenlesbar festhalten, was neu, geändert, zusammengeführt oder als Konflikt markiert wurde.',
      type: 'automatisierung',
      primary_category: 'Wissenskonsolidierung',
      categories: ['Evidence & Audit', 'Automation'],
      priority: 'P1',
      maturity: 'E1',
      scope: 'projekt',
      sources: [{kind:'projektchat',ref:'Wissensspeicher Autopilot – Iteration 002',claim:'Als nächster Verbesserungshebel wurde ein maschinenlesbares Knowledge-Delta vorgeschlagen.'}],
      status: 'neu'
    },
    {
      candidate_id: 'INBOX-002',
      title: 'Ein Wissenseintrag einmal speichern, vielfach anzeigen',
      summary: 'Mehrfachsichtbarkeit soll nicht durch Datenkopien entstehen.',
      type: 'regel',
      primary_category: 'Informationsarchitektur',
      categories: ['Daten & Integrität'],
      priority: 'P0',
      maturity: 'E2',
      scope: 'projekt',
      sources: [{kind:'projektdatei',ref:'WISSENSSPEICHERBUCH_UND_TOOL.txt',claim:'Ein Eintrag darf mehrfach sichtbar sein, aber nur einmal gespeichert werden.'}],
      status: 'neu'
    },
    {
      candidate_id: 'INBOX-003',
      title: 'Mehrfachsichtbarkeit durch Kopien erlauben',
      summary: 'Für jede Navigationssicht könnte eine eigene Kopie eines Wissenseintrags gespeichert werden.',
      type: 'entscheidung',
      primary_category: 'Informationsarchitektur',
      categories: ['Daten & Integrität'],
      priority: 'P1',
      maturity: 'E0',
      scope: 'projekt',
      sources: [{kind:'projektchat',ref:'Störfallkandidat I003',claim:'Absichtlich widersprechender Testkandidat für die Konfliktdarstellung.'}],
      relationships: [{type:'widerspricht',target_id:'RULE-002'}],
      status: 'neu'
    },
    {
      candidate_id: 'INBOX-004',
      title: 'Ungeprüfte Idee sofort als Goldene Regel übernehmen',
      summary: 'Neue hoch priorisierte Erkenntnisse sollen unmittelbar E5 erhalten.',
      type: 'goldene_regel',
      primary_category: 'Governance',
      categories: ['Goldene Regeln'],
      priority: 'P0',
      maturity: 'E1',
      scope: 'projekt',
      sources: [{kind:'projektchat',ref:'Störfallkandidat I003',claim:'Absichtlich ungültiger Testkandidat für die BLOCKED-Darstellung.'}],
      status: 'neu'
    },
    {
      candidate_id: 'INBOX-005',
      title: 'Dateiidentität unmittelbar vor Mutation erneut prüfen',
      summary: 'Eine erfolgreiche Pfad- oder Symlinkprüfung darf keine spätere Objektidentität garantieren. Vor mutierenden Dateisystemschritten muss ein read-only Identitätssnapshot erneut fail-closed verglichen werden.',
      type: 'regel',
      primary_category: 'Daten & Integrität',
      categories: ['Dateisystem', 'Fehlervermeidung', 'Evidence & Audit', 'Tests'],
      priority: 'P0',
      maturity: 'E1',
      scope: 'projektübergreifend',
      projects: ['PROVOWARE', 'PROVOWARE Knowledge & Project Intelligence'],
      automatable: true,
      tags: ['TOCTOU', 'Stale Guard', 'Device', 'Inode', 'Fail Closed'],
      sources: [
        {kind:'projektdatei',ref:'provoware/PROVOWARE: docs/WISSENSSPEICHER_I014_ERKENNTNIS.json',claim:'I014 modelliert die TOCTOU-Lücke vor der ersten mutierenden Dateisystemprimitive als E1/P0-Regelentwurf.'},
        {kind:'projektdatei',ref:'provoware/PROVOWARE: docs/PLAN_DELTA_I014.json',claim:'Die ursprünglichen mutierenden P03-Schritte werden bis zur qualifizierten read-only Identitätsprüfung aufgeschoben.'}
      ],
      status: 'neu'
    }
  ]
};
