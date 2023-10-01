// Declare a variable to track whether the onSpeechEnd function has been called
let speechEnded = false;

/**
 * Change the text of the paragraph element with the given text.
 * @param {string} text - The new text for the paragraph element.
 */
function changeParagraphText(text) {
  const paragraph = document.getElementById("speak");
  paragraph.innerText = text;
}

/**
 * Set the recording state of the microphone image.
 * @param {boolean} recording - True if the agent is recording, false otherwise.
 */
function setRecordingState(recording) {
  const microphone = document.querySelector(".agent img");
  if (recording) {
    microphone.classList.add("recording");
  } else {
    microphone.classList.remove("recording");
  }
}

/**
 * Handle the recording process.
 * @param {SpeechRecognition} recognition - The speech recognition instance.
 */
async function handleRecording(recognition) {
  if (!recognition) return;

  // Stop playing the audio if it's still playing
  const audio = document.getElementById("audio");
  audio.pause();

  // Change the paragraph text and cancel any ongoing speech synthesis
  changeParagraphText("Bitte sprechen");
  speechSynthesis.cancel();

  console.log("recording...");

  // Set the recording state for the microphone image
  setRecordingState(true);

  // Reset the speechEnded flag
  speechEnded = false;

  // Start the speech recognition
  recognition.start();
}

/**
 * Initialize the speech recognition instance.
 * @returns {SpeechRecognition} The speech recognition instance.
 */
function initSpeechRecognition() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert(
      "Der Agent unterstützt diesen Browser nicht. Bitte nutzen Sie für ein bestmögliches Erlebnis Chrome."
    );
    return null;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "de-DE";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.continuous = false;

  let silenceTimer;

  recognition.onspeechend = () => onSpeechEnd(recognition);
  recognition.onresult = (event) => onRecognitionResult(event);

  // Add event listeners to manage silence timer
  recognition.onaudiostart = () => {
    clearTimeout(silenceTimer);
  };
  recognition.onaudioend = () => {
    silenceTimer = setTimeout(() => {
      onSpeechEnd(recognition);
    }, 1500);
  };
  recognition.onsoundend = () => {
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => {
      onSpeechEnd(recognition);
    }, 1500);
  };

  return recognition;
}

/**
 * Handle the speech end event.
 * @param {SpeechRecognition} recognition - The speech recognition instance.
 */
function onSpeechEnd(recognition) {
  // Return early if onSpeechEnd has already been called for the current recording
  if (speechEnded) return;

  speechEnded = true;

  console.log("sound end");
  recognition.stop();

  // Set the recording state for the microphone image
  setRecordingState(false);

  changeParagraphText("Bitte warten");
}

/**
 * Handle the recognition result event.
 * @param {SpeechRecognitionEvent} event - The speech recognition event.
 */
async function onRecognitionResult(event) {
  const text = event.results[0][0].transcript;
  console.log("recorded:", text);

  // fetch response from agent
  const response = await fetch("/detect-intent", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: text }),
  });

  const data = await response.json();
  console.log(data.result);

  const audio = document.getElementById("audio");
  audio.src = "/static/output.wav?" + new Date().getTime();
  audio.play();

  setRecordingState(false);
  changeParagraphText("Drücken um zu sprechen");
}

/**
 * Main record function to be called on button click
 */
function record() {
  const recognition = initSpeechRecognition();
  handleRecording(recognition);
}
