

document.addEventListener('DOMContentLoaded', () => {
	const name = document.querySelector('#name-input');
	const specialization = document.querySelector('#specialization-select');
	const filterButtons = document.querySelector('#filter-buttons');

	// event listener to choose filter button and toggle other ones off

	filterButtons.querySelectorAll('button').forEach((element) => {
		element.addEventListener('click', () => {
			for(const child of filterButtons.children){
				child.classList.remove('active')
			} element.classList.add('active')
		})
	})


	//event listener to show search button
	const searchButton = document.querySelector('#search-button')

	name.addEventListener('keydown', event => searchButton.classList.add('show'))
	specialization.addEventListener('change', event => searchButton.classList.add('show'))

	// actual searching
	searchButton.addEventListener('click', () => {
		try {filter = filterButtons.querySelector('.active').value}
		catch (TypeError){filter = ''}

		const formData = new FormData();

		formData.append('name', name.value);
		formData.append('specialization', specialization.value);
		formData.append('filters', filter);

		fetch('/search/', {
			method: 'POST',
			headers: {'X-CSRFToken': getCookie('csrftoken')},
			body: formData
		})
		.then(response => response.json())
		.then(response => {
			const doctors = document.querySelector('#doctors')
			doctors.innerHTML = ''
			response.forEach((profile) => {
				const element = elementFromHtml(`
					<div class="doctor-profile"> 
					  <div class="doctor-photo"> 
						<img src="../media/${profile.profile_picture}" alt="Doctor Photo">
					  </div>
					  <div class="doctor-details">
						<div class="doctor-description">
						  <h2>${profile.full_name}</h2>
							<p>Specializations: ${profile.specializations}</p>
							<p>Days of Experience: ${profile.experience}</p>
							<p>Lorem ipsum dolor sit amet</p>
						</div>
							<button class="custom-btn purple">View profile</button>
					  </div>
					</div>`)

				// .purple.addeventlistener aby przenieść na profil doktora

				doctors.appendChild(element)
			});
		});
	});
});