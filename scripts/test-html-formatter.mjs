import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';

// Run the actual controller with only the framework base class stubbed.
const source = fs.readFileSync('frontend/src/controllers/html_formatter_controller.js', 'utf8')
  .replace('import { Controller } from "@hotwired/stimulus";', 'class Controller {}')
  .replace('export default class', 'globalThis.Formatter = class');
function fixture(input, busy = false) {
  let requests = 0;
  const events = [];
  const context = { window: { bwdTrack: (...args) => events.push(args) },
    fetch: () => { requests++; throw new Error('Example must not submit'); } };
  vm.runInNewContext(source, context);
  const controller = new context.Formatter();
  Object.assign(controller, {
    inputTarget: {value: input, focus() {}}, resultTarget: {value: 'previous output'},
    submitButtonTarget: {disabled: busy}, exampleButtonTarget: {disabled: busy},
    copyButtonTarget: {disabled: false},
    statusTarget: {textContent: '', classList: {add() {}, remove() {}}}
  });
  return {controller, events, requests: () => requests};
}

test('loading an example never submits or overwrites visitor input or an in-flight result', () => {
  for (const [input, busy] of [['', false], ['   ', false], ['<p>My work</p>', false], ['', true]]) {
    const {controller, events, requests} = fixture(input, busy);
    controller.loadExample();
    assert.equal(requests(), 0);
    if (!busy && !input.trim()) {
      assert.match(controller.inputTarget.value, /{% for project in projects %}/);
      assert.equal(controller.resultTarget.value, '');
      assert.equal(controller.copyButtonTarget.disabled, true);
      assert.equal(events.length, 1);
      assert.equal(events[0][0], 'html formatter example loaded');
      assert.equal(Object.keys(events[0][1]).length, 0);
    } else {
      assert.equal(controller.inputTarget.value, input);
      assert.equal(controller.resultTarget.value, 'previous output');
      assert.equal(events.length, 0);
    }
  }
});
