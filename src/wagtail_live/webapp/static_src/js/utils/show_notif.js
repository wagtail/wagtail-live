const toShow = [];

export default function showNotif(msg, reason = 1) {
    let currentAlert = document.getElementById("current-alert");
    if (currentAlert) {
        toShow.push([msg, reason]);
        return;
    }

    const notifDiv = document.createElement("div");
    notifDiv.id = "current-alert";
    notifDiv.classList.add("alert", "fixed-top");
    notifDiv.style.transition = "all 1s ease 0s";
    notifDiv.setAttribute("role", "alert");
    notifDiv.innerText = msg;
    notifDiv.style.opacity = 0;
    notifDiv.style.height = 0;
    document.body.insertAdjacentElement("afterbegin", notifDiv);

    if (reason == 1) {
        notifDiv.classList.add("alert-success");
    } else {
        notifDiv.classList.add("alert-danger");
    }

    notifDiv.style.height = "auto";
    notifDiv.style.opacity = "1";
    setTimeout(() => {
        notifDiv.style.height = 0;
        notifDiv.style.opacity = 0;
        notifDiv.remove();
        if (toShow.length) {
            showNotif(...toShow.shift());
        }
    }, 1500);
}
