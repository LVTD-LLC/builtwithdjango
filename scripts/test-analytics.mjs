import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';

// Exercise the actual template initializer, with anonymous Django branches
// resolved and test-only literal values substituted (no live network).
const template = fs.readFileSync('templates/base.html', 'utf8');
const inline = template.slice(template.indexOf('        !function'), template.indexOf('      </script>', template.indexOf('        !function')))
  .replace(/{% if user.is_authenticated %}[\s\S]*?{% else %}([\s\S]*?){% endif %}/g, '$1')
  .replace(/{{[^}]+}}/g, 'test');
function configFixture() {
  let config;
  const handlers = {};
  const posthog = {__SV: 1, init: (_key, value) => { config = value; }, register() {}, capture() {}};
  const context = { URL, posthog, window: {posthog, location: {origin:'https://example.com',host:'example.com',pathname:'/'}},
    document: {addEventListener: (name, fn) => { handlers[name] = fn; }} };
  vm.runInNewContext(inline, context);
  return {config, context, handlers};
}
test('ingestion token survives privacy settings; replay masks and vitals enabled', () => {
  const {config} = configFixture();
  assert.ok(!config.property_denylist.includes('token'));
  assert.ok(config.property_denylist.includes('password'));
  assert.equal(config.capture_performance.web_vitals, true);
  assert.equal(config.session_recording.maskAllInputs, true);
  assert.equal(config.session_recording.maskTextSelector, '*');
  assert.equal(config.person_profiles, 'identified_only');
});
test('logout resets previous identity before pageview', () => {
  const {config} = configFixture();
  let resets = 0;
  config.loaded({get_property: () => '42', reset: () => resets++});
  config.loaded({get_property: () => undefined, reset: () => resets++});
  assert.equal(resets, 1);
});
test('URLs remove sensitive queries, fragments, credentials and auth path tokens', () => {
  const {context} = configFixture();
  const result = context.bwdRedactUrl('https://user:secret@example.com/accounts/confirm-email/private/?token=secret#secret');
  assert.ok(!result.includes('secret'));
  assert.ok(!result.includes('private'));
  assert.ok(!result.includes('user:'));
  assert.ok(context.bwdRedactUrl('/?utm_source=newsletter').includes('utm_source=newsletter'));
});
test('replay omits like polling and network bodies', () => {
  const {config} = configFixture();
  const mask = config.session_recording.maskCapturedNetworkRequestFn;
  assert.equal(mask({name:'https://example.com/api/v1/like/1/'}), null);
  const result = mask({name:'https://example.com/?token=secret',requestBody:'private',responseBody:'private'});
  assert.equal(result.requestBody, undefined);
  assert.equal(result.responseBody, undefined);
  assert.ok(!result.name.includes('secret'));
});
const source = fs.readFileSync('frontend/src/analytics-engagement.js', 'utf8');
const {installEngagement} = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
test('engagement installs once, bounds scroll events and never captures form values', () => {
  const handlers = {}, events = [];
  const doc = { documentElement: {scrollHeight:2000}, addEventListener: (name, fn) => {handlers[name] = fn;} };
  const win = {innerHeight:1000,scrollY:750,bwdTrack:(...args)=>events.push(args),
    addEventListener:(name, fn)=>{handlers[name] = fn;},requestAnimationFrame:fn=>fn()};
  installEngagement(win, doc);
  const firstHandler = handlers.focusin;
  installEngagement(win, doc);
  assert.equal(firstHandler, handlers.focusin);
  const form = {id:'newsletter',getAttribute:()=> 'post',value:'private'};
  handlers.focusin({target:{form,value:'private'}});
  handlers.focusin({target:{form,value:'private'}});
  handlers.invalid({target:{form,value:'private'}});
  handlers.invalid({target:{form,value:'private'}});
  handlers.scroll(); handlers.scroll();
  assert.deepEqual(events.map(e=>e[0]), ['form started','form validation blocked',
    'page scroll depth reached','page scroll depth reached','page scroll depth reached']);
  assert.ok(!JSON.stringify(events).includes('private'));
  handlers['turbo:load'](); handlers.scroll();
  assert.equal(events.length, 8);
});
