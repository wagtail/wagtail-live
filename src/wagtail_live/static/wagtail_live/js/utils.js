/**
 * Retrieves a live post by its ID.
 * @param {str} livePostID - Live post's ID
 * @returns {HTMLElement} corresponding to the live post if it exists, else null.
 */
function getPostByID(livePostID) {
    return document.querySelector(`[data-post-id='${livePostID}']`);
}

/**
 * Processes new updates.
 * Replaces a previous live post if it's been edited or 
 * adds a new live post if it's been created.
 * @param {string} updateID - ID of the live post to update
 * @param {string} value - Value of the new content of this live post.
 */
function process(updateID, value) {
    let postsDiv = document.querySelector("#live-posts");
    let livePost = createLivePostWrapper(value);
    let post = getPostByID(updateID);

    if (post != null) {
        postsDiv.replaceChild(livePost, post.parentElement);
    } else {postsDiv.insertAdjacentElement("afterbegin", livePost);}
}


function process_updates(data) {
    for (let i in data.renders) {process(i, data.renders[i])};
    data.removals.forEach(post => removeLivePost(post));
}

/**
 * Removes a live post.
 * @param {string} livePostID - ID of the live post to remove.
 */
function removeLivePost(livePostID) {
    let post = getPostByID(livePostID);
    if (post != null) {
        post.parentElement.remove();
    } else {return;} /** Apparently it's already gone! */
}

/**
 * Helper to create a live post wrapper.
 * @param {str} value - Content of the live post.
 * @returns {HTMLElement} Live post wrapper div.
 */
function createLivePostWrapper(value) {
    let livePostWrapper = document.createElement("div");
    livePostWrapper.classList.add("live-post-wrapper");
    livePostWrapper.innerHTML = value;
    return livePostWrapper;
}