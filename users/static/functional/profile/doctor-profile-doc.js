// user profile

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('#profile-picture');
    const profilePicture = document.querySelector('#profile-picture-img');
    const savePicture = document.querySelector('#save-picture')

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                profilePicture.src = e.target.result;
            };
            reader.readAsDataURL(file);

            savePicture.classList.add('visible')
        }
    });

    savePicture.addEventListener('click', (event) =>{
        savePicture.classList.remove('visible')
    })

    const bio = document.querySelector('#biography')
    const saveBio = document.querySelector('#save-changes')

    const startText = bio.value
    console.log(startText)

    bio.addEventListener('input', () => {
        if(bio.value !== startText){
            saveBio.classList.add('visible')
        }else{
            saveBio.classList.remove('visible')
        }
    })

    saveBio.addEventListener('click', (event) => {

        event.preventDefault()

        const csrftoken = getCookie('csrftoken')

        const formData = new FormData();
        formData.append('bio', bio.value)

        fetch('/profile/', {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            console.log(result)
            saveBio.classList.remove('visible')
        })
        .catch((e) => {
            console.log("error:", e)
            alert(`error: ${e}`)
        })
    })

    // availability calendar
    Date.prototype.getWeekOfMonth = function() {
      let firstWeekday = new Date(this.getFullYear(), this.getMonth(), 1).getDay() - 1;
      if (firstWeekday < 0) firstWeekday = 6;
      let offsetDate = this.getDate() + firstWeekday - 1;
      return Math.floor(offsetDate / 7);
    }

    const now = new Date(Date.now())

    console.log(now.getUTCMonth())
    console.log('month:', now.getMonth())

    fetch('http://localhost:8000/calendar?' + new URLSearchParams({
        "doc-id": '3',
        year: now.getUTCFullYear(),
        month: now.getUTCMonth() + 1, // because js months starts at 0
        week: now.getWeekOfMonth()
    }).toString())
    .then(res => res.json())
    .then(response => {
        console.log(response);
        document.querySelector('#availability').innerHTML = `<div id="hours-selection"><div id="button-grid"></div></div>` +  response.week;
    })
    .then(() => {
        document.querySelectorAll(".cal-day").forEach((element) => {
            attachWorkHoursChanging(element);
        })
    })
});

function attachWorkHoursChanging(arg){
    console.log("arg:", arg.dataset)

    arg.addEventListener('click', () => {
        // select hours changing field
        fetch('http://localhost:8000/get-workhours?' + new URLSearchParams({
            "doc-id": '3',
            year: arg.dataset.year,
            month: arg.dataset.month,
            day: arg.dataset.day
        }).toString())
        .then(res => res.json())
        .then(response => {
            let workHoursSelection = document.querySelector("#hours-selection");
            let grid = workHoursSelection.querySelector("#button-grid");

            workHoursSelection.classList.remove("show");
            updateGrid(response, grid);
            workHoursSelection.classList.add('show');
        })
        .catch((e) => {
            console.log("error:", e);
            alert(`error: ${e}`);
        })
    })
}

function updateGrid(response, grid) {
    animateButtons(() => {
        grid.innerHTML = "";

        for (const hour in response.hours) {
            const status = response.hours[hour].status
            const button = elementFromHtml(`<div class="${status}">${hour}</div>`);
            grid.appendChild(button);

            button.addEventListener('click', () => {
                if(button.classList.contains("free")){
                    button.classList.remove('free')
                    button.classList.add('working')

                } else if(button.classList.contains("working")){
                    button.classList.remove('working')
                    button.classList.add('free')

                } else {
                    alert(`You can't unbook patient's visits. `)
                }
            })
        }

        const newButtons = grid.children;
        for (let button of newButtons) {
            setTimeout(() => {
                button.classList.add('show');
            }, 100);
        }
    }, grid);
}