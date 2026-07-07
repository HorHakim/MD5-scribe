(function () {
  let mediaRecorder = null;
  let chunks = [];
  let stream = null;
  let timerInterval = null;
  let elapsedSeconds = 0;

  const startBtn = document.getElementById("start-btn");
  const stopBtn = document.getElementById("stop-btn");
  const recordingIndicator = document.getElementById("recording-indicator");
  const timerEl = document.getElementById("timer");
  const micError = document.getElementById("mic-error");
  const audioInput = document.getElementById("audio-input");
  const form = document.getElementById("record-form");

  const MIME_CANDIDATES = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/mp4",
  ];

  function pickMimeType() {
    if (typeof MediaRecorder === "undefined" || !MediaRecorder.isTypeSupported) {
      return "";
    }
    return MIME_CANDIDATES.find((type) => MediaRecorder.isTypeSupported(type)) || "";
  }

  function extensionFor(mimeType) {
    if (mimeType.includes("mp4")) return "mp4";
    if (mimeType.includes("ogg")) return "ogg";
    return "webm";
  }

  function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, "0")}`;
  }

  function startTimer() {
    elapsedSeconds = 0;
    timerEl.textContent = formatTime(elapsedSeconds);
    timerInterval = setInterval(() => {
      elapsedSeconds += 1;
      timerEl.textContent = formatTime(elapsedSeconds);
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
  }

  startBtn.addEventListener("click", async () => {
    micError.classList.add("hidden");

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      micError.textContent = "L'enregistrement audio n'est pas supporté par ce navigateur.";
      micError.classList.remove("hidden");
      return;
    }

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      micError.textContent = "Accès au microphone refusé ou indisponible.";
      micError.classList.remove("hidden");
      return;
    }

    const mimeType = pickMimeType();
    mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
    chunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const usedMimeType = mediaRecorder.mimeType || "audio/webm";
      const blob = new Blob(chunks, { type: usedMimeType });
      const extension = extensionFor(usedMimeType);
      const file = new File([blob], `recording.${extension}`, { type: usedMimeType });

      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      audioInput.files = dataTransfer.files;

      form.requestSubmit();

      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    };

    mediaRecorder.start();
    startTimer();
    recordingIndicator.classList.remove("hidden");
    startBtn.disabled = true;
    stopBtn.disabled = false;
  });

  stopBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    stopTimer();
    recordingIndicator.classList.add("hidden");
    stopBtn.disabled = true;
    startBtn.disabled = false;
  });
})();
