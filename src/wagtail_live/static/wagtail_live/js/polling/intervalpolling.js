let POLLING_INTERVAL;

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
        return;
    } 

    const {livePosts, lastUpdateTimestamp, pollingInterval} = await response.json();
    livePostsTracker.setLivePosts(livePosts);
    [lastUpdateReceivedAt, POLLING_INTERVAL] = [lastUpdateTimestamp, pollingInterval];

    setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
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
        return;
    }
    
    /** Check if new updates are available. */
    if (!newUpdate(response)) {
        /** No updates are available, wait for the polling interval duration and call getUpdates. */
        setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
        return;
    }

    /** If yes, try to get those updates. */
    response = await fetchUpdates();

    if (response.status != 200) {
        setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
        return;
    }

    const {updates, currentPosts, lastUpdateTimestamp} = await response.json();

    /** Process new updates */
    for (let i in updates) {process(i, updates[i])};

    /** Retrieve and remove posts to remove. */
    let postsToDelete = livePostsTracker.getLivePostsToDelete(currentPosts);
    postsToDelete.forEach(post => removeLivePost(post));

    /** Set current live posts to new live posts. */
    livePostsTracker.setLivePosts(currentPosts);

    /** Update the timestamp of the last update received. */
    lastUpdateReceivedAt = lastUpdateTimestamp;
    
    setTimeout(async () => await getUpdates(), POLLING_INTERVAL);
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
    return parseFloat(tsLastUpdateAt) > parseFloat(lastUpdateReceivedAt);
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

document.addEventListener('DOMContentLoaded', shake);