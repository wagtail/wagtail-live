import bindUploadEvents from "./utils/bind_upload_events";
import { createLivePost, LivePost } from "./utils/live_post";

document.addEventListener("DOMContentLoaded", () => {
    const newLivePostForm = document.querySelector("#new-message-form");
    const livePostsWrapper = document.getElementById("live-posts");
    if (!newLivePostForm || !livePostsWrapper) {
        return;
    }

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
