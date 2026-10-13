(function (root, createSpeechHelpers) {
  "use strict";
  const helpers = createSpeechHelpers();
  if (typeof module === "object" && module.exports) {
    module.exports = helpers;
  } else {
    root.PaymentMonitorSpeech = helpers;
  }
})(globalThis, function () {
  "use strict";

  function findKhmerVoice(synthesis) {
    return synthesis.getVoices()
      .find((voice) => /^km([_-]|$)/i.test(voice.lang)) || null;
  }

  function speakKhmerPayment(payment, synthesis, Utterance) {
    if (!payment.announcement) return false;
    const voice = findKhmerVoice(synthesis);
    if (!voice) return false;
    const utterance = new Utterance(payment.announcement);
    utterance.lang = voice.lang;
    utterance.voice = voice;
    synthesis.speak(utterance);
    return true;
  }

  return { findKhmerVoice, speakKhmerPayment };
});
