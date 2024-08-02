document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('#navbar')
    console.log(navbar.offsetHeight)
    const container = document.querySelector('.container')
    console.log(container.offsetHeight)
    container.style.marginTop = `${navbar.offsetHeight + 16}px`;
})

document.addEventListener('scroll', () => {
  const navbar = document.querySelector('#navbar');
  if (window.scrollY > 0) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});