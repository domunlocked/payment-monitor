(() => {
  "use strict";

  const elements = {
    connectionBadge: document.querySelector("#connection-badge"),
    connectionLabel: document.querySelector("#connection-label"),
    startButton: document.querySelector("#start-listening"),
    stopButton: document.querySelector("#stop-listening"),
    listenerMessage: document.querySelector("#listener-message"),
    serviceMessage: document.querySelector("#service-message"),
    waitingMessage: document.querySelector("#waiting-message"),
    paymentDetails: document.querySelector("#payment-details"),
    amount: document.querySelector("#payment-amount"),
    currency: document.querySelector("#payment-currency"),
    khmer: document.querySelector("#payment-khmer"),
    date: document.querySelector("#payment-date"),
    reference: document.querySelector("#payment-reference"),
    referenceRow: document.querySelector("#reference-row"),
    status: document.querySelector("#payment-status"),
    statusRow: document.querySelector("#payment-status-row")
  };

  const isLocalDashboard = location.protocol === "http:"
    && location.hostname === "127.0.0.1"
    && location.port === "8765";
  let polling = false;
  let actionPending = false;
  let pollTimer = null;
  let listenerRunning = false;

  function setConnection(connected) {
    elements.connectionLabel.textContent = connected ? "Connected" : "Disconnected";
    elements.connectionBadge.classList.toggle("status-connected", connected);
    elements.connectionBadge.classList.toggle("status-offline", !connected);
  }

  function showMessage(element, message) {
    element.textContent = message || "";
    element.hidden = !message;
  }

  async function requestJson(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(path, {
        cache: "no-store",
        credentials: "same-origin",
        signal: controller.signal,
        ...options
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(body.detail || `The local service returned HTTP ${response.status}.`);
      }
      return body;
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error("The local service did not respond. Check that it is running.");
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  function renderPayment(payment) {
    const hasPayment = payment && typeof payment === "object";
    elements.waitingMessage.hidden = Boolean(hasPayment);
    elements.paymentDetails.hidden = !hasPayment;
    if (!hasPayment) return;

    elements.amount.textContent = typeof payment.amount === "string" ? payment.amount : "—";
    elements.currency.textContent = typeof payment.currency === "string" ? payment.currency : "";
    elements.date.textContent = payment.payment_datetime || "—";
    elements.reference.textContent = payment.transaction_id || "—";
    elements.referenceRow.hidden = !payment.transaction_id;
    elements.status.textContent = typeof payment.payment_status === "string"
      ? payment.payment_status
      : "";
    elements.statusRow.hidden = !elements.status.textContent;
    elements.khmer.textContent = typeof payment.announcement === "string"
      ? payment.announcement
      : "";
    elements.khmer.hidden = !elements.khmer.textContent;
  }

  function renderListener(status) {
    const connected = status.telegram_connected === true;
    listenerRunning = status.listener_running === true;
    setConnection(connected);
    elements.startButton.disabled = actionPending || listenerRunning || !isLocalDashboard;
    elements.stopButton.disabled = actionPending || !listenerRunning || !isLocalDashboard;
    showMessage(elements.listenerMessage, status.message || "");
  }

  async function refresh() {
    if (!isLocalDashboard || polling) return;
    polling = true;
    try {
      const [status, latest] = await Promise.all([
        requestJson("/api/status"),
        requestJson("/api/latest-payment")
      ]);
      renderListener(status);
      renderPayment(latest.payment);
      showMessage(elements.serviceMessage, "");
    } catch (error) {
      setConnection(false);
      listenerRunning = false;
      elements.startButton.disabled = actionPending;
      elements.stopButton.disabled = true;
      showMessage(elements.serviceMessage, error.message || "Could not reach the local service.");
    } finally {
      polling = false;
      clearTimeout(pollTimer);
      pollTimer = setTimeout(() => void refresh(), 2500);
    }
  }

  async function sendListenerAction(action) {
    if (!isLocalDashboard || actionPending) return;
    actionPending = true;
    let actionError = "";
    elements.startButton.disabled = true;
    elements.stopButton.disabled = true;
    showMessage(
      elements.listenerMessage,
      action === "start" ? "Starting the listener…" : "Stopping the listener…"
    );
    showMessage(elements.serviceMessage, "");
    try {
      const result = await requestJson(`/api/listener/${action}`, { method: "POST" });
      renderListener(result);
    } catch (error) {
      actionError = error.message || "The listener action failed.";
    } finally {
      actionPending = false;
      await refresh();
      if (actionError) showMessage(elements.serviceMessage, actionError);
    }
  }

  elements.startButton.addEventListener("click", () => void sendListenerAction("start"));
  elements.stopButton.addEventListener("click", () => void sendListenerAction("stop"));

  if (!isLocalDashboard) {
    elements.startButton.disabled = true;
    elements.stopButton.disabled = true;
    showMessage(
      elements.listenerMessage,
      "This static page cannot access your private Windows listener. Open http://127.0.0.1:8765 on that computer."
    );
  } else {
    void refresh();
  }
})();
