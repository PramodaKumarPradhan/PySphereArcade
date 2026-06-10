/**
 * ARIA Voice Assistant — Frontend JavaScript
 * Web Speech API + Socket.IO + REST API integration
 */

'use strict';

// ══════════════════════════════════════════════════════════
// STATE
// ══════════════════════════════════════════════════════════
const STATE = {
  language: 'en',
  isListening: false,
  isSpeaking: false,
  commandCount: 0,
  sessionStart: Date.now(),
  recognition: null,
  socket: null,
  animFrame: null,
  audioCtx: null,
  analyser: null,
  micStream: null,
};

// ══════════════════════════════════════════════════════════
// COMMAND EXAMPLES (rotated in right panel)
// ══════════════════════════════════════════════════════════
const CMD_EXAMPLES = [
  { lang: '🇬🇧 English', text: '"What time is it?"' },
  { lang: '🇮🇳 हिंदी', text: '"समय बताओ"' },
  { lang: '🇲🇾 Melayu', text: '"Pukul berapa sekarang?"' },
  { lang: '🇬🇧 English', text: '"Open Notepad"' },
  { lang: '🇮🇳 हिंदी', text: '"Notepad खोलो"' },
  { lang: '🇲🇾 Melayu', text: '"Buka Notepad"' },
  { lang: '🇬🇧 English', text: '"Search YouTube for lo-fi music"' },
  { lang: '🇮🇳 हिंदी', text: '"आवाज़ बढ़ाओ"' },
  { lang: '🇲🇾 Melayu', text: '"Kuatkan audio"' },
  { lang: '🇬🇧 English', text: '"Take a screenshot"' },
  { lang: '🇮🇳 हिंदी', text: '"मौसम बताओ"' },
  { lang: '🇲🇾 Melayu', text: '"Bagaimana cuaca hari ini?"' },
  { lang: '🇬🇧 English', text: '"Battery status"' },
  { lang: '🇮🇳 हिंदी', text: '"जोक सुनाओ"' },
  { lang: '🇲🇾 Melayu', text: '"Tunjukkan status bateri"' },
  { lang: '🇬🇧 English', text: '"Set timer for 5 minutes"' },
  { lang: '🇮🇳 हिंदी', text: '"WhatsApp खोलो"' },
  { lang: '🇲🇾 Melayu', text: '"Buka WhatsApp"' },
];

// ══════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initSocket();
  initWebSpeech();
  loadQuickCommands();
  loadCommandExamples();
  setupTextInput();
  startSessionTimer();
  startLiveStats();
  fetchStatus();

  // Keyboard shortcut: Ctrl+Space → toggle mic
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.code === 'Space') {
      e.preventDefault();
      toggleListening();
    }
    if (e.key === 'Enter' && document.activeElement === document.getElementById('textInput')) {
      sendTextCommand();
    }
  });
});

// ══════════════════════════════════════════════════════════
// SOCKET.IO
// ══════════════════════════════════════════════════════════
function initSocket() {
  try {
    STATE.socket = io('/', { transports: ['websocket', 'polling'] });

    STATE.socket.on('connect', () => {
      console.log('Connected to ARIA server ✅');
      setStatus('ready', 'Connected to ARIA');
    });

    STATE.socket.on('disconnect', () => {
      console.log('Disconnected from ARIA server');
      setStatus('error', 'Connection lost — retrying...');
    });

    STATE.socket.on('response', (data) => handleCommandResult(data));
    STATE.socket.on('command_result', (data) => handleCommandResult(data));

    STATE.socket.on('notification', (data) => {
      const msg = data[`message_${STATE.language}`] || data.message;
      showToast('🔔 Reminder', msg, 'reminder');
      addMessage('aria', msg);
    });

    STATE.socket.on('status', (data) => {
      if (data.connected) setStatus('ready', 'ARIA is ready');
    });

  } catch (e) {
    console.warn('Socket.IO not available, using HTTP fallback', e);
  }
}

// ══════════════════════════════════════════════════════════
// WEB SPEECH API (Browser STT)
// ══════════════════════════════════════════════════════════
function initWebSpeech() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('Web Speech API not supported in this browser');
    showToast('⚠️ Warning', 'Voice recognition requires Chrome or Edge browser', 'warning');
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;
  const langLocales = { en: 'en-IN', hi: 'hi-IN', ms: 'ms-MY' };
  recognition.lang = langLocales[STATE.language] || 'en-IN';

  recognition.onstart = () => {
    STATE.isListening = true;
    document.body.classList.add('is-listening');
    setMicState('listening');
    setStatus('listen', 'Listening... speak now');
    setAriaState('Listening...');
    startWaveform();
  };

  recognition.onresult = (event) => {
    let interim = '';
    let final = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const t = event.results[i][0].transcript;
      if (event.results[i].isFinal) final += t;
      else interim += t;
    }
    const liveEl = document.getElementById('liveTranscript');
    if (interim) liveEl.textContent = `"${interim}"`;
    if (final) {
      liveEl.textContent = '';
      sendCommand(final.trim());
    }
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    stopListening();
    const msgs = {
      'no-speech': 'No speech detected. Try again!',
      'audio-capture': 'Microphone not found. Check permissions.',
      'not-allowed': 'Microphone access denied. Please allow microphone.',
      'network': 'Network error. Check your internet connection.',
    };
    showToast('🎤 Voice Error', msgs[event.error] || `Error: ${event.error}`, 'error');
    setStatus('error', msgs[event.error] || 'Recognition error');
  };

  recognition.onend = () => {
    if (STATE.isListening) stopListening();
  };

  STATE.recognition = recognition;
}

// ══════════════════════════════════════════════════════════
// LISTENING CONTROL
// ══════════════════════════════════════════════════════════
function toggleListening() {
  if (STATE.isListening) stopListening();
  else startListening();
}

function startListening() {
  if (!STATE.recognition) {
    showToast('⚠️', 'Voice recognition not available. Use text input.', 'warning');
    return;
  }
  try {
    const langLocales = { en: 'en-IN', hi: 'hi-IN', ms: 'ms-MY' };
    STATE.recognition.lang = langLocales[STATE.language] || 'en-IN';
    STATE.recognition.start();
  } catch (e) {
    console.error('Recognition start error:', e);
  }
}

function stopListening() {
  STATE.isListening = false;
  document.body.classList.remove('is-listening');
  setMicState('idle');
  setStatus('ready', 'Click mic to speak');
  stopWaveform();
  document.getElementById('liveTranscript').textContent = '';
  if (STATE.recognition) {
    try { STATE.recognition.stop(); } catch (e) {}
  }
}

// ══════════════════════════════════════════════════════════
// COMMAND DISPATCH
// ══════════════════════════════════════════════════════════
async function sendCommand(text) {
  if (!text.trim()) return;

  stopListening();
  addMessage('user', text);
  setStatus('thinking', 'Processing...');
  setAriaState('Thinking...');
  STATE.commandCount++;
  document.getElementById('statCommands').textContent = STATE.commandCount;

  // Show typing indicator
  const typingId = showTyping();

  try {
    const response = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language: STATE.language })
    });
    const data = await response.json();
    hideTyping(typingId);
    handleCommandResult(data);
  } catch (e) {
    hideTyping(typingId);
    console.error('Command error:', e);
    const errMsg = 'Server not responding. Make sure ARIA server is running.';
    addMessage('aria', errMsg);
    showToast('❌ Error', errMsg, 'error');
    setStatus('error', 'Server error');
  }
}

function handleCommandResult(data) {
  if (!data) return;

  const replyText = data[`response_${STATE.language}`] || data.response;

  if (replyText) {
    addMessage('aria', replyText);
  }

  if (data.action === 'exit') {
    setTimeout(() => {
      showToast('👋', 'ARIA is signing off. Goodbye!', 'success');
    }, 500);
  }

  setStatus('ready', 'Click mic to speak');
  setAriaState(data.success ? 'Ready to help' : 'Could not complete');
  setAriaState('Ready to help');
}

function sendTextCommand() {
  const input = document.getElementById('textInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  sendCommand(text);
}

// ══════════════════════════════════════════════════════════
// LANGUAGE TOGGLE
// ══════════════════════════════════════════════════════════
function setLanguage(lang) {
  STATE.language = lang;
  document.getElementById('langEN').classList.toggle('active', lang === 'en');
  document.getElementById('langHI').classList.toggle('active', lang === 'hi');
  document.getElementById('langMS').classList.toggle('active', lang === 'ms');
  document.getElementById('statLang').textContent = lang.toUpperCase();
  document.getElementById('defaultLang').value = lang;

  if (STATE.recognition) {
    const langLocales = { en: 'en-IN', hi: 'hi-IN', ms: 'ms-MY' };
    STATE.recognition.lang = langLocales[lang] || 'en-IN';
  }

  let placeholder = 'Type command here... atau taip arahan di sini';
  if (lang === 'hi') {
    placeholder = 'हिंदी में बोलें या टाइप करें... Type in Hindi or English';
  } else if (lang === 'ms') {
    placeholder = 'Tulis arahan dalam Bahasa Melayu atau Inggeris...';
  }
  document.getElementById('textInput').placeholder = placeholder;

  let msg = 'Switched to English mode! 🇬🇧';
  if (lang === 'hi') {
    msg = 'हिंदी मोड चालू! अब हिंदी में बोलें। 🇮🇳';
  } else if (lang === 'ms') {
    msg = 'Mod Bahasa Melayu diaktifkan! Sila bercakap sekarang. 🇲🇾';
  }
  addMessage('aria', msg);
}

// ══════════════════════════════════════════════════════════
// CHAT UI
// ══════════════════════════════════════════════════════════
function addMessage(sender, text) {
  const container = document.getElementById('chatMessages');
  const isAria = sender === 'aria';

  const now = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  const msgEl = document.createElement('div');
  msgEl.className = `chat-message ${isAria ? 'aria-msg' : 'user-msg'}`;

  // Format long text (pre-wrap for command output)
  const formattedText = text.replace(/\n/g, '<br/>');

  msgEl.innerHTML = `
    <div class="msg-avatar">${isAria ? '🎙️' : '👤'}</div>
    <div class="msg-bubble">
      <p class="msg-text">${formattedText}</p>
      <span class="msg-time">${now}</span>
    </div>
  `;

  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;

  // If ARIA responding, do browser TTS
  if (isAria && STATE.language) {
    browserSpeak(text);
  }
}

function clearChat() {
  const container = document.getElementById('chatMessages');
  container.innerHTML = `
    <div class="chat-message aria-msg">
      <div class="msg-avatar">🎙️</div>
      <div class="msg-bubble">
        <p class="msg-text">Chat cleared! Ready for your commands. 🎙️</p>
      </div>
    </div>
  `;
  fetch('/api/history', { method: 'DELETE' });
}

function showTyping() {
  const container = document.getElementById('chatMessages');
  const id = 'typing-' + Date.now();
  const el = document.createElement('div');
  el.id = id;
  el.className = 'chat-message aria-msg';
  el.innerHTML = `
    <div class="msg-avatar">🎙️</div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  return id;
}

function hideTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ══════════════════════════════════════════════════════════
// BROWSER TTS (Web Speech Synthesis)
// ══════════════════════════════════════════════════════════
function browserSpeak(text) {
  if (!window.speechSynthesis) return;
  // Cancel ongoing speech
  window.speechSynthesis.cancel();

  // Limit to ~300 chars for TTS
  const spokenText = text.length > 300 ? text.substring(0, 300) + '...' : text;

  const utterance = new SpeechSynthesisUtterance(spokenText);
  utterance.lang = STATE.language === 'hi' ? 'hi-IN' : 'en-IN';
  utterance.rate = 0.95;
  utterance.pitch = 1.05;
  utterance.volume = 0.9;

  // Try to find a matching voice
  const voices = window.speechSynthesis.getVoices();
  const langCode = STATE.language;
  const voice = voices.find(v => v.lang.startsWith(langCode) && v.name.toLowerCase().includes('female'))
              || voices.find(v => v.lang.startsWith(langCode));
  if (voice) utterance.voice = voice;

  utterance.onstart = () => {
    STATE.isSpeaking = true;
    setAriaState('Speaking...');
    setStatus('speaking', 'ARIA is speaking...');
    document.getElementById('avatarRing').style.background =
      'linear-gradient(135deg, #06b6d4, #8b5cf6)';
  };
  utterance.onend = () => {
    STATE.isSpeaking = false;
    setAriaState('Ready to help');
    setStatus('ready', 'Click mic to speak');
    document.getElementById('avatarRing').style.background = '';
  };

  window.speechSynthesis.speak(utterance);
}

// Load voices async
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// ══════════════════════════════════════════════════════════
// MIC WAVEFORM VISUALIZER (Canvas)
// ══════════════════════════════════════════════════════════
function startWaveform() {
  const canvas = document.getElementById('visualizerCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const cx = W / 2;
  const cy = H / 2;
  const r = 55;

  let phase = 0;
  function draw() {
    if (!STATE.isListening) return;
    ctx.clearRect(0, 0, W, H);
    phase += 0.08;

    // Draw animated ring
    const bars = 48;
    for (let i = 0; i < bars; i++) {
      const angle = (i / bars) * Math.PI * 2;
      const amp = 8 + Math.sin(phase + i * 0.3) * 6 + Math.random() * 4;
      const x1 = cx + Math.cos(angle) * r;
      const y1 = cy + Math.sin(angle) * r;
      const x2 = cx + Math.cos(angle) * (r + amp);
      const y2 = cy + Math.sin(angle) * (r + amp);

      const hue = 270 + Math.sin(phase + i * 0.1) * 40;
      ctx.beginPath();
      ctx.strokeStyle = `hsla(${hue}, 80%, 70%, 0.7)`;
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    STATE.animFrame = requestAnimationFrame(draw);
  }
  draw();
}

function stopWaveform() {
  if (STATE.animFrame) {
    cancelAnimationFrame(STATE.animFrame);
    STATE.animFrame = null;
  }
  const canvas = document.getElementById('visualizerCanvas');
  if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
}

// ══════════════════════════════════════════════════════════
// QUICK COMMANDS
// ══════════════════════════════════════════════════════════
async function loadQuickCommands() {
  try {
    const res = await fetch('/api/quick-commands');
    const { commands } = await res.json();
    const grid = document.getElementById('quickGrid');
    grid.innerHTML = '';
    commands.forEach(cmd => {
      const tile = document.createElement('div');
      tile.className = 'quick-tile';
      tile.id = `tile-${cmd.id}`;
      tile.title = cmd.command;
      tile.innerHTML = `
        <span class="tile-icon">${cmd.icon}</span>
        <span class="tile-label">${STATE.language === 'hi' ? cmd.label_hi : cmd.label}</span>
      `;
      tile.onclick = () => sendCommand(cmd.command);
      grid.appendChild(tile);
    });
  } catch (e) {
    console.error('Could not load quick commands:', e);
  }
}

// ══════════════════════════════════════════════════════════
// COMMAND EXAMPLES (right panel rotation)
// ══════════════════════════════════════════════════════════
function loadCommandExamples() {
  const container = document.getElementById('cmdExamples');
  // Show 6 random examples
  const shuffled = [...CMD_EXAMPLES].sort(() => 0.5 - Math.random()).slice(0, 6);
  container.innerHTML = '';
  shuffled.forEach(ex => {
    const el = document.createElement('div');
    el.className = 'cmd-example';
    el.innerHTML = `
      <span class="ex-lang">${ex.lang}</span>
      <span class="ex-text">${ex.text}</span>
    `;
    // Click to execute (strip quotes)
    el.onclick = () => sendCommand(ex.text.replace(/["""]/g, ''));
    container.appendChild(el);
  });

  // Rotate examples every 12s
  setTimeout(loadCommandExamples, 12000);
}

// ══════════════════════════════════════════════════════════
// SETTINGS
// ══════════════════════════════════════════════════════════
function toggleSettings() {
  const card = document.getElementById('settingsCard');
  const isVisible = card.style.display !== 'none';
  card.style.display = isVisible ? 'none' : 'block';
  if (!isVisible) card.style.animation = 'toastIn 0.3s ease';
}

function updateVoiceRate(val) {
  document.getElementById('voiceRateVal').textContent = val;
}

function updateVolume(val) {
  document.getElementById('voiceVolVal').textContent = val + '%';
}

function saveApiKey() {
  const key = document.getElementById('geminiKey').value.trim();
  if (!key) return;
  fetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ai: { gemini_api_key: key } })
  }).then(() => {
    showToast('✅ Saved', 'Gemini API key saved. Restart ARIA to apply.', 'success');
    document.getElementById('geminiKey').value = '';
  });
}

// ══════════════════════════════════════════════════════════
// STATUS HELPERS
// ══════════════════════════════════════════════════════════
function setStatus(type, text) {
  const dot = document.getElementById('statusDot');
  const label = document.getElementById('statusText');
  dot.className = `status-dot ${type}`;
  label.textContent = text;
}

function setMicState(state) {
  const btn = document.getElementById('micBtn');
  const icon = document.getElementById('micIcon');
  if (state === 'listening') {
    btn.classList.add('listening');
    icon.textContent = '⏹️';
  } else {
    btn.classList.remove('listening');
    icon.textContent = '🎙️';
  }
}

function setAriaState(text) {
  document.getElementById('ariaState').textContent = text;
}

// ══════════════════════════════════════════════════════════
// LIVE SYSTEM STATS
// ══════════════════════════════════════════════════════════
async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    if (data.cpu !== undefined)
      document.getElementById('liveCpu').textContent = `${Math.round(data.cpu)}%`;
    if (data.ram !== undefined)
      document.getElementById('liveRam').textContent = `${Math.round(data.ram)}%`;
    if (data.battery !== undefined) {
      const charging = data.charging ? '⚡' : '🔋';
      document.getElementById('liveBattery').textContent = `${charging}${data.battery}%`;
    }
    if (data.ai_enabled !== undefined) {
      const badge = document.getElementById('aiBadge');
      const label = document.getElementById('aiLabel');
      if (data.ai_enabled) {
        badge.style.background = 'rgba(16,185,129,0.1)';
        badge.style.borderColor = 'rgba(16,185,129,0.2)';
        label.textContent = 'AI ✓';
      } else {
        badge.style.background = 'rgba(100,100,100,0.1)';
        label.textContent = 'AI';
      }
    }
  } catch (e) {
    // Server not available yet
  }
}

function startLiveStats() {
  // Update time every second
  setInterval(() => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('liveTime').textContent = timeStr;
  }, 1000);

  // Update system stats every 5s
  setInterval(fetchStatus, 5000);
}

function startSessionTimer() {
  setInterval(() => {
    const elapsed = Math.floor((Date.now() - STATE.sessionStart) / 1000);
    const m = Math.floor(elapsed / 60).toString().padStart(2, '0');
    const s = (elapsed % 60).toString().padStart(2, '0');
    document.getElementById('statSession').textContent = `${m}:${s}`;
  }, 1000);
}

// ══════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════
const TOAST_ICONS = { success: '✅', error: '❌', warning: '⚠️', reminder: '🔔', info: 'ℹ️' };

function showToast(title, message, type = 'info', duration = 5000) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <div class="toast-icon">${TOAST_ICONS[type] || 'ℹ️'}</div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-msg">${message}</div>
    </div>
  `;

  // Color by type
  if (type === 'error') {
    toast.style.borderColor = 'rgba(239,68,68,0.3)';
    toast.style.background = 'rgba(239,68,68,0.1)';
  } else if (type === 'success') {
    toast.style.borderColor = 'rgba(16,185,129,0.3)';
    toast.style.background = 'rgba(16,185,129,0.1)';
  } else if (type === 'reminder') {
    toast.style.borderColor = 'rgba(245,158,11,0.3)';
    toast.style.background = 'rgba(245,158,11,0.1)';
  }

  container.appendChild(toast);

  // Click to dismiss
  toast.addEventListener('click', () => dismissToast(toast));

  setTimeout(() => dismissToast(toast), duration);
}

function dismissToast(toast) {
  toast.classList.add('hide');
  setTimeout(() => toast.remove(), 300);
}

// ══════════════════════════════════════════════════════════
// TEXT INPUT
// ══════════════════════════════════════════════════════════
function setupTextInput() {
  const input = document.getElementById('textInput');
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTextCommand();
    }
  });
}

// ══════════════════════════════════════════════════════════
// WELCOME
// ══════════════════════════════════════════════════════════
window.addEventListener('load', () => {
  setTimeout(() => {
    setStatus('ready', 'ARIA is ready — Ctrl+Space to speak');
    showToast('🎙️ ARIA Ready!',
      'Click the mic or press Ctrl+Space to start. Say "help" for commands!',
      'success', 6000);
  }, 1500);
});
