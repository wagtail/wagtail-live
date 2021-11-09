import fetchHelper from "./utils/fetch_helper";
import showNotif from "./utils/show_notif";

function constructChannelLink(channelName) {
    const baseURL = `${window.location.protocol}//${window.location.host}/`;
    return `${baseURL}webapp/channels/${channelName}/`;
}

function createChannelDiv(channel) {
    const channelName = channel.channel_name;
    const channelLink = constructChannelLink(channelName);
    const channelDiv = document.createElement("div");
    channelDiv.classList.add("d-flex");
    channelDiv.dataset.id = channelName;

    channelDiv.innerHTML = `
        <li class="list-group-item list-group-item-action">
            <a href="${channelLink}" class="text-decoration-none">
                <div class="d-flex flex-wrap my-1 justify-content-between">
                    <h5 class="mb-1">#${channelName}</h5>
                    <small class="text-muted">Created now</small>
                </div>
                <small class="text-muted">${channel.posts_count} posts</small>
            </a>
        </li>
        <button type="button" class="btn col-2 delete-btn opacity-50" data-channel="${channelName}">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#B83030"><path d="M0 0h24v24H0z" fill="none"/><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
        </button>
    `;

    channelDiv
        .querySelector(".delete-btn")
        .addEventListener("click", deleteChannel);
    return channelDiv;
}

async function createChannel(event) {
    // Prevent default form submission
    event.preventDefault();

    const form = event.target;
    const newChannelName = form.channel_name.value;
    const regexp = /^[a-zA-Z0-9-_]+$/;
    if (!newChannelName.match(regexp)) {
        const errorMsg =
            "Channel names can only contain alphanumeric characters or - and _";
        showNotif(errorMsg, 0);

        // Clear out composition fields
        document.querySelector("#channel_name").value = "";
        return;
    }

    // Send a POST request to save channel
    try {
        const payload = JSON.stringify({ channel_name: newChannelName });
        const result = await fetchHelper("channels/", "POST", payload, 201);
        if (!result.ok) {
            // Clear out composition fields
            document.querySelector("#channel_name").value = "";
            return;
        }

        const channel = await result.response.json();
        showNotif(`Channel ${channel.channel_name} created.`);

        const channelDiv = createChannelDiv(channel);
        document
            .querySelector("ul")
            .insertAdjacentElement("afterbegin", channelDiv);

        // Clear out composition fields
        document.querySelector("#channel_name").value = "";
    } catch (error) {
        showNotif(error, 0);
    }
}

async function deleteChannel(event) {
    // Prevent default form submission
    event.preventDefault();

    const deleteChannelBtn = event.currentTarget;
    const { channel } = deleteChannelBtn.dataset;

    // Send a DELETE request to delete channel
    try {
        const payload = await fetchHelper(
            `channels/${channel}/`,
            "DELETE",
            {},
            204
        );

        if (payload.ok) {
            showNotif(`Channel ${channel} deleted.`);
            document.querySelector(`[data-id=${channel}]`).remove();
        }
    } catch (error) {
        showNotif(error, 0);
        return error;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const newChannelForm = document.querySelector("#new-channel-form");
    if (!newChannelForm) {
        return;
    }
    newChannelForm.addEventListener("submit", createChannel);

    const deleteChannelBtn = document.querySelectorAll(".delete-btn");
    deleteChannelBtn.forEach((btn) => {
        btn.addEventListener("click", deleteChannel);
    });
});
