(function (root, createTracker) {
  "use strict";
  const PaymentNotificationTracker = createTracker();
  if (typeof module === "object" && module.exports) {
    module.exports = PaymentNotificationTracker;
  } else {
    root.PaymentNotificationTracker = PaymentNotificationTracker;
  }
})(globalThis, function () {
  "use strict";

  return class PaymentNotificationTracker {
    constructor() {
      this.cursor = 0;
      this.initialized = false;
      this.spokenIds = new Set();
    }

    initialize(payments, cursor) {
      this.cursor = Math.max(
        Number(cursor) || 0,
        ...payments.map((payment) => Number(payment.id) || 0)
      );
      this.spokenIds.clear();
      this.initialized = true;
    }

    receive(payments, { listening, speakerEnabled }) {
      if (!this.initialized) {
        this.initialize(payments, 0);
        return [];
      }
      const speakable = [];
      for (const payment of payments) {
        const id = Number(payment.id) || 0;
        if (id <= this.cursor) continue;
        this.cursor = id;
        if (!listening || !speakerEnabled) continue;
        const speechId = String(payment.id || payment.transaction_id || "");
        if (!speechId || this.spokenIds.has(speechId)) continue;
        this.spokenIds.add(speechId);
        speakable.push(payment);
      }
      return speakable;
    }
  };
});
