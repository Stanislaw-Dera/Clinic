document.addEventListener('DOMContentLoaded', () => {

  // toggling save button on and off

  const saveButton = document.querySelector('#save-changes')
  let phoneNumChanged = false, emailChanged = false, addressChanged = false, extraInfoChanged = false;

  const phoneNum = document.querySelector('#phone-number')
  const email = document.querySelector('#email')
  const address = document.querySelector('#address')
  const extraInfo = document.querySelector('#extra-info')

  const phoneNumValue = phoneNum.value;
  const emailValue = email.value;
  const addressValue = address.value;
  const extraInfoValue = extraInfo.value;

  phoneNum.addEventListener('input', () => {
    if(phoneNum.value !== phoneNumValue){
        phoneNumChanged = true;
        saveButton.classList.add('visible')
    } else {
        phoneNumChanged = false;

      if(!checkIfChanged(phoneNumChanged, emailChanged, addressChanged, extraInfoChanged)){
          saveButton.classList.remove('visible')
      }
    }
  })

  email.addEventListener('input', () => {
    if(email.value !== emailValue){
        emailChanged = true;
        saveButton.classList.add('visible')
    } else {
        emailChanged = false;

      if(!checkIfChanged(phoneNumChanged, emailChanged, addressChanged, extraInfoChanged)){
          saveButton.classList.remove('visible')
      }
    }
  })

  address.addEventListener('input', () => {
    if(address.value !== addressValue){
        addressChanged = true;
        saveButton.classList.add('visible')
    } else {
        addressChanged = false;

      if(!checkIfChanged(phoneNumChanged, emailChanged, addressChanged, extraInfoChanged)){
          saveButton.classList.remove('visible')
      }
    }
  })

  extraInfo.addEventListener('input', () => {
    if(extraInfo.value !== extraInfoValue){
        extraInfoChanged = true;
        saveButton.classList.add('visible')
    } else {
        extraInfoChanged = false;

        if(!checkIfChanged(phoneNumChanged, emailChanged, addressChanged, extraInfoChanged)){
            saveButton.classList.remove('visible')
        }
    }
  })

  saveButton.addEventListener('click', (event) =>{
    event.preventDefault()

    const csrftoken = getCookie('csrftoken')

    const formData = new FormData();

    phoneNumChanged ? formData.append('phone_number', phoneNum.value): 'foo' ;
    emailChanged ? formData.append('email', email.value): 'foo' ;
    addressChanged ? formData.append('address', address.value): 'foo' ;
    extraInfoChanged ? formData.append('extra_info', extraInfo.value): 'foo' ;


    fetch('/profile/', {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorInfo => Promise.reject(errorInfo));
        }
        return response.json();
    })
    .then(result => {
        console.log("result:", result)
        saveButton.classList.remove('visible')
    })
    .catch((e) => {
        console.log(e.error)
        alert(`error: ${e.error}`) // YOU CAN MAKE IT prettier
    })
  })
})

function checkIfChanged(var1,var2,var3,var4){
  return var1 || var2 || var3 || var4;
}
