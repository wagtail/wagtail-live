document.addEventListener('DOMContentLoaded', function() {
    let newChannelForm = document.querySelector('#new-channel-form');
    newChannelForm.addEventListener('submit', createChannel);

    let deleteChannelBtn = document.querySelectorAll(".delete-btn");
    deleteChannelBtn.forEach(btn => {
        btn.addEventListener("click", deleteChannel);
    });
});


async function createChannel(event) {
    // Prevent default form submission
    event.preventDefault();
  
    let form = event.target;
    let newChannelName = form["channel_name"].value;
    var regexp = /^[a-zA-Z0-9-_]+$/;
    if (!newChannelName.match(regexp)) {
        let errorMsg = "Channel names can only contain alphanumeric characters or - and _";
        showNotif(errorMsg, reason=0);
        // Clear out composition fields
        document.querySelector('#channel_name').value = '';
        return;
    }

    // Send a POST request to save channel
    try {
        let payload = JSON.stringify({channel_name: newChannelName});
        let response = await fetchHelper('channels/', 'POST', payload); 
        if (response.status != 201) {
            // Display corresponding error message
            let errorMsg = await response.json(); 
            showNotif(errorMsg["channel_name"][0], reason=0);
            // Clear out composition fields
            document.querySelector('#channel_name').value = '';
            return 
        } else {
            let channel = await response.json();
            showNotif(`Dummy channel ${channel["channel_name"]} created.`)
            let channelDiv = createChannelDiv(channel);
            document.querySelector("ul").insertAdjacentElement("afterbegin", channelDiv);
            // Clear out composition fields
            document.querySelector('#channel_name').value = '';
            return
        }
  
    } catch(error) {
        /**
         * @todo Need better error handling.
        */
        err = await response.json(); 
        return err;
    }
}
  

async function deleteChannel(event) {
    // Prevent default form submission
    event.preventDefault();

    let deleteChannelBtn = event.target;
    let channel = deleteChannelBtn.dataset.channel;
    // Send a DELETE request to delete channel
    try {
        let response = await fetchHelper(`channels/${channel}/`, 'DELETE');
    
        if (response.status != 204) {
            // Display corresponding error message
            let errorMsg = await response.json();
            showNotif(errorMsg["detail"], reason=0);
            return  
        } else {
            showNotif(`Dummy channel ${channel} deleted.`)
            document.querySelector(`#${channel}`).remove();
            return
        }

    } catch(error) {
        showNotif(err, reason=0);
        return err;
    }
}


function constructChannelLink(channelName){
    let baseURL = window.location.protocol + "//" + window.location.host + "/";
    return baseURL + "wagtail_live_interface/channels/" + channelName + "/";
}

function createChannelDiv(channel){
    let channelName = channel["channel_name"];
    let channelLink = constructChannelLink(channelName);
    let channelDiv = document.createElement("li");
    channelDiv.setAttribute("id", channelName);
    channelDiv.innerHTML = `
        <div>
            <a href=${channelLink}>#${channelName}</a>
            <span class="date">${channel["created"]}</span>
        </div>
        <div class="btn-group channel-btn">
            <a href=${channelLink}>
                <button class="enter-btn">Go to channel</button>
            </a>
            <button class="delete-btn" data-channel=${channelName}>Delete</button>
        </div>
    `;
    channelDiv.querySelector(".delete-btn").addEventListener("click", deleteChannel);
    return channelDiv;
}
