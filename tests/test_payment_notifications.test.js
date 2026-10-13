"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const PaymentNotificationTracker = require("../payment_notifications.js");

function payment(id) {
  return { id, transaction_id: `fixture-${id}`, amount: "12.50", currency: "USD" };
}

test("existing history initializes the cursor silently", () => {
  const tracker = new PaymentNotificationTracker();
  tracker.initialize([payment(1), payment(2)], 2);
  assert.deepEqual(tracker.receive([payment(1), payment(2)], {
    listening: true,
    speakerEnabled: true
  }), []);
});

test("only new transactions are spoken once while both controls are enabled", () => {
  const tracker = new PaymentNotificationTracker();
  tracker.initialize([payment(8)], 8);
  const options = { listening: true, speakerEnabled: true };
  assert.deepEqual(tracker.receive([payment(9)], options), [payment(9)]);
  assert.deepEqual(tracker.receive([payment(9)], options), []);
  assert.deepEqual(tracker.receive([payment(10)], {
    listening: false,
    speakerEnabled: true
  }), []);
  assert.deepEqual(tracker.receive([payment(11)], {
    listening: true,
    speakerEnabled: false
  }), []);
  assert.deepEqual(tracker.receive([payment(12)], options), [payment(12)]);
});

test("a fresh browser instance does not announce transactions already stored", () => {
  const reopened = new PaymentNotificationTracker();
  assert.deepEqual(reopened.receive([payment(20), payment(21)], {
    listening: true,
    speakerEnabled: true
  }), []);
  assert.deepEqual(reopened.receive([payment(22)], {
    listening: true,
    speakerEnabled: true
  }), [payment(22)]);
});
