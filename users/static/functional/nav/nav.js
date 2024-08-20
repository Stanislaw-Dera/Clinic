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