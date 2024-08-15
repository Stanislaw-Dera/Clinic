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

function elementFromHtml(html){
    const temp = document.createElement('temp');

    temp.innerHTML = html.trim();

    return temp.firstElementChild;
}

function animateButtons(callback, grid) {
    const buttons = grid.children;
    for (let button of buttons) {
        button.classList.remove('show');
    }
    setTimeout(() => {
        callback();
    }, 600);
}

// https://stackoverflow.com/questions/13627308/add-st-nd-rd-and-th-ordinal-suffix-to-a-number
function ordinal_suffix_of(i) {
    let j = i % 10,
        k = i % 100;
    if (j === 1 && k !== 11) {
        return i + "st";
    }
    if (j === 2 && k !== 12) {
        return i + "nd";
    }
    if (j === 3 && k !== 13) {
        return i + "rd";
    }
    return i + "th";
}