const docId = window.location.pathname.match(/\d+/)[0];

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

	const now = new Date(Date.now())

    fetch('http://localhost:8000/calendar?' + new URLSearchParams({
        "doc-id": docId,
        year: now.getUTCFullYear(),
        month: now.getUTCMonth() + 1, // because js months starts at 0
    }).toString())
    .then(res => res.json())
    .then(response => {
        console.log(response);
		document.querySelector('#calendar').innerHTML = response.month;
    })
    .then(() => {
        document.querySelectorAll(".cal-day").forEach((element) => {
            attachVisitBooking(element);
        })
    })
}

let clickedButton;

function attachVisitBooking(element){
	element.addEventListener('click', () => {
		// select visit booking field
		//let bookingContainer = document.querySelector(".booking-container");
		if (clickedButton === element) {
			//bookingContainer.classList.remove('show');
			//clickedButton = null;
		} else {

			//clickedButton = element

			fetch(`http://localhost:8000/appointments/get-doctor-appointments/${docId}?` + new URLSearchParams({
				year: element.dataset.year,
				month: element.dataset.month,
				day: element.dataset.day,
			}).toString())
			.then(res => res.json())
			.then(response => {
				console.log(response)
			});
		}
	});
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