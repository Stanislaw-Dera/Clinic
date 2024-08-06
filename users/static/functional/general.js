//auto-resize textarea (https://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize)
document.addEventListener('DOMContentLoaded', () =>{
    const tx = document.getElementsByTagName("textarea");
    for (let i = 0; i < tx.length; i++) {
      tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:hidden;");
      tx[i].addEventListener("input", OnInput, false);
    }
})

function OnInput() {
    this.style.resize = 'vertical';
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + "px";
    this.style.resize = 'none';
}

//django's function

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}