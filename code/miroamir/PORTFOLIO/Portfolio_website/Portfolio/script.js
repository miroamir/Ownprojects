// Add this to your script.js file
window.addEventListener('scroll', function () {
  const parallaxSection = document.querySelector('.parallax');
  const scrollPosition = window.pageYOffset;

  parallaxSection.style.backgroundPositionY = -scrollPosition * 0.5 + 'px';
});
