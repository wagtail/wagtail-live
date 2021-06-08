/**
 * @classdesc The LivePostsTracker class is a helper to track
 * current live posts appearing in the DOM in order to know which 
 * live posts needs to be deleted.
 */
 class LivePostsTracker {
    /**
     * Creates a new LivePostsTracker.
     * Initializes current live posts to an empty set.
     * @constructor
     */
    constructor() {
        this.currentLivePosts = new Set();
    }

    /**
     * Sets current live posts from a list of live posts.
     * @param {Array} livePosts - New live posts that replaces the previous ones.
     */
    setLivePosts(livePosts) {
        this.currentLivePosts = new Set(livePosts);
    }

    /**
     * Retrieves the live posts to delete.
     * @param {Array} newLivePosts - Represents the current live posts on this page 
     *  (some of which may not appear in the DOM yet).
     * @returns {Array} containing the IDs of the live posts to delete.
     */
    getLivePostsToDelete(newLivePosts) {
        let postsToDelete = [];

        /** A live post has been deleted if it's in currentLivePosts and not in newLivePosts */
        this.currentLivePosts.forEach(post => {
            if (!newLivePosts.includes(post)) {postsToDelete.push(post)};
        });

        /** Set current live posts to new live posts. */
        this.setLivePosts(newLivePosts);

        return postsToDelete;
    }
}

const basePollingURL = `/wagtail_live/get-updates/${channelID}/`;
const SHAKING_INTERVAL = 1000;
let POLLING_INTERVAL;
let lastUpdateReceivedAt;
let livePostsTracker = new LivePostsTracker();


/**
 * Initiates communication with server side.
 * If response status is 200, this function initializes the current live posts, 
 * the polling interval and the timestamp of the last update received then it waits
 * for the duration of the polling interval and calls getUpdates.
 * If response status isn't 200, it waits for the duration of the shaking interval and tries again.
 */
async function shake() {
    let response = await fetch(basePollingURL, {
        headers: {'X-CSRFToken': csrftoken},
        method: 'POST',
    });
    if (response.status != 200) {
        setTimeout(async () => await shake(), SHAKING_INTERVAL);
    } else {
        let [livePosts, lastUpdateTs, pollingInterval] = await response.json();
        livePostsTracker.setLivePosts(livePosts);
        [lastUpdateReceivedAt, POLLING_INTERVAL] = [lastUpdateTs, pollingInterval];
        setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
    }
}

/**
 * Main function which handles getting updates from the server side.
 * @todo Needs better error handling.
 */
async function getUpdates() {
    /** Retrieve timestamp of the last update of this page. */
    let response = await fetchLastUpdateAt();
    if (response.status != 200) {
        setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
    }
    else {
        /** Check if new updates are available. */
        if (newUpdate(response)) {
            /** If yes, try to get those updates. */
            let newResponse = await fetchUpdates();

            if (newResponse.status != 200) {
                setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
            } else {
                let [updates, currentPosts, lastUpdateTS] = await newResponse.json();

                /** Processe new updates */
                for (let i in updates) {process(i, updates[i])};

                /** Retrieve and remove posts to remove. */
                let postsToDelete = livePostsTracker.getLivePostsToDelete(currentPosts);
                postsToDelete.forEach(post => removeLivePost(post));

                /** Update the timestamp of the last update received. */
                lastUpdateReceivedAt = lastUpdateTS["last_update_timestamp"];
                
                setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
            }

        } else {
            /** No updates are available, wait for the polling interval duration and call getUpdates. */
            setTimeout(async () => await getUpdates(), POLLING_INTERVAL)
        };
    }
}

/**
 * Fetches timestamp of the last update for this page.
 * @returns {*} HttpResponse with headers containing the
 *  timestamp of the last update for this page.
 */
async function fetchLastUpdateAt() {
    return await fetch(basePollingURL, {method: 'HEAD'});
}

/**
 * Checks if new updates are available.
 * We know that new updates are available if the timestamp of
 * the last update of the current page is greater than the
 * timestamp of the last update received in the client side.
 * @param {*} response - HttpResponse from HEAD request 
 * @returns {boolean} true if new updates are available, false else.
 */
function newUpdate(response) {
    let tsLastUpdateAt = response.headers.get('Last-Update-At');
    if (parseFloat(tsLastUpdateAt) > parseFloat(lastUpdateReceivedAt)) {
        return true;
    } else {return false;}
}

/**
 * Fetches new updates from the server by sending the timestamp
 * of the last update received in the client side. 
 * Server should respond with new updates, current live posts and 
 * the timestamp of the page's last update.
 * @returns {*} HttpResponse
 */
async function fetchUpdates() {
    let url = basePollingURL + '?' +  new URLSearchParams({last_update_ts: lastUpdateReceivedAt});
    return await fetch(url);
}

/**
 * Retrievs a live post by its ID.
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

/**
 * Removes a live post.
 * @param {string} livePostID - ID of the live post to remove.
 */
function removeLivePost(livePostID) {
    let post = getPostByID(livePostID);
    if (post == null) {
        /** Problematic! */
    } else {post.parentElement.remove()};
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

document.addEventListener('DOMContentLoaded', shake);
module.exports = LivePostsTracker; /** For jest tests. */