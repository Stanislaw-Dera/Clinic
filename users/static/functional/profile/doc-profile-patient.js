document.addEventListener('DOMContentLoaded', () => {
	// profile elements handling

	document.querySelectorAll('.doc-profile-element').forEach(element => {
		element.querySelector('.element-title').addEventListener('click', () => element.classList.toggle('show'));
	});

	document.querySelectorAll('.image-container').forEach(element => {
		element.addEventListener('click', () => element.classList.toggle('click'));
	});

	// booking calendar

	const btn = document.querySelector('.custom-btn');

	if (btn) {
		btn.addEventListener('click', showOverlay);
		document.querySelector('.overlay-close').addEventListener('click', hideOverlay);
	}
});

function fetchBookingCalendar(){
	const docId = window.location.pathname.match(/\d+/)[0];


}

function showOverlay() {
	const overlay = document.querySelector('#booking-calendar');
	overlay.style.display = 'block';
	delay(100).then(() => {
		overlay.classList.add('active')
		fetchBookingCalendar()
	});
}

function hideOverlay() {
	const overlay = document.querySelector('#booking-calendar');
	overlay.classList.remove('active');
	delay(600).then(() => {
		overlay.style.display = 'none';

	});
}