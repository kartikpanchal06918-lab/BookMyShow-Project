(() => {
  const root = document.getElementById("bms-assistant");
  if (!root) return;
  const panel = document.getElementById("bms-chat-panel");
  const toggle = document.getElementById("bms-chat-toggle");
  const close = document.getElementById("bms-chat-close");
  const input = document.getElementById("bms-chat-input");
  const send = document.getElementById("bms-send");
  const mic = document.getElementById("bms-mic");
  const messages = document.getElementById("bms-chat-messages");
  const language = document.getElementById("bms-language");
  const speakReplies = document.getElementById("bms-speak-replies");
  const status = document.getElementById("bms-voice-status");
  const chatUrl = root.dataset.chatUrl;
  let recognition = null;

  function openPanel(open) {
    panel.classList.toggle("bms-open", open);
    panel.setAttribute("aria-hidden", String(!open));
    if (open) input.focus();
  }
  toggle.addEventListener("click", () => openPanel(!panel.classList.contains("bms-open")));
  close.addEventListener("click", () => openPanel(false));

  function addText(text, who) {
    const item = document.createElement("div");
    item.className = `bms-message ${who === "user" ? "bms-user" : "bms-bot"}`;
    item.textContent = text;
    messages.appendChild(item);
    messages.scrollTop = messages.scrollHeight;
  }
  function addMovieCards(items) {
    items.forEach(movie => {
      const card = document.createElement("div");
      card.className = "bms-movie-result";
      if (movie.poster) {
        const img = document.createElement("img");
        img.src = movie.poster;
        img.alt = movie.title;
        card.appendChild(img);
      }
      const link = document.createElement("a");
      link.href = movie.url;
      link.textContent = movie.title + (movie.rating ? ` · ★ ${movie.rating}/5` : " · View details");
      card.appendChild(link);
      messages.appendChild(card);
    });
    messages.scrollTop = messages.scrollHeight;
  }
  function speak(text) {
    if (!speakReplies.checked || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = /[\u0900-\u097F]/.test(text) ? "hi-IN" : language.value;
    window.speechSynthesis.speak(utterance);
  }
  function getCookie(name) {
    const part = document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith(name + "="));
    return part ? decodeURIComponent(part.slice(name.length + 1)) : "";
  }
  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;
    addText(message, "user");
    input.value = "";
    send.disabled = true;
    try {
      const response = await fetch(chatUrl, {
        method: "POST",
        headers: {"Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({message})
      });
      const data = await response.json();
      addText(data.reply || "I couldn't process that request.", "bot");
      if (data.movies && data.movies.length) addMovieCards(data.movies);
      speak(data.reply || "");
      if (data.login_url) {
        const link = document.createElement("a");
        link.className = "bms-message bms-bot";
        link.href = data.login_url;
        link.textContent = "Log in";
        messages.appendChild(link);
      }
    } catch (error) {
      addText("I couldn't connect to the server. Please try again.", "bot");
    } finally {
      send.disabled = false;
      messages.scrollTop = messages.scrollHeight;
    }
  }
  send.addEventListener("click", sendMessage);
  input.addEventListener("keydown", event => { if (event.key === "Enter") sendMessage(); });

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onstart = () => { mic.textContent = "⏺"; status.textContent = "Listening… speak now."; };
    recognition.onresult = event => { input.value = event.results[0][0].transcript; status.textContent = "Voice captured. Sending your message…"; sendMessage(); };
    recognition.onerror = event => { status.textContent = event.error === "not-allowed" ? "Please allow microphone access in your browser." : "Voice recognition failed. You can type your message instead."; };
    recognition.onend = () => { mic.textContent = "🎙"; };
    mic.addEventListener("click", () => { recognition.lang = language.value; try { recognition.start(); } catch (error) { status.textContent = "Microphone is already listening."; } });
  } else {
    mic.addEventListener("click", () => { status.textContent = "Voice recognition is not supported in this browser. Please use a recent version of Chrome or Edge."; });
  }
})();