let page;
let filters;
document.addEventListener('DOMContentLoaded', () => {
	const filterDoctor = document.querySelector('#filter-doctor')
	const filterDate = document.querySelector('#filter-date')
	const filterStatus = document.querySelector('#filter-status')

	filterDoctor.addEventListener('click', updateDocFilterOption)
	filterDate.addEventListener('click', updateFilterOption)
	filterStatus.addEventListener('click', updateFilterOption)

	const searchButton = document.querySelector('#search-button')

	searchButton.addEventListener('click', () => {
		document.querySelector('.appointments').innerHTML =''
		page = 1;

		filters = {
			date: parseArray(filterDate.dataset.options)[filterDate.dataset.counter],
			status: parseArray(filterStatus.dataset.options)[filterStatus.dataset.counter],
			'doc-id': filterDoctor.dataset.docId,
			page: page
		}

		console.log('filters', filters)

		document.querySelector('.appointments-footer').innerHTML = ''

		fetchNextAppointments(page)

		window.addEventListener('scrollend', loadNextAppointments)
	})
})

function updateDocFilterOption() {
	const options = docOptionsArray(this.dataset.options);
	let counter = parseInt(this.dataset.counter) + 1;

	if (counter > options.length) {
		counter = 0;
	}

	if (counter === 0) {
		this.innerHTML = 'Doctors: all';
		this.dataset.docId = 'all';
	} else if (counter <= options.length) {
		this.innerHTML = `Doctor: ${options[counter - 1][1]}`;
		this.dataset.docId = `${options[counter - 1][0]}`;
	} else {
		throw `Invalid counter. Error in updateDocFilterOption function. (counter: ${counter})`;
	}

	this.dataset.counter = (counter).toString();
}

function updateFilterOption() {
	const options = parseArray(this.dataset.options);
	let counter = parseInt(this.dataset.counter) + 1;

	if (counter >= options.length) {
		counter = 0;
	}

	const name = this.id.match(/filter-(\w+)/)[1]

	if (counter < options.length) {
		this.innerHTML = `${name}: ${options[counter]}`
	} else {
		throw `Invalid counter. Error in updateFilterOption function. (${name}; counter: ${counter})`;
	}

	this.dataset.counter = (counter).toString();
}

function docOptionsArray(str) {
	const regex = /\[\s*(\d+)\s*,\s*'([^']*)'\s*\]/g;

	let matches;
	const docOptions = [];

	while ((matches = regex.exec(str)) !== null) {
		docOptions.push([parseInt(matches[1]), matches[2]]);
	}

	console.log(docOptions);
	return docOptions
}

function parseArray(str) {
	const regex = /'([^']*)'/g;

	let matches;
	const arr = [];

	while ((matches = regex.exec(str)) !== null) {
		arr.push(matches[1]);
	}

	console.log(arr);
	return arr
}

function attachVisitToHistory(data) {
	const container = document.querySelector('.appointments')

	//console.log(data)

	const dateString = data.date_time;

	const [datePart, timePart] = dateString.split('T');
	const [year, month, day] = datePart.split('-');
	const [hours, minutes] = timePart.split(':');
	const formattedMinutes = minutes.slice(0, 2);

	const formattedDate = `${day}.${month}.${year} ${hours}:${formattedMinutes}`;

	const e = elementFromHtml(`
		<div class="appointment">
			<div class="appointment-header">
				<div class="header-element"><p>Date</p><p>${formattedDate}</p></div>
				<div class="header-element"><p>Doctor</p><p>${data.doctor}</p></div>
				<div class="header-element"><p>Visit type</p><p>${data.type}</p></div>
				<div class="header-element"><p>Status</p><p>${data.status}</p></div>
			</div>
			<div class="appointment-body">
				<div class="body-textarea">
					<textarea class="input-field" >Lorem ipsum dolor sit amet</textarea>
				</div>
				<div class="body-buttons">
					<button class="custom-btn purple">Lorem ipsum</button>
					<button class="custom-btn purple">Lorem ipsum</button>
				</div>
			</div>
		</div>
	`)
	container.appendChild(e)
}

function loadNextAppointments() {
	if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
		filters['page'] = parseInt(filters['page']) + 1;
		delay(500).then(fetchNextAppointments)
	}
}

function fetchNextAppointments() {
	console.log('filters', filters)
	fetch('http://localhost:8000/appointments/history-api?' + new URLSearchParams(filters).toString())
	.then(res => {
		if(!res.ok){
			window.removeEventListener('scrollend', loadNextAppointments)
			throw new Error("No more visits to load.")
		}
		return res.json()
	})
	.then(response => {
		if(response.length === 0){throw new Error("No Visits to load with that filters")}
		response.forEach(arrayElement => attachVisitToHistory(arrayElement))
		document.querySelectorAll('.appointment').forEach(e => e.querySelector('.appointment-header').addEventListener('click', () => e.classList.toggle('expanded')))
	})
	.catch((e) => {
		document.querySelector('.appointments-footer').innerHTML = e.message
		console.log("error in fetching history-api:", e);
	})
}