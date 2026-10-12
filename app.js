(() => {
  "use strict";

  const translations = {
    en: {
      language: "Language", eyebrow: "PAYMENT MONITOR", heading: "Your payments, spoken in Khmer.",
      subheading: "Private payment monitoring from your own Windows computer.", latestPayment: "Latest payment",
      noPayments: "No payment received yet", speakerStatus: "Speaker", deviceControls: "THIS DEVICE",
      audioControls: "Audio controls", enableAudio: "Enable audio", pauseAnnouncements: "Pause announcements",
      resumeAnnouncements: "Resume announcements", testVoice: "Test Khmer voice", exportCsv: "Export CSV",
      speechSpeed: "Speech speed", volume: "Volume", khmerVoice: "Khmer voice", noKhmerVoice: "No Khmer voice found",
      audioHint: "Audio plays only when this device has an installed Khmer voice, the browser permits speech, and the device is not muted.",
      history: "HISTORY", recentPayments: "Recent payments", allCurrencies: "All", amount: "Amount",
      customer: "Customer", method: "Method", time: "Received", transaction: "Transaction ID",
      waiting: "Waiting for a new payment", waitingHint: "Connect your local listener to show real payment notifications here.",
      noMatchingPayments: "No payments match this currency filter.", connection: "CONNECTION",
      connectListener: "Connect to your listener", connectionHelp: "The Python listener stays on your Windows computer. Enter its private API address and the token from your local .env file.",
      apiAddress: "Listener API address", apiToken: "Private API token", connect: "Connect",
      forgetToken: "Forget saved token", privacyHint: "Your API token is stored only in this browser's local storage. Never share it or commit it to GitHub.",
      footer: "GitHub Pages hosts this static dashboard; your private listener and database stay on your computer.",
      connected: "Connected", disconnected: "Disconnected", connectionError: "Error", audioOff: "Audio is off",
      audioReady: "Khmer voice ready", audioPaused: "Announcements paused", voiceMissing: "No Khmer voice is available on this device.",
      voiceTestOk: "Khmer sample spoken.", voiceTestFailed: "The browser could not speak the Khmer sample.",
      apiFailed: "Could not connect. Check the listener, API address, token, and CORS_ORIGINS setting.",
      apiInsecure: "This HTTPS page cannot use an HTTP listener. Connect through a private HTTPS VPN address.",
      authFailed: "Access denied. Check your private API token.", listenerOffline: "Listener API is reachable, but Telegram is disconnected.",
      httpFailure: "Listener returned HTTP",
      voiceAvailable: "Khmer voice available", voicesAvailable: "Khmer voices available",
      filterCurrencies: "Filter payments by currency",
      paymentAudioStatus: "Payment and audio status",
      home: "DomZzz-Payment Speaker home",
      queueOverflow: "The local speech queue is full; enable audio and resume this device.",
      announcementsQueue: "queued", resetState: "Connection settings cleared. Existing device payment history is unchanged.",
      speakBlocked: "Speech failed. Check your device volume and Khmer voice settings.", emptyToken: "Enter the listener address and private API token."
    },
    km: {
      language: "ភាសា", eyebrow: "តាមដានការទូទាត់", heading: "ស្តាប់ការទូទាត់ជាភាសាខ្មែរ។",
      subheading: "តាមដានការទូទាត់ដោយឯកជនពីកុំព្យូទ័រ Windows របស់អ្នក។", latestPayment: "ការទូទាត់ចុងក្រោយ",
      noPayments: "មិនទាន់មានការទូទាត់ទេ", speakerStatus: "ឧបករណ៍បំពងសំឡេង", deviceControls: "ឧបករណ៍នេះ",
      audioControls: "ការគ្រប់គ្រងសំឡេង", enableAudio: "បើកសំឡេង", pauseAnnouncements: "ផ្អាកការប្រកាស",
      resumeAnnouncements: "បន្តការប្រកាស", testVoice: "សាកល្បងសំឡេងខ្មែរ", exportCsv: "នាំចេញ CSV",
      speechSpeed: "ល្បឿននិយាយ", volume: "កម្រិតសំឡេង", khmerVoice: "សំឡេងខ្មែរ", noKhmerVoice: "រកមិនឃើញសំឡេងខ្មែរ",
      audioHint: "សំឡេងនឹងដំណើរការតែនៅពេលឧបករណ៍នេះមានសំឡេងខ្មែរដែលបានដំឡើង កម្មវិធីរុករកអនុញ្ញាត និងឧបករណ៍មិនបានបិទសំឡេង។",
      history: "ប្រវត្តិ", recentPayments: "ការទូទាត់ថ្មីៗ", allCurrencies: "ទាំងអស់", amount: "ចំនួនទឹកប្រាក់",
      customer: "អតិថិជន", method: "វិធីសាស្ត្រ", time: "ពេលទទួល", transaction: "លេខប្រតិបត្តិការ",
      waiting: "កំពុងរង់ចាំការទូទាត់ថ្មី", waitingHint: "ភ្ជាប់កម្មវិធីស្តាប់ក្នុងម៉ាស៊ីន ដើម្បីបង្ហាញការជូនដំណឹងពិតនៅទីនេះ។",
      noMatchingPayments: "មិនមានការទូទាត់តាមរូបិយប័ណ្ណនេះទេ។", connection: "ការតភ្ជាប់",
      connectListener: "ភ្ជាប់ទៅកម្មវិធីស្តាប់", connectionHelp: "កម្មវិធី Python ដំណើរការលើកុំព្យូទ័រ Windows របស់អ្នក។ បញ្ចូលអាសយដ្ឋាន API ឯកជន និង token ពីឯកសារ .env។",
      apiAddress: "អាសយដ្ឋាន API", apiToken: "Token API ឯកជន", connect: "ភ្ជាប់",
      forgetToken: "លុប token ដែលបានរក្សាទុក", privacyHint: "Token API ត្រូវបានរក្សាទុកតែក្នុង browser នេះប៉ុណ្ណោះ។ កុំចែករំលែក ឬបញ្ចូលវាទៅ GitHub។",
      footer: "GitHub Pages ផ្ទុកផ្ទាំងគ្រប់គ្រងឋិតិវន្តនេះ។ កម្មវិធីស្តាប់ឯកជន និងមូលដ្ឋានទិន្នន័យនៅលើកុំព្យូទ័ររបស់អ្នក។",
      connected: "បានតភ្ជាប់", disconnected: "មិនបានតភ្ជាប់", connectionError: "មានបញ្ហា", audioOff: "បានបិទសំឡេង",
      audioReady: "សំឡេងខ្មែររួចរាល់", audioPaused: "បានផ្អាកការប្រកាស", voiceMissing: "មិនមានសំឡេងខ្មែរនៅលើឧបករណ៍នេះទេ។",
      voiceTestOk: "បាននិយាយប្រយោគសាកល្បងជាខ្មែរ។", voiceTestFailed: "កម្មវិធីរុករកមិនអាចនិយាយប្រយោគខ្មែរបានទេ។",
      apiFailed: "មិនអាចភ្ជាប់បាន។ សូមពិនិត្យកម្មវិធីស្តាប់ អាសយដ្ឋាន API token និង CORS_ORIGINS។",
      apiInsecure: "ទំព័រ HTTPS នេះមិនអាចប្រើកម្មវិធីស្តាប់ HTTP បានទេ។ សូមភ្ជាប់តាម VPN ឯកជន HTTPS។",
      authFailed: "មិនមានសិទ្ធិចូលប្រើទេ។ សូមពិនិត្យ token API ឯកជន។", listenerOffline: "API អាចប្រើបាន ប៉ុន្តែ Telegram មិនបានតភ្ជាប់ទេ។",
      httpFailure: "API បានត្រឡប់កំហុស HTTP",
      voiceAvailable: "មានសំឡេងខ្មែរមួយ", voicesAvailable: "មានសំឡេងខ្មែរច្រើន",
      filterCurrencies: "ត្រងការទូទាត់តាមរូបិយប័ណ្ណ",
      paymentAudioStatus: "ស្ថានភាពការទូទាត់ និងសំឡេង",
      home: "ទំព័រដើម DomZzz-Payment Speaker",
      queueOverflow: "ជួរសំឡេងពេញហើយ។ សូមបើកសំឡេង និងបន្តការប្រកាស។",
      announcementsQueue: "កំពុងរង់ចាំ", resetState: "បានលុបការកំណត់តភ្ជាប់។ ប្រវត្តិទូទាត់លើឧបករណ៍នេះនៅដដែល។",
      speakBlocked: "ការនិយាយមិនដំណើរការទេ។ សូមពិនិត្យកម្រិតសំឡេង និងការកំណត់សំឡេងខ្មែរ។",
      emptyToken: "សូមបញ្ចូលអាសយដ្ឋានកម្មវិធីស្តាប់ និង token API ឯកជន។"
    }
  };

  const $ = (id) => document.getElementById(id);
  const configKey = "domzz-payment-speaker.config.v1";
  const languageKey = "domzz-payment-speaker.language";
  let language = localStorage.getItem(languageKey) || "en";
  let apiUrl = "";
  let apiToken = "";
  let apiAuthorized = false;
  let currentFilter = "ALL";
  let connectionStatus = "offline";
  let audioEnabled = false;
  let paused = false;
  let speaking = false;
  let cursor = null;
  let stateKey = "";
  let storedState = { cursor: null, queue: [], heard: [] };
  let payments = [];
  let khmerVoices = [];
  let pollHandle = null;
  let polling = false;

  const t = (key) => (translations[language] || translations.en)[key] || translations.en[key] || key;
  const setMessage = (element, message, isError = false) => {
    element.textContent = message;
    element.classList.toggle("notice-error", isError);
  };
  const setConnection = (state) => {
    connectionStatus = state;
    const badge = $("connection-badge");
    badge.className = `status-pill status-${state}`;
    $("connection-label").textContent = state === "connected" ? t("connected") : state === "error" ? t("connectionError") : t("disconnected");
  };
  const sortedRecent = () => [...payments].sort((a, b) => b.id - a.id).slice(0, 100);
  const paymentTime = (payment) => {
    const date = new Date(payment.received_at);
    return Number.isNaN(date.getTime()) ? payment.payment_datetime : date.toLocaleString(language === "km" ? "km-KH" : undefined);
  };
  const saveDeviceState = () => {
    storedState.cursor = cursor;
    localStorage.setItem(stateKey, JSON.stringify(storedState));
    $("queue-count").textContent = `${storedState.queue.length} ${t("announcementsQueue")}`;
  };

  function setLanguage(next) {
    language = next === "km" ? "km" : "en";
    localStorage.setItem(languageKey, language);
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      const text = t(element.dataset.i18n);
      if (element.tagName === "OPTION") element.textContent = text;
      else element.textContent = text;
    });
    $("language-select").value = language;
    $("language-select").setAttribute("aria-label", t("language"));
    document.querySelector(".brand").setAttribute("aria-label", t("home"));
    document.querySelector(".summary-grid").setAttribute("aria-label", t("paymentAudioStatus"));
    $("voice-select").setAttribute("aria-label", t("khmerVoice"));
    $("filter-group")?.setAttribute("aria-label", t("filterCurrencies"));
    $("pause-audio").textContent = paused ? t("resumeAnnouncements") : t("pauseAnnouncements");
    $("speaker-label").textContent = paused ? t("audioPaused") : audioEnabled ? t("audioReady") : t("audioOff");
    $("queue-count").textContent = `${storedState.queue.length} ${t("announcementsQueue")}`;
    setConnection(connectionStatus);
    chooseKhmerVoices();
    renderPayments();
  }

  function renderPayments() {
    const visible = sortedRecent().filter((payment) => currentFilter === "ALL" || payment.currency === currentFilter);
    const tbody = $("payments-body");
    tbody.replaceChildren();
    for (const payment of visible) {
      const row = document.createElement("tr");
      const amount = document.createElement("td");
      amount.className = "amount-cell";
      amount.textContent = Number(payment.amount).toLocaleString(undefined, { minimumFractionDigits: payment.currency === "USD" && payment.amount.includes(".") ? 2 : 0, maximumFractionDigits: 2 });
      const currency = document.createElement("span");
      currency.className = "currency-tag";
      currency.textContent = payment.currency;
      amount.append(currency);
      const customer = document.createElement("td");
      customer.textContent = payment.customer_name;
      const method = document.createElement("td");
      method.textContent = payment.bank_name ? `${payment.payment_method} · ${payment.bank_name}` : payment.payment_method;
      const received = document.createElement("td");
      received.textContent = paymentTime(payment);
      const transaction = document.createElement("td");
      transaction.textContent = payment.transaction_id;
      row.append(amount, customer, method, received, transaction);
      tbody.append(row);
    }
    const latest = sortedRecent()[0];
    $("latest-amount").textContent = latest ? `${Number(latest.amount).toLocaleString(undefined, { minimumFractionDigits: latest.currency === "USD" && latest.amount.includes(".") ? 2 : 0, maximumFractionDigits: 2 })} ${latest.currency}` : "—";
    $("latest-caption").textContent = latest ? `${latest.customer_name} · ${paymentTime(latest)}` : t("noPayments");
    $("payments-empty").hidden = payments.length > 0;
    $("payments-table-wrap").hidden = payments.length === 0 || visible.length === 0;
    $("filter-empty").hidden = payments.length === 0 || visible.length > 0;
    $("export-csv").disabled = !apiAuthorized;
  }

  function chooseKhmerVoices() {
    if (!("speechSynthesis" in window)) {
      khmerVoices = [];
      $("voice-select").replaceChildren(new Option(t("noKhmerVoice"), ""));
      $("voice-label").textContent = t("voiceMissing");
      return;
    }
    khmerVoices = window.speechSynthesis.getVoices().filter((voice) => /^km(?:-|$)/i.test(voice.lang));
    const selector = $("voice-select");
    const selected = localStorage.getItem("domzz-payment-speaker.voice") || "";
    selector.replaceChildren();
    if (khmerVoices.length === 0) {
      selector.append(new Option(t("noKhmerVoice"), ""));
      $("voice-label").textContent = t("voiceMissing");
    } else {
      khmerVoices.forEach((voice, index) => selector.append(new Option(`${voice.name} (${voice.lang})`, String(index))));
      selector.value = khmerVoices.some((voice) => voice.lang === selected) ? String(khmerVoices.findIndex((voice) => voice.lang === selected)) : "0";
      $("voice-label").textContent = `${khmerVoices.length} ${t(khmerVoices.length === 1 ? "voiceAvailable" : "voicesAvailable")}`;
    }
  }

  function getSelectedVoice() {
    const index = Number($("voice-select").value);
    return Number.isInteger(index) ? khmerVoices[index] || null : null;
  }

  function speak(text, isPayment = false) {
    return new Promise((resolve, reject) => {
      const voice = getSelectedVoice();
      if (!voice || !("speechSynthesis" in window)) {
        reject(new Error(t("voiceMissing")));
        return;
      }
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = voice;
      utterance.lang = voice.lang;
      utterance.rate = Number($("speech-speed").value);
      utterance.volume = Number($("speech-volume").value) / 100;
      utterance.onend = () => resolve();
      utterance.onerror = (event) => reject(new Error(`${t("speakBlocked")} (${event.error})`));
      if (isPayment) {
        storedState.heard = [...storedState.heard, storedState.queue[0].transaction_id].slice(-1000);
        saveDeviceState();
      }
      window.speechSynthesis.speak(utterance);
    });
  }

  async function pumpSpeechQueue() {
    if (speaking || paused || !audioEnabled || !storedState.queue.length) return;
    speaking = true;
    try {
      while (!paused && audioEnabled && storedState.queue.length) {
        const payment = storedState.queue[0];
        if (!storedState.heard.includes(payment.transaction_id)) {
          try {
            await speak(payment.announcement, true);
          } catch (error) {
            storedState.heard = storedState.heard.filter((id) => id !== payment.transaction_id);
            saveDeviceState();
            audioEnabled = false;
            $("enable-audio").disabled = false;
            $("speaker-label").textContent = t("audioOff");
            setMessage($("audio-message"), error.message, true);
            break;
          }
        }
        storedState.queue.shift();
        saveDeviceState();
      }
    } finally {
      speaking = false;
    }
  }

  function enqueuePayments(incoming) {
    const queued = new Set(storedState.queue.map((payment) => payment.transaction_id));
    let acceptedCursor = cursor;
    for (const payment of incoming) {
      if (storedState.heard.includes(payment.transaction_id) || queued.has(payment.transaction_id)) {
        acceptedCursor = payment.id;
        continue;
      }
      if (storedState.queue.length >= 50) {
        setMessage($("audio-message"), t("queueOverflow"), true);
        break;
      }
      storedState.queue.push(payment);
      queued.add(payment.transaction_id);
      acceptedCursor = payment.id;
    }
    return acceptedCursor;
  }

  function appendPayments(incoming) {
    const known = new Set(payments.map((payment) => payment.transaction_id));
    incoming.forEach((payment) => {
      if (!known.has(payment.transaction_id)) payments.push(payment);
      known.add(payment.transaction_id);
    });
  }

  function currentApiDefault() {
    if (location.protocol !== "file:" && (
      location.protocol === "http:"
      || location.hostname.endsWith(".ts.net")
      || location.hostname === "localhost"
      || location.hostname === "127.0.0.1"
    )) {
      return location.origin;
    }
    return "http://127.0.0.1:8765";
  }

  function appendPaymentsToView(incoming) {
    appendPayments(incoming);
    renderPayments();
  }

  function enqueueAndSave(incoming) {
    const acceptedCursor = enqueuePayments(incoming);
    if (acceptedCursor !== null) cursor = acceptedCursor;
    saveDeviceState();
    void pumpSpeechQueue();
  }

  async function request(path) {
    const response = await fetch(`${apiUrl}${path}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${apiToken}` },
      cache: "no-store",
      mode: "cors"
    });
    if (response.status === 401) throw new Error(t("authFailed"));
    if (!response.ok) throw new Error(`${t("httpFailure")} ${response.status}.`);
    return response;
  }

  async function refresh() {
    if (!apiUrl || !apiToken || polling) return;
    polling = true;
    try {
      const statusResponse = await request("/api/status");
      const status = await statusResponse.json();
      setConnection(status.telegram_connected ? "connected" : "offline");
      if (!status.telegram_connected) setMessage($("connection-message"), t("listenerOffline"), true);
      const query = cursor === null ? "" : `?after_id=${encodeURIComponent(cursor)}&limit=50`;
      const paymentsResponse = await request(`/api/payments${query}`);
      const batch = await paymentsResponse.json();
      if (batch.initial || cursor === null) {
        cursor = batch.cursor;
      } else if (batch.payments.length) {
        appendPaymentsToView(batch.payments);
        enqueueAndSave(batch.payments);
      }
      if (batch.initial) {
        appendPayments(batch.payments);
      }
      saveDeviceState();
      renderPayments();
      $("export-csv").disabled = false;
      apiAuthorized = true;
      $("global-error").hidden = true;
      if (status.telegram_connected) setMessage($("connection-message"), t("privacyHint"));
    } catch (error) {
      apiAuthorized = false;
      $("export-csv").disabled = true;
      setConnection("error");
      setMessage($("connection-message"), error.message === t("authFailed") ? error.message : error.message || t("apiFailed"), true);
      $("global-error").textContent = error.message || t("apiFailed");
      $("global-error").hidden = false;
    } finally {
      polling = false;
    }
  }

  function normalizedApiUrl(value) {
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
      throw new Error("Use a plain HTTP or HTTPS listener base address without credentials, query, or fragment.");
    }
    return url.href.replace(/\/+$/, "");
  }

  function saveConfig(nextUrl, nextToken) {
    const normalizedUrl = normalizedApiUrl(nextUrl);
    if (location.protocol === "https:" && new URL(normalizedUrl).protocol !== "https:") {
      throw new Error(t("apiInsecure"));
    }
    if (apiUrl && apiUrl !== normalizedUrl) {
      payments = [];
      renderPayments();
    }
    apiUrl = normalizedUrl;
    apiToken = nextToken.trim();
    apiAuthorized = false;
    stateKey = `domzz-payment-speaker.device.v1:${apiUrl}`;
    const saved = localStorage.getItem(stateKey);
    const restored = saved ? JSON.parse(saved) : null;
    storedState = restored
      && Array.isArray(restored.queue)
      && Array.isArray(restored.heard)
      && (restored.cursor === null || Number.isSafeInteger(restored.cursor))
      ? restored
      : { cursor: null, queue: [], heard: [] };
    cursor = storedState.cursor === null ? null : Number(storedState.cursor);
    localStorage.setItem(configKey, JSON.stringify({ apiUrl, apiToken }));
    $("api-url").value = apiUrl;
    $("api-token").value = apiToken;
    setMessage($("connection-message"), t("privacyHint"));
    renderPayments();
    void refresh();
    if (pollHandle) clearInterval(pollHandle);
    pollHandle = setInterval(() => void refresh(), 5000);
  }

  $("connection-form").addEventListener("submit", (event) => {
    event.preventDefault();
    try {
      if (!$("api-token").value.trim()) throw new Error(t("emptyToken"));
      saveConfig($("api-url").value.trim(), $("api-token").value);
    } catch (error) {
      setMessage($("connection-message"), error.message, true);
    }
  });
  $("forget-token").addEventListener("click", () => {
    localStorage.removeItem(configKey);
    apiToken = "";
    apiAuthorized = false;
    $("api-token").value = "";
    if (pollHandle) clearInterval(pollHandle);
    pollHandle = null;
    setConnection("offline");
    setMessage($("connection-message"), t("resetState"));
    renderPayments();
  });
  $("language-select").addEventListener("change", (event) => setLanguage(event.target.value));
  $("voice-select").addEventListener("change", () => {
    const voice = getSelectedVoice();
    if (voice) localStorage.setItem("domzz-payment-speaker.voice", voice.lang);
  });
  $("speech-speed").addEventListener("input", (event) => { $("speed-value").value = `${Number(event.target.value).toFixed(1)}×`; });
  $("speech-volume").addEventListener("input", (event) => { $("volume-value").value = `${event.target.value}%`; });
  $("enable-audio").addEventListener("click", async () => {
    chooseKhmerVoices();
    if (!getSelectedVoice()) {
      setMessage($("audio-message"), t("voiceMissing"), true);
      return;
    }
    audioEnabled = true;
    $("speaker-label").textContent = t("audioReady");
    $("enable-audio").disabled = true;
    $("pause-audio").disabled = false;
    try {
      await speak("សំឡេងខ្មែររួចរាល់");
      setMessage($("audio-message"), t("audioHint"));
    } catch (error) {
      audioEnabled = false;
      $("enable-audio").disabled = false;
      $("speaker-label").textContent = t("audioOff");
      setMessage($("audio-message"), error.message || t("voiceTestFailed"), true);
    }
    void pumpSpeechQueue();
  });
  $("pause-audio").addEventListener("click", () => {
    paused = !paused;
    $("pause-audio").textContent = paused ? t("resumeAnnouncements") : t("pauseAnnouncements");
    $("speaker-label").textContent = paused ? t("audioPaused") : audioEnabled ? t("audioReady") : t("audioOff");
    if (paused && "speechSynthesis" in window) window.speechSynthesis.pause();
    else if ("speechSynthesis" in window) window.speechSynthesis.resume();
    void pumpSpeechQueue();
  });
  $("test-voice").addEventListener("click", async () => {
    chooseKhmerVoices();
    try {
      await speak("ទទួលបានប្រាក់ ប្រាំម៉ឺនរៀល");
      setMessage($("audio-message"), t("voiceTestOk"));
    } catch (error) {
      setMessage($("audio-message"), error.message || t("voiceTestFailed"), true);
    }
  });
  $("export-csv").addEventListener("click", async () => {
    try {
      const response = await request("/api/payments.csv");
      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "payment-history.csv";
      link.click();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    } catch (error) {
      setMessage($("connection-message"), error.message, true);
    }
  });
  document.querySelectorAll(".filter-button").forEach((button) => button.addEventListener("click", () => {
    currentFilter = button.dataset.currency;
    document.querySelectorAll(".filter-button").forEach((item) => item.classList.toggle("active", item === button));
    renderPayments();
  }));
  if ("speechSynthesis" in window) window.speechSynthesis.addEventListener("voiceschanged", chooseKhmerVoices);
  chooseKhmerVoices();
  setLanguage(language);
  $("api-url").value = currentApiDefault();
  try {
    const saved = JSON.parse(localStorage.getItem(configKey) || "null");
    if (saved && saved.apiUrl && saved.apiToken) saveConfig(saved.apiUrl, saved.apiToken);
  } catch (error) {
    setMessage($("connection-message"), `Saved connection settings could not be loaded: ${error.message}`, true);
  }
})();
