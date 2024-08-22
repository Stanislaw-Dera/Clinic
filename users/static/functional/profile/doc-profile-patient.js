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
const now = new Date(Date.now());
now.setMonth(now.getMonth()-1);

function fetchBookingCalendar(now) {
	fetch('http://localhost:8000/calendar?' + new URLSearchParams({
		"doc-id": docId,
		year: now.getUTCFullYear(),
		month: now.getUTCMonth() + 2, // because js months starts at 0
	}).toString())
	.then(res => res.json())
	.then(response => {
		console.log(response);
		try {
			document.querySelector('.calendar').remove()
		} catch (TypeError) {
			console.log('cal not removed')
		}
		const cal = document.querySelector('#calendar')
		cal.appendChild(elementFromHtml(response.month))
		cal.classList.add('show')

		document.querySelectorAll('.calendar-nav-image').forEach(element => {
			const date = new Date(`${element.dataset.year}-${parseInt(element.dataset.month)}-1`)
			console.log(date.getMonth())
			element.addEventListener('click', () => {fetchBookingCalendar(date)})
		});
	})
	.then(() => {
		document.querySelectorAll(".cal-day").forEach((element) => {
			attachVisitBooking(element);
		})
	})
	.catch(e => {
		console.log("error:", e);
		alert(`error: ${e}`);
	})
}

let clickedButton;

function attachVisitBooking(element) {
	element.addEventListener('click', () => {
		// select visit booking field
		let bookingContainer = document.querySelector(".booking-container");
		if (clickedButton === element) {
			bookingContainer.classList.remove('show');
			clickedButton = null;
		} else {

			clickedButton = element

			getBookingData(element, bookingContainer)
		}
	});
}

//element must have a dataset containing year, month and day
function getBookingData(element, bookingContainer) {
	fetch(`http://localhost:8000/appointments/get-booking-data/${docId}?` + new URLSearchParams({
		year: element.dataset.year,
		month: element.dataset.month,
		day: element.dataset.day,
	}).toString())
	.then(res => res.json())
	.then(response => {
		console.log(response)
		if (response.bookingHours.length === 0) {
			bookingContainer.innerHTML = `
					<h2>Available workhours on ${element.dataset.day} ${element.dataset.month} ${element.dataset.year}</h2>
					<h2>Doctor doesn't have any available hours that day.</h2>`
		} else {
			bookingContainer.innerHTML = `
					<h2>Available workhours on </h2> 
					<div class="button-container">
						<div id="time-selection" class="buttons-wrapper">

						</div>
					</div>
					<h2>Choose a visit type</h2>
					<div class="button-container">
						<div id="category-selection" class="buttons-wrapper">

						</div>
					</div>
					<button class="custom-btn purple">Book a visit</button>`
		} // fix to date showing is needed.
		// handling response elements
		const timeWrapper = document.querySelector('#time-selection')
		for (const el of response.bookingHours) {
			const button = elementFromHtml(`<button class="custom-btn gray" data-time="${el}">${el}</button>`)
			timeWrapper.appendChild(button)
			button.addEventListener('click', buttonSelected)
		}
		const catWrapper = document.querySelector('#category-selection')
		for (const el of response.categories) {
			const button = elementFromHtml(`<button class="custom-btn gray" data-type="${el}">${el}</button>`)
			catWrapper.appendChild(button)
			button.addEventListener('click', buttonSelected)
		}
		const book = document.querySelector('.purple')
		book.dataset = {'date': response.date}
		book.addEventListener('click', () => {})
		bookingContainer.classList.add('show')
	});
}


function buttonSelected() {
	const buttons = this.parentElement.querySelectorAll('button')
	for (const button of buttons) {
		button.classList.remove('active')
	}
	this.classList.add('active')
}

function showOverlay() {
	const overlay = document.querySelector('#booking-calendar');
	overlay.style.display = 'block';
	delay(100).then(() => {
		overlay.classList.add('active')
		fetchBookingCalendar(now)
	});
}

function hideOverlay() {
	const overlay = document.querySelector('#booking-calendar');
	overlay.classList.remove('active');
	delay(600).then(() => {
		overlay.style.display = 'none';

	});
}