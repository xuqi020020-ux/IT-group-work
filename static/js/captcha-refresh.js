document.addEventListener('DOMContentLoaded', function() {
  const captchaImg = document.querySelector('img.captcha');

  if (captchaImg) {
    captchaImg.style.cursor = 'pointer';
    captchaImg.title = "Can't see it? Click to refresh the verification code.";

    captchaImg.addEventListener('click', function() {
      fetch('/captcha/refresh/', {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        captchaImg.src = data.image_url;
        document.getElementById('id_captcha_0').value = data.key;
      })
      .catch(error => console.error('Failed to refresh captcha:', error));
    });
  }
});
