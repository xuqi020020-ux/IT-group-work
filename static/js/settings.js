document.addEventListener('DOMContentLoaded', function() {
  const ids = document.getElementById('settings-ids').dataset;
  const textSlider = document.getElementById(ids.textSizeId);
  const zoomSlider = document.getElementById(ids.zoomId);
  const brightnessInput = document.getElementById(ids.brightnessId);
  const rootStyle = document.documentElement.style;

  textSlider.addEventListener('input', function(e) {
    document.getElementById('textLabel').innerText = e.target.value + 'px';
    rootStyle.setProperty('--user-text-size', e.target.value + 'px');
  });

  zoomSlider.addEventListener('input', function(e) {
    document.getElementById('zoomLabel').innerText = e.target.value + '%';
    rootStyle.setProperty('--user-zoom', e.target.value + '%');
  });

  document.getElementById('btn-decrease-brightness').addEventListener('click', function() {
    let current = parseInt(brightnessInput.value) || 100;
    if (current > 20) {
      brightnessInput.value = current - 10;
      rootStyle.setProperty('--user-brightness', brightnessInput.value + '%');
    }
  });

  document.getElementById('btn-increase-brightness').addEventListener('click', function() {
    let current = parseInt(brightnessInput.value) || 100;
    if (current < 150) {
      brightnessInput.value = current + 10;
      rootStyle.setProperty('--user-brightness', brightnessInput.value + '%');
    }
  });

  document.getElementById('logout-btn').addEventListener('click', function() {
    document.getElementById('logoutForm').submit();
  });
});
