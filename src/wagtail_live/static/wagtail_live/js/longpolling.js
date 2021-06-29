/**
 * Initiates communication with server side.
 * If response status is 200, this function initializes the current live posts
 * and the timestamp of the last update received then it calls getUpdates.
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
    
    const {livePosts, lastUpdateTimestamp} = await response.json();
    livePostsTracker.setLivePosts(livePosts);
    lastUpdateReceivedAt = lastUpdateTimestamp;

    await getUpdates();
    return;
}

/**
 * Main function which handles getting updates from the server side.
 */
async function getUpdates() {

    let url = basePollingURL + '?' +  new URLSearchParams({last_update_ts: lastUpdateReceivedAt});
    let response = await fetch(url);

    if (response.status != 200) {
        await getUpdates();
        return;
    }

    let result = await response.json();
    if ("timeOutReached" in result) {
        await getUpdates();
        return;
    }

    const {updates, currentPosts, lastUpdateTimestamp} = result;

    /** Process new updates */
    for (let i in updates) {process(i, updates[i])};

    /** Retrieve and remove posts to remove. */
    let postsToDelete = livePostsTracker.getLivePostsToDelete(currentPosts);
    postsToDelete.forEach(post => removeLivePost(post));

    /** Set current live posts to new live posts. */
    livePostsTracker.setLivePosts(currentPosts);

    /** Update the timestamp of the last update received. */
    lastUpdateReceivedAt = lastUpdateTimestamp;
    
    await getUpdates();
}

document.addEventListener('DOMContentLoaded', shake);