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
console.log(now)

function fetchBookingCalendar(now) {
	console.log(now)
	fetch('http://localhost:8000/calendar?' + new URLSearchParams({
		"doc-id": docId,
		year: now.getUTCFullYear(),
		month: now.getUTCMonth()+1, // because js months starts at 0
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
		cal.classList.remove('show')
		cal.appendChild(elementFromHtml(response.month))

		document.querySelectorAll('.calendar-nav-image').forEach(element => {
			if(parseInt(element.dataset.month) < 0){
				element.dataset.month = '0';
			}
			const date = new Date(`${element.dataset.year}-${parseInt(element.dataset.month)}-3`); // 3 to ensure month will be utc
			console.log(date)
			element.addEventListener('click', () => {fetchBookingCalendar(date)})
		});
	})
	// attaching event listeners to all buttons to provide booking data
	.then(() => {
		document.querySelector('#calendar').classList.add('show')
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
			bookingContainer.style.height = 0;
			clickedButton = null;
		} else {
			clickedButton = element
			document.querySelector('.booking-container').classList.remove('show')
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
			bookingContainer.innerHTML = `<h2>Doctor doesn't have any available hours that day (${element.dataset.day}.${element.dataset.month}.${element.dataset.year}).</h2>`
			delay(500).then(() => bookingContainer.classList.add('show'))
		} else {
			delay(100).then(() => {
				bookingContainer.style.height = 'auto';
			})
			bookingContainer.innerHTML = `
					<h2>Available workhours on ${element.dataset.day} ${element.dataset.month} ${element.dataset.year}</h2> 
					<div class="button-container">
						<div id="time-selection" class="buttons-wrapper">

						</div>
					</div>
					<h2>Choose a visit type</h2>
					<div class="button-container">
						<div id="category-selection" class="buttons-wrapper">

						</div>
					</div>
					<button class="custom-btn purple booking-button">Book a visit</button>
					<div class="book-error-container"></div>`
			// handling response elements

			const timeWrapper = document.querySelector('#time-selection')
			for (const el of response.bookingHours) {
				const button = elementFromHtml(`<button class="custom-btn gray" data-time="${el}">${el}</button>`)
				timeWrapper.appendChild(button)
				button.addEventListener('click', buttonSelected)
			}
			const catWrapper = document.querySelector('#category-selection')
			for (const el of response.categories) {
				const button = elementFromHtml(`<button class="custom-btn gray" data-category="${el}">${el}</button>`)
				catWrapper.appendChild(button)
				button.addEventListener('click', buttonSelected)
			}
			const book = document.querySelector('.booking-button')
			console.log('book', book)

			book.addEventListener('click', () => {
				const time = timeWrapper.querySelector('.active').dataset.time
				const cat = catWrapper.querySelector('.active').dataset.category
				console.log('cat: ', cat)
				const date = response.date
				const dt = `${date} ${time}`

				const formData = new FormData()
				formData.append('datetime', dt)
				formData.append('category', cat)

				postAppointment(formData)  // actual booking
			})
		} // fix to date showing is needed.
	})
	.then(() => {
		delay(500).then(() => document.querySelector('.booking-container').classList.add('show'));
	})
	.catch(e => {
		console.log("error in function getBookingData:", e);
		alert(`error: ${e}`);
	})
}


function buttonSelected() {
	const buttons = this.parentElement.querySelectorAll('button')
	for (const button of buttons) {
		button.classList.remove('active')
	}
	this.classList.add('active')
}

function postAppointment(formData){
	fetch(`../../appointments/manage/${docId}`, {
		method: 'POST',
		headers: {'X-CSRFToken': getCookie('csrftoken')},
		body: formData
	})
	.then(response => {
		if (!response.ok) {
        	return response.json().then(err => { throw new Error(err.message); });
    	}

		return response.json()
	})
	.then(response => {
		console.log(response)
	})
	.catch(e => {
		console.log("error in function postAppointment:", e.message);
		document.querySelector('.book-error-container').innerHTML = e.message
	})
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