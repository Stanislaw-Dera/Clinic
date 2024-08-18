document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('#navbar');
    console.log(navbar.offsetHeight);
    const container = document.querySelector('.container');
    container.style.marginTop = `${navbar.offsetHeight + 32}px`;
})

function addScrolledClass(){
  const navbar = document.querySelector('#navbar');
  if (window.scrollY > 0) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
}

document.addEventListener('scroll', addScrolledClass);
document.addEventListener('touchstart', addScrolledClass)