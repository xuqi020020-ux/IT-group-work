document.addEventListener('DOMContentLoaded', function() {
  const ttsBtn = document.getElementById('tts-btn');
  const titleEl = document.getElementById('doc-title-data');
  const docTitle = titleEl ? titleEl.dataset.title : '';
  const docContent = document.getElementById('document-content').innerText;

  let isSpeaking = false;

  ttsBtn.addEventListener('click', function() {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      isSpeaking = false;
      ttsBtn.innerHTML = '🔊 Read Aloud';
      ttsBtn.classList.replace('btn-info', 'btn-outline-info');
      ttsBtn.classList.remove('text-white');
    } else {
      const textToRead = docTitle + "。 \n\n" + docContent;
      const utterance = new SpeechSynthesisUtterance(textToRead);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      utterance.onend = function() {
        isSpeaking = false;
        ttsBtn.innerHTML = '🔊 Read Aloud';
        ttsBtn.classList.replace('btn-info', 'btn-outline-info');
        ttsBtn.classList.remove('text-white');
      };

      window.speechSynthesis.speak(utterance);
      isSpeaking = true;
      ttsBtn.innerHTML = '⏹ Stop Reading';
      ttsBtn.classList.replace('btn-outline-info', 'btn-info');
      ttsBtn.classList.add('text-white');
    }
  });

  window.addEventListener('beforeunload', function() {
    window.speechSynthesis.cancel();
  });
});
