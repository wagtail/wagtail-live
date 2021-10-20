import bindUploadEvents from "./utils/bind_upload_events";
import { createLivePost, LivePost } from "./utils/live_post";

function checkFormPosition(form) {
    const onLargeDevice = window.innerWidth > 768 ? true : false;
    if (onLargeDevice) {
        if (form.style.height === "0") {
            form.style.opacity = 1;
            form.style.height = "auto";
        }
        return;
    }
    if (window.pageYOffset > 100) {
        form.style.opacity = 0;
        form.style.height = 0;
    } else {
        form.style.opacity = 1;
        form.style.height = "auto";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const newLivePostForm = document.querySelector("#new-message-form");
    const livePostsWrapper = document.getElementById("live-posts");
    if (!newLivePostForm || !livePostsWrapper) {
        return;
    }

    document.addEventListener("scroll", () => {
        checkFormPosition(newLivePostForm);
    });

    const channelName = livePostsWrapper.dataset.channel;
    newLivePostForm.addEventListener("submit", (e) => {
        createLivePost(e, channelName, livePostsWrapper);
    });

    const uploadImageBtn = document.getElementById("uploadFile");
    const uploadImageSelect = document.getElementById("images");
    const uploadCountDiv = document.getElementById("imagesList");
    bindUploadEvents(uploadImageBtn, uploadImageSelect, uploadCountDiv);

    const livePosts = Array.from(livePostsWrapper.children);
    livePosts.forEach((livePost) => {
        const handler = new LivePost(livePost, channelName, livePostsWrapper);
        handler.bindEvents();
    });
});
