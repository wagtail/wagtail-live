document.addEventListener('DOMContentLoaded', function() {
    newMessageForm = document.querySelector('#new-message-form');
    newMessageForm.addEventListener('submit', createMessage);

    showEditMsgFormBtn = document.querySelectorAll(".show-edit-msg-form");
    showEditMsgFormBtn.forEach(btn => {
        btn.addEventListener("click", showEditMsgForm);
    });

    deleteMsgBtn = document.querySelectorAll(".delete-message");
    deleteMsgBtn.forEach(btn => {
        btn.addEventListener("click", deleteMessage);
    });
});

function showEditMsgForm(event) {
    let showEditFormBtn = event.target;
    let editMsgForm = showEditFormBtn.parentElement.parentElement.querySelector('.edit-message-form')
    editMsgForm.previousElementSibling.style.display = "none",
    showEditFormBtn.style.display = "none",
    editMsgForm.style.display = "block";

    editMsgForm.addEventListener("submit", editMessage);
};

async function editMessage(event) {
    // Prevent default form submission
    event.preventDefault();
    let form = event.target;
    let pk = form.dataset.id;
    let payload = JSON.stringify({
        channel: document.querySelector("#channel-name").innerText,
        content: form["content"].value,
    })

    try {
        let response = await fetchHelper(`messages/${pk}/`, 'PUT', payload);
    
        if (response.status != 200) {
            // Display corresponding error message
            let errorMsg = await response.json();
            showNotif(errorMsg["detail"], reason=0);
            return  
        } else {
            message = await response.json()
            showNotif(`Message ${pk} edited.`)
            form.style.display = "none";
            form.previousElementSibling.querySelector("p").innerText = message["content"];
            form.previousElementSibling.style.display = "block";
            form.parentElement.nextElementSibling.querySelector(".show-edit-msg-form").style.display = "block";
            return
        }

    } catch(error) {
        showNotif(error, reason=0);
        return
    }
}

async function deleteMessage(event) {
    // Prevent default form submission
    event.preventDefault();

    let deleteMsgBtn = event.target;
    let pk = deleteMsgBtn.dataset.id
    // Send a POST request to save channel
    try {
        let response = await fetchHelper(`messages/${pk}/`, 'DELETE');
    
        if (response.status != 204) {
            // Display corresponding error message
            let errorMsg = await response.json();
            showNotif(errorMsg["detail"], reason=0);
            return  
        } else {
            showNotif(`Message ${pk} deleted.`)
            deleteMsgBtn.parentElement.parentElement.remove();
            return
        }

    } catch(error) {
        showNotif(error, reason=0);
        return
    }
}


async function createMessage(event) {
    // Prevent default form submission
    event.preventDefault();

    let form = event.target;
    let payload = JSON.stringify({
        channel: document.querySelector("#channel-name").innerText,
        content: form["content"].value,
    });

    // Send a POST request to save channel
    try {
        let response = await fetchHelper('messages/', 'POST', payload);
    
        if (response.status != 201) {
            let errorMsg = await response.json(); 
            showNotif(errorMsg, reason=0);
            return  
        } else {
            let message = await response.json();
            // Clear out composition fields
            document.querySelector('#content').value = '';
            showNotif(`Message posted.`)
            let messageDiv = createMessageDiv(message);
            document.querySelector("ul").insertAdjacentElement("afterbegin", messageDiv);
            return
        }

    } catch(error) {
        showNotif(error, reason=0);
        return
    }
}

function createMessageDiv(message){
    let messageContent = message["content"];
    let messageID = message["id"];
    let messageDiv = document.createElement("li");

    messageDiv.innerHTML = `
        <div class="message-content">
            <div>
                <span class="date">${message["created"]}</span>
                <p>${messageContent}</p>
            </div>
            
            <form class="edit-message-form" data-id="${messageID}">
                <textarea name="content" value="${messageContent}">${messageContent}</textarea>
                <button data-id="${messageID}" class="edit-message">Save changes</button>
            </form>
        </div>
        <div class="btn-group">
            <button data-id=${messageID} class="show-edit-msg-form">Edit message</button>
            <button data-id=${messageID} class="delete-message delete-btn">Delete message</button>
        </div>
    `;
    messageDiv.querySelector(".delete-message").addEventListener("click", deleteMessage);
    messageDiv.querySelector(".show-edit-msg-form").addEventListener("click", showEditMsgForm);
    return messageDiv;
}