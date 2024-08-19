document.addEventListener('DOMContentLoaded', () => {
	// profile elements handling

	document.querySelectorAll('.doc-profile-element').forEach(element => {
		element.querySelector('.element-title').addEventListener('click', () => element.classList.toggle('show'))
	})

	document.querySelectorAll('.image-container').forEach(element => {
		element.addEventListener('click', () => element.classList.toggle('click'))
	})

})