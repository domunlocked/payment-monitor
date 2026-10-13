(() => {
  "use strict";

  const elements = {
    connectionBadge: document.querySelector("#connection-badge"),
    connectionLabel: document.querySelector("#connection-label"),
    connectionSource: document.querySelector("#connection-source"),
    remoteAccessCard: document.querySelector("#remote-access-card"),
    remoteAccessForm: document.querySelector("#remote-access-form"),
    connectButton: document.querySelector("#connect-button"),
    forgetKeyButton: document.querySelector("#forget-key-button"),
    remoteAccessKey: document.querySelector("#remote-access-key"),
    startButton: document.querySelector("#start-listening"),
    stopButton: document.querySelector("#stop-listening"),
    speakerButton: document.querySelector("#speaker-toggle"),
    speakerLabel: document.querySelector("#speaker-label"),
    listenerMessage: document.querySelector("#listener-message"),
    serviceMessage: document.querySelector("#service-message"),
    syncStatus: document.querySelector("#sync-status"),
    waitingMessage: document.querySelector("#waiting-message"),
    paymentDetails: document.querySelector("#payment-details"),
    paymentCard: document.querySelector("#last-payment-card"),
    amount: document.querySelector("#payment-amount"),
    currency: document.querySelector("#payment-currency"),
    khmer: document.querySelector("#payment-khmer"),
    date: document.querySelector("#payment-date"),
    reference: document.querySelector("#payment-reference"),
    referenceRow: document.querySelector("#reference-row"),
    status: document.querySelector("#payment-status"),
    statusRow: document.querySelector("#payment-status-row"),
    history: document.querySelector("#payment-history"),
    historyEmpty: document.querySelector("#history-empty")
  };

  const remoteConfig = window.PAYMENT_MONITOR_REMOTE || {};
  const isLocalDashboard = location.protocol === "http:"
    && location.hostname === "127.0.0.1"
    && location.port === "8765";
  let remoteApiBaseUrl = "";
  try {
    const parsedApiUrl = new URL(remoteConfig.apiBaseUrl || "");
    if (parsedApiUrl.protocol === "https:" && parsedApiUrl.pathname === "/"
      && !parsedApiUrl.search && !parsedApiUrl.hash && !parsedApiUrl.username
      && !parsedApiUrl.password) {
      remoteApiBaseUrl = parsedApiUrl.origin;
    }
  } catch {
    remoteApiBaseUrl = "";
  }
  const isRemoteConfigured = !isLocalDashboard && Boolean(remoteApiBaseUrl);
  const tokenStorageKey = "payment-monitor-remote-key-v1";
  let polling = false;
  let actionPending = false;
  let pollTimer = null;
  let listenerRunning = false;
  let localInitialized = false;
  let phoneListening = false;
  let speakerEnabled = false;
  let remoteAccessKey = null;
  let remoteInitialized = false;
  const remotePaymentTracker = new PaymentNotificationTracker();
  let remoteOnline = false;
  let remoteGeneration = 0;
  let localCursor = 0;
  const spokenIds = new Set();

  function setConnection(connected) {
    elements.connectionLabel.textContent = connected ? "Connected" : "Disconnected";
    elements.connectionBadge.classList.toggle("status-connected", connected);
    elements.connectionBadge.classList.toggle("status-offline", !connected);
  }

  function highlightNewPayment() {
    elements.paymentCard.classList.add("payment-arrived");
    setTimeout(() => elements.paymentCard.classList.remove("payment-arrived"), 2200);
  }

  function showMessage(element, message) {
    element.textContent = message || "";
    element.hidden = !message;
  }

  highlightNewPayment();

  async function requestJson(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    const remote = !isLocalDashboard;
    const headers = new Headers(options.headers || {});
    if (remote && remoteAccessKey) {
      headers.set("Authorization", `Bearer ${remoteAccessKey}`);
    }
    try {
      const response = await fetch(remote ? `${remoteApiBaseUrl}${path}` : path, {
        cache: "no-store",
        ...options,
        credentials: remote ? "omit" : "same-origin",
        headers,
        signal: controller.signal,
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        if (remote && response.status === 401) {
          throw new Error("The private access key was rejected. Check it or use Forget key.");
        }
        throw new Error(body.detail || `The service returned HTTP ${response.status}.`);
      }
      return body;
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error(remote
          ? "The PC did not respond. Check that it is running and connected to the tunnel."
          : "The local service did not respond. Check that it is running.");
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }

  function forgetRemoteKey() {
    remoteGeneration += 1;
    sessionStorage.removeItem(tokenStorageKey);
    remoteAccessKey = null;
    phoneListening = false;
    remoteInitialized = false;
    remoteOnline = false;
    speakerEnabled = false;
    elements.speakerButton.setAttribute("aria-pressed", "false");
    elements.speakerLabel.textContent = "Speaker Off";
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    renderPayment(null);
    renderHistory([]);
    showRemoteAccess();
  }

  function loadRemoteKey() {
    try {
      const value = sessionStorage.getItem(tokenStorageKey) || "";
      if (/^[A-Za-z0-9_-]{32,}$/.test(value)) remoteAccessKey = value;
    } catch {
      sessionStorage.removeItem(tokenStorageKey);
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

  function renderHistory(payments) {
    elements.history.replaceChildren();
    elements.historyEmpty.hidden = payments.length > 0;
    elements.historyEmpty.textContent = payments.length
      ? ""
      : remoteAccessKey || isLocalDashboard
        ? "No payments have arrived yet."
        : "Enter your private access key to load payment history.";
    for (const payment of payments) {
      const item = document.createElement("li");
      const amount = document.createElement("strong");
      const date = document.createElement("span");
      const reference = document.createElement("span");
      amount.textContent = `${payment.amount} ${payment.currency}`;
      date.textContent = payment.payment_datetime || "—";
      reference.textContent = payment.transaction_id || "";
      item.append(amount, date, reference);
      elements.history.append(item);
    }
  }

  function renderListener(status) {
    listenerRunning = status.listener_running === true;
    setConnection(status.telegram_connected === true);
    if (isLocalDashboard) {
      elements.startButton.disabled = actionPending || listenerRunning;
      elements.stopButton.disabled = actionPending || !listenerRunning;
    } else {
      elements.startButton.disabled = actionPending || phoneListening || !remoteAccessKey;
      elements.stopButton.disabled = actionPending || !phoneListening;
    }
    showMessage(elements.listenerMessage, status.message || "");
  }

  function currentKhmerVoice() {
    if (!("speechSynthesis" in window)) return null;
    return PaymentMonitorSpeech.findKhmerVoice(window.speechSynthesis);
  }

  function speakPayment(payment) {
    const id = String(payment.id || payment.transaction_id || "");
    if (!id || spokenIds.has(id)) return;
    spokenIds.add(id);
    if (spokenIds.size > 500) spokenIds.delete(spokenIds.values().next().value);
    const spoken = "speechSynthesis" in window
      && typeof SpeechSynthesisUtterance !== "undefined"
      && PaymentMonitorSpeech.speakKhmerPayment(
        payment,
        window.speechSynthesis,
        SpeechSynthesisUtterance
      );
    if (!spoken) {
      showMessage(
        elements.serviceMessage,
        "Your phone has no Khmer speech voice available. Payments still appear, but will not be spoken."
      );
    }
  }

  function setSpeaker(enabled) {
    speakerEnabled = enabled;
    elements.speakerButton.setAttribute("aria-pressed", String(enabled));
    elements.speakerLabel.textContent = enabled ? "Speaker On" : "Speaker Off";
    if (!enabled && "speechSynthesis" in window) window.speechSynthesis.cancel();
    if (enabled && !currentKhmerVoice()) {
      showMessage(
        elements.serviceMessage,
        "No Khmer speech voice is available in this browser. Do not use an English voice as a substitute."
      );
    } else if (enabled && !phoneListening && !isLocalDashboard) {
      showMessage(elements.serviceMessage, "Speaker is on. Press Start Listening to announce new payments.");
    } else {
      showMessage(elements.serviceMessage, "");
    }
    if (enabled) {
      const voice = currentKhmerVoice();
      if (voice) {
        const prompt = new SpeechSynthesisUtterance("ការជូនដំណឹងការទូទាត់បានបើក");
        prompt.lang = voice.lang;
        prompt.voice = voice;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(prompt);
      }
    }
  }

  async function refreshLocal() {
    if (polling) return;
    polling = true;
    try {
      const [status, result] = await Promise.all([
        requestJson("/api/status"),
        requestJson(
          localInitialized ? `/api/payments?after_id=${localCursor}` : "/api/payments?limit=50"
        )
      ]);
      renderListener(status);
      const payments = result.payments || [];
      if (!localInitialized || result.initial) {
        localInitialized = true;
        localCursor = Number(result.cursor || 0);
        renderHistory(payments.slice().reverse());
        if (payments.length) renderPayment(payments[payments.length - 1]);
      } else if (payments.length) {
        for (const payment of payments) {
          localCursor = Math.max(localCursor, Number(payment.id || 0));
          if (speakerEnabled && phoneListening) speakPayment(payment);
        }
        highlightNewPayment();
        const historyResult = await requestJson("/api/payments?limit=50");
        renderHistory((historyResult.payments || []).slice().reverse());
        renderPayment(payments[payments.length - 1]);
      }
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
      pollTimer = setTimeout(() => void refreshLocal(), 2500);
    }
  }

  async function sendListenerAction(action) {
    if (!isLocalDashboard || actionPending) return;
    actionPending = true;
    elements.startButton.disabled = true;
    elements.stopButton.disabled = true;
    showMessage(
      elements.listenerMessage,
      action === "start" ? "Starting the Telegram listener…" : "Stopping the Telegram listener…"
    );
    try {
      renderListener(await requestJson(`/api/listener/${action}`, { method: "POST" }));
      phoneListening = action === "start";
    } catch (error) {
      showMessage(elements.serviceMessage, error.message || "The listener action failed.");
    } finally {
      if (action === "stop" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      actionPending = false;
      await refreshLocal();
    }
  }

  async function refreshRemote() {
    if (!remoteAccessKey || polling || !isRemoteConfigured) return;
    const requestGeneration = remoteGeneration;
    polling = true;
    try {
      const [status, result] = await Promise.all([
        requestJson("/api/status"),
        requestJson(remoteInitialized
          ? `/api/payments?after_id=${remotePaymentTracker.cursor}`
          : "/api/payments?limit=50")
      ]);
      if (requestGeneration !== remoteGeneration || !remoteAccessKey) return;
      remoteOnline = true;
      renderListener(status);
      const rows = result.payments || [];
      if (!remoteInitialized || result.initial) {
        remoteInitialized = true;
        remotePaymentTracker.initialize(rows, Number(result.cursor || 0));
        renderHistory(rows.slice().reverse());
        if (rows.length) renderPayment(rows[rows.length - 1]);
      } else if (rows.length) {
        const speakable = remotePaymentTracker.receive(rows, {
          listening: phoneListening,
          speakerEnabled
        });
        for (const payment of speakable) speakPayment(payment);
        highlightNewPayment();
        const recent = await requestJson("/api/payments?limit=50");
        if (requestGeneration !== remoteGeneration || !remoteAccessKey) return;
        renderHistory((recent.payments || []).slice().reverse());
        renderPayment(rows[rows.length - 1]);
      }
      const checkedAt = status.server_time ? new Date(status.server_time) : new Date();
      const lastPaymentAt = status.last_payment_received_at
        ? new Date(status.last_payment_received_at)
        : null;
      const lastPaymentText = lastPaymentAt && Number.isFinite(lastPaymentAt.getTime())
        ? ` · last payment received ${lastPaymentAt.toLocaleString()}`
        : " · no payments received yet";
      showMessage(
        elements.syncStatus,
        `PC online · checked ${checkedAt.toLocaleTimeString()}${lastPaymentText}`
      );
      showMessage(elements.serviceMessage, "");
    } catch (error) {
      if (requestGeneration !== remoteGeneration || !remoteAccessKey) return;
      remoteOnline = false;
      setConnection(false);
      showMessage(elements.syncStatus, "PC or tunnel offline. Retrying automatically.");
      showMessage(elements.serviceMessage, error.message || "Could not refresh private payments.");
    } finally {
      polling = false;
      clearTimeout(pollTimer);
      if (remoteAccessKey) pollTimer = setTimeout(() => void refreshRemote(), 2500);
    }
  }

  async function waitForPoll() {
    while (polling) await new Promise((resolve) => setTimeout(resolve, 25));
  }

  function showRemoteAccess() {
    elements.connectionSource.textContent = "WINDOWS PC";
    elements.remoteAccessCard.hidden = !isRemoteConfigured;
    elements.remoteAccessForm.hidden = Boolean(remoteAccessKey);
    elements.forgetKeyButton.hidden = !remoteAccessKey;
    elements.startButton.disabled = !remoteAccessKey || phoneListening;
    elements.stopButton.disabled = !phoneListening;
    elements.speakerButton.disabled = false;
    if (!isRemoteConfigured) {
      showMessage(elements.listenerMessage, "The website owner must configure the protected PC API address.");
      showMessage(elements.historyEmpty, "Remote dashboard setup is not complete.");
    } else if (remoteAccessKey) {
      showMessage(elements.listenerMessage, "Connected access key saved for this tab. The Windows PC runs Telegram.");
      void refreshRemote();
    } else {
      setConnection(false);
      showMessage(elements.listenerMessage, "Enter your private key to view payments. Telegram login stays on the Windows PC.");
      showMessage(elements.historyEmpty, "Connect to load payment history.");
    }
  }

  elements.speakerButton.addEventListener("click", () => setSpeaker(!speakerEnabled));

  elements.remoteAccessForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const candidate = elements.remoteAccessKey.value.trim();
    if (!isRemoteConfigured || actionPending || !/^[A-Za-z0-9_-]{32,}$/.test(candidate)) {
      showMessage(elements.serviceMessage, "Enter the private access key (at least 32 letters, numbers, hyphens, or underscores).");
      return;
    }
    actionPending = true;
    elements.connectButton.disabled = true;
    showMessage(elements.serviceMessage, "");
    try {
      remoteAccessKey = candidate;
      sessionStorage.setItem(tokenStorageKey, candidate);
      elements.remoteAccessKey.value = "";
      showRemoteAccess();
      await waitForPoll();
      await refreshRemote();
      if (remoteOnline) showMessage(elements.serviceMessage, "");
    } catch (error) {
      remoteAccessKey = null;
      showMessage(elements.serviceMessage, error.message || "Could not connect to the PC.");
    } finally {
      actionPending = false;
      elements.connectButton.disabled = false;
    }
  });

  elements.forgetKeyButton.addEventListener("click", forgetRemoteKey);

  elements.startButton.addEventListener("click", async () => {
    if (isLocalDashboard) {
      await sendListenerAction("start");
      return;
    }
    if (!remoteAccessKey || actionPending) return;
    actionPending = true;
    elements.startButton.disabled = true;
    try {
      await waitForPoll();
      if (!remoteInitialized) await refreshRemote();
      if (!remoteOnline || !remoteInitialized) {
        throw new Error("Connect to the PC before starting phone listening.");
      }
      phoneListening = true;
      elements.startButton.disabled = true;
      elements.stopButton.disabled = false;
      if ("speechSynthesis" in window) window.speechSynthesis.resume();
      showMessage(elements.listenerMessage, "Listening for new payments on this phone.");
      if (speakerEnabled && !currentKhmerVoice()) {
        showMessage(
          elements.serviceMessage,
          "The phone has no Khmer speech voice. New payments will appear silently."
        );
      }
    } catch (error) {
      showMessage(elements.serviceMessage, error.message || "Could not start phone listening.");
      elements.startButton.disabled = !remoteAccessKey;
      elements.stopButton.disabled = true;
    } finally {
      actionPending = false;
    }
  });

  elements.stopButton.addEventListener("click", () => {
    if (isLocalDashboard) {
      void sendListenerAction("stop");
      return;
    }
    phoneListening = false;
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    elements.startButton.disabled = !remoteAccessKey;
    elements.stopButton.disabled = true;
    showMessage(elements.listenerMessage, "Phone announcements are stopped. The PC listener continues.");
  });

  if (isLocalDashboard) {
    elements.remoteAccessCard.hidden = true;
    elements.startButton.disabled = true;
    elements.stopButton.disabled = true;
    elements.speakerButton.disabled = false;
    void refreshLocal();
  } else if (!isRemoteConfigured) {
    elements.startButton.disabled = true;
    elements.stopButton.disabled = true;
    showMessage(elements.listenerMessage, "The protected PC API URL is not configured on this website.");
    showMessage(elements.serviceMessage, "Set apiBaseUrl in remote-config.js to the HTTPS tunnel hostname.");
  } else {
    loadRemoteKey();
    showRemoteAccess();
  }

  if ("speechSynthesis" in window) {
    window.speechSynthesis.addEventListener("voiceschanged", () => {
      if (speakerEnabled && !currentKhmerVoice()) {
        showMessage(elements.serviceMessage, "No Khmer speech voice is available on this device.");
      }
    });
  }
})();
