document.addEventListener('DOMContentLoaded', () => {
    const newChannelForm = document.querySelector('#new-channel-form');
    newChannelForm.addEventListener('submit', createChannel);
  
    const deleteChannelBtn = document.querySelectorAll('.delete-btn');
    deleteChannelBtn.forEach((btn) => {
        btn.addEventListener('click', deleteChannel);
    });
});
  
  async function fetchHelper(path, method, body) {
    const fullPath = `/webapp/api/${path}`;
    return await fetch(fullPath, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body,
    });
}
  
async function createChannel(event) {
    // Prevent default form submission
    event.preventDefault();
  
    const form = event.target;
    const newChannelName = form.channel_name.value;
    const regexp = /^[a-zA-Z0-9-_]+$/;
    if (!newChannelName.match(regexp)) {
        const errorMsg = 'Channel names can only contain alphanumeric characters or - and _';
        showNotif(errorMsg, reason = 0);
    
        // Clear out composition fields
        document.querySelector('#channel_name').value = '';
        return;   
    }
  
    // Send a POST request to save channel
    try {
        const payload = JSON.stringify({ channel_name: newChannelName });
        const response = await fetchHelper('channels/', 'POST', payload);
        if (response.status != 201) {
            // Display corresponding error message
            const errorMsg = await response.json();
            showNotif(errorMsg.channel_name[0], reason = 0);
    
            // Clear out composition fields
            document.querySelector('#channel_name').value = '';
            return;
        }
  
        const channel = await response.json();
        showNotif(`Channel ${channel.channel_name} created.`);
    
        const channelDiv = createChannelDiv(channel);
        document.querySelector('ul').insertAdjacentElement('afterbegin', channelDiv);
    
        // Clear out composition fields
        document.querySelector('#channel_name').value = '';
        return;
    
    } catch (error) {
        showNotif(error, reason = 0);
    }     
}
  
async function deleteChannel(event) {
    // Prevent default form submission
    event.preventDefault();
  
    const deleteChannelBtn = event.target;
    const { channel } = deleteChannelBtn.dataset;
  
    // Send a DELETE request to delete channel
    try {
        const response = await fetchHelper(`channels/${channel}/`, 'DELETE');
    
        if (response.status != 204) {
            // Display corresponding error message
            const errorMsg = await response.json();
            showNotif(errorMsg.detail, reason = 0);
            return;
        }
    
        showNotif(`Channel ${channel} deleted.`);
        document.querySelector(`[data-id=${channel}]`).remove();
        return;
  
    } catch (error) {
      showNotif(err, reason = 0);
      return err;
    }
}
  
function constructChannelLink(channelName) {
    const baseURL = `${window.location.protocol}//${window.location.host}/`;
    return `${baseURL}webapp/channels/${channelName}/`;
}
  
function createChannelDiv(channel) {
    const channelName = channel.channel_name;
    const channelLink = constructChannelLink(channelName);
    const channelDiv = document.createElement('li');
    channelDiv.dataset.id = channelName;
    channelDiv.innerHTML = `
        <div>
            <a href=${channelLink}>#${channelName}</a>
            <span class="date">${channel.created}</span>
        </div>
        <div class="btn-group channel-btn">
            <a href=${channelLink}>
                <button class="enter-btn">Go to channel</button>
            </a>
            <button class="delete-btn" data-channel=${channelName}>Delete</button>
        </div>
    `;
    channelDiv.querySelector('.delete-btn').addEventListener('click', deleteChannel);
    return channelDiv;
}
  