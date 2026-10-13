"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { speakKhmerPayment } = require("../phone_speech.js");

const payment = {
  amount: "12.50",
  currency: "USD",
  announcement: "ទទួលបានប្រាក់ ដប់ពីរដុល្លារ និងហាសិបសេន"
};

test("phone speech says the parsed payment announcement using an actual Khmer voice", () => {
  const spoken = [];
  class FakeUtterance {
    constructor(text) {
      this.text = text;
    }
  }
  const synthesis = {
    getVoices: () => [
      { lang: "en-US", name: "English" },
      { lang: "km-KH", name: "Khmer" }
    ],
    speak: (utterance) => spoken.push(utterance)
  };

  assert.equal(speakKhmerPayment(payment, synthesis, FakeUtterance), true);
  assert.equal(spoken.length, 1);
  assert.equal(spoken[0].text, payment.announcement);
  assert.equal(spoken[0].lang, "km-KH");
  assert.equal(spoken[0].voice.name, "Khmer");
});

test("phone speech does not substitute an English voice when Khmer is unavailable", () => {
  const spoken = [];
  class FakeUtterance {
    constructor(text) {
      this.text = text;
    }
  }
  const synthesis = {
    getVoices: () => [{ lang: "en-US", name: "English" }],
    speak: (utterance) => spoken.push(utterance)
  };

  assert.equal(speakKhmerPayment(payment, synthesis, FakeUtterance), false);
  assert.deepEqual(spoken, []);
});
