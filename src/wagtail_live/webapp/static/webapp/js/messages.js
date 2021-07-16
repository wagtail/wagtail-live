document.addEventListener('DOMContentLoaded', () => {
    const newMessageForm = document.querySelector('#new-message-form');
    newMessageForm.addEventListener('submit', createMessage);
  
    const showEditMsgFormBtn = document.querySelectorAll('.show-edit-form');
    showEditMsgFormBtn.forEach((btn) => {
      btn.addEventListener('click', showEditMsgForm);
    });
  
    const deleteMsgBtn = document.querySelectorAll('.delete-message');
    deleteMsgBtn.forEach((btn) => {
      btn.addEventListener('click', deleteMessage);
    });
  
    const deleteImageBtn = document.querySelectorAll('.delete-image');
    deleteImageBtn.forEach((btn) => {
      btn.addEventListener('click', deleteImage);
    });
  });
  
  async function fetchHelper(path, method, body, expectedStatus = 200) {
    const fullPath = `/webapp/api/${path}`;
    const response = await fetch(fullPath, {
      method,
      headers: {
        'X-CSRFToken': csrftoken,
      },
      body,
    });
  
    if (response.status != expectedStatus) {
      // Display corresponding error message
      const errorMsg = await response.json();
      showNotif(errorMsg.detail, reason = 0);
      return { ok: false };
    }
    return { ok: true, response };
  }
  
  function getMessage(messageID) {
    return document.querySelector(`.message[data-id='${messageID}']`);
  }
  
  function getImage(imageID) {
    return document.querySelector(`.image-box[data-id='${imageID}']`);
  }
  
  function showEditMsgForm(event) {
    const showEditFormBtn = event.target;
    const message = getMessage(messageID = showEditFormBtn.dataset.id);
    const editMsgForm = message.querySelector('.edit-form');
  
    // Hide message content
    message.querySelector('.message-content').style.display = 'none';
  
    // Hide edit message button
    showEditFormBtn.style.display = 'none';
  
    // Show edit form
    editMsgForm.style.display = 'block';
  
    editMsgForm.addEventListener('submit', editMessage);
  }
  
  async function editMessage(event) {
    // Prevent default form submission
    event.preventDefault();
  
    const form = event.target;
    const formdata = new FormData(form);
    formdata.append('channel', channelName);
    const pk = form.dataset.id;
  
    try {
      let response = await fetchHelper(path = `messages/${pk}/`, method = 'PUT', body = formdata);
      if (!response.ok) {
        return;
      }
  
      response = response.response;
      showNotif(`Message ${pk} edited.`);
  
      const message = await response.text();
      const messageDiv = createMessageDiv(message);
  
      // Hide edit form
      form.style.display = 'none';
  
      // Replace previous message
      const previousMessageDiv = form.parentElement.parentElement;
      previousMessageDiv.parentElement.replaceChild(messageDiv, previousMessageDiv);
      return;
  
    } catch (error) {
      showNotif(error, reason = 0);
    }
  }
  
  async function deleteMessage(event) {
    // Prevent default form submission
    event.preventDefault();
  
    const deleteMsgBtn = event.target;
    const pk = deleteMsgBtn.dataset.id;
  
    try {
      const response = await fetchHelper(path = `messages/${pk}/`, method = 'DELETE', body = {}, expectedStatus = 204);
      if (!response.ok) {
        return;
      }
      // Remove message
      getMessage(messageID = pk).parentElement.remove();
      showNotif(`Message ${pk} deleted.`);
      return;
  
    } catch (error) {
      showNotif(error, reason = 0);
    }
  }
  
  async function deleteImage(event) {
    // Prevent default form submission
    event.preventDefault();
  
    const deleteImageBtn = event.target;
    const pk = deleteImageBtn.dataset.id;
  
    try {
      const response = await fetchHelper(path = `images/${pk}/`, method = 'DELETE', body = {}, expectedStatus = 204);
      if (!response.ok) {
        return;
      }
      // Remove Image
      getImage(ImageID = pk).remove();
      showNotif(`Image ${pk} deleted.`);
      return;
  
    } catch (error) {
      showNotif(error, reason = 0);
    }
  }
  
  async function createMessage(event) {
    // Prevent default form submission
    event.preventDefault();
  
    const form = event.target;
    const formdata = new FormData(form);
    formdata.append('channel', channelName);
  
    // Send a POST request to save channel
    try {
      let response = await fetchHelper(path = 'messages/', method = 'POST', body = formdata, expectedStatus = 201);
      if (!response.ok) {
        return;
      }
  
      response = response.response;
      const message = await response.text();
  
      // Clear out composition fields
      document.querySelector('#content').value = '';
      document.querySelector('#images').value = '';
  
      showNotif('Message posted.');
  
      const messageDiv = createMessageDiv(message);
      document.querySelector('ul').insertAdjacentElement('afterbegin', messageDiv);
      return;
  
    } catch (error) {
      showNotif(error, reason = 0);
    }
  }
  
  function createMessageDiv(message) {
    const messageDiv = document.createElement('li');
    messageDiv.innerHTML = message;
    messageDiv.querySelector('.delete-message').addEventListener('click', deleteMessage);
    messageDiv.querySelector('.show-edit-form').addEventListener('click', showEditMsgForm);
    deleteImageBtn = messageDiv.querySelectorAll('.delete-image');
    deleteImageBtn.forEach((btn) => {
      btn.addEventListener('click', deleteImage);
    });
    return messageDiv;
  }
  