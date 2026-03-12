// Confetti celebrations

function fireConfetti() {
  const duration = 5000;
  const end = Date.now() + duration;
  const colors = ['#7B2FBE', '#FFB400', '#FF4D8D', '#00D4FF', '#28A745'];

  (function frame() {
    confetti({
      particleCount: 4,
      angle: 60,
      spread: 55,
      origin: { x: 0, y: 0.6 },
      colors: colors
    });
    confetti({
      particleCount: 4,
      angle: 120,
      spread: 55,
      origin: { x: 1, y: 0.6 },
      colors: colors
    });

    if (Date.now() < end) {
      requestAnimationFrame(frame);
    }
  })();
}

function fireMiniConfetti() {
  confetti({
    particleCount: 80,
    spread: 100,
    origin: { y: 0.5 },
    colors: ['#7B2FBE', '#FFB400', '#FF4D8D']
  });
}

function fireWinnerConfetti() {
  // Burst from center
  confetti({
    particleCount: 150,
    spread: 120,
    origin: { y: 0.6 },
    colors: ['#FFB400', '#FFD166', '#7B2FBE', '#FF4D8D', '#ffffff']
  });

  setTimeout(() => fireConfetti(), 500);
}

// Auto-fire on results page
window.addEventListener('load', function() {
  const winnerSection = document.getElementById('winner-section');
  if (winnerSection && typeof confetti !== 'undefined') {
    setTimeout(() => fireWinnerConfetti(), 500);
  }
});
