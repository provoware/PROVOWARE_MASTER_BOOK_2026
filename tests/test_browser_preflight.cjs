#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const load = name => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const browser = {window: {}};
vm.createContext(browser);
for (const file of ['src/registries.js', 'src/preflight.js']) {
  vm.runInContext(fs.readFileSync(path.join(root, file), 'utf8'), browser, {filename: file});
}
const check = (candidate, seed) => browser.window.PROVOWARE_PREFLIGHT(candidate, seed);
const seed = load('data/masterbook_seed.json');
const inbox = load('data/inbox.json').items;
const byId = Object.fromEntries(inbox.map(c => [c.candidate_id, c]));
assert.equal(check(byId['INBOX-001'], seed).result, 'READY');
assert.equal(check(byId['INBOX-002'], seed).result, 'DUPLICATE');
assert.equal(check(byId['INBOX-003'], seed).result, 'CONFLICT');
assert.equal(check(byId['INBOX-004'], seed).result, 'BLOCKED');

const base = structuredClone(byId['INBOX-001']);
const sourceDuplicate = {...base, candidate_id: 'REG-SOURCE', title: 'Vollständig anderer Titel',
  type: seed[1].type, sources: structuredClone(seed[1].sources)};
assert.equal(check(sourceDuplicate, seed).result, 'DUPLICATE');
assert.equal(check(sourceDuplicate, seed).possible_duplicate_of, seed[1].id);
const differentClaim = structuredClone(sourceDuplicate);
differentClaim.sources[0].claim = 'Andere, eigenständige Behauptung';
assert.equal(check(differentClaim, seed).result, 'READY');

assert.equal(check({...base, primary_category: 'NICHT_VORHANDEN'}, seed).result, 'BLOCKED');
assert.equal(check({...base, categories: ['NICHT_VORHANDEN']}, seed).result, 'BLOCKED');
assert.equal(check({...base, relationships: [{type: 'NICHT_VORHANDEN'}]}, seed).result, 'BLOCKED');
assert.equal(check({...base, type: 'goldene_regel', maturity: 'E2'}, seed).result, 'BLOCKED');
assert.equal(check({...base, sources: []}, seed).result, 'BLOCKED');
const missing = structuredClone(base);
delete missing.summary;
assert.equal(check(missing, seed).result, 'BLOCKED');
assert.equal(check({...base, relationships: [{type: 'widerspricht', target_id: seed[0].id}]}, seed).result, 'CONFLICT');
assert.equal(check({...sourceDuplicate, primary_category: 'NICHT_VORHANDEN'}, seed).result, 'BLOCKED');

for (const [html, controller] of [['index.html','src/app.js'],['preview.html','src/preview.js']]) {
  const markup = fs.readFileSync(path.join(root, html), 'utf8');
  const scriptOrder = ['src/registries.js', 'src/preflight.js', controller].map(src => markup.indexOf('src="' + src + '"'));
  assert(scriptOrder.every(n => n >= 0) && scriptOrder.every((n,i) => i === 0 || n > scriptOrder[i-1]),
    html + ': Browser-Preflight muss vor dem Controller geladen werden');
  assert(fs.readFileSync(path.join(root, controller), 'utf8').includes('window.PROVOWARE_PREFLIGHT('));
}
console.log('PASS: Browser-Preflight READY/DUPLICATE/CONFLICT/BLOCKED, Quellentriple, Negativfälle und beide Ansichten.');
