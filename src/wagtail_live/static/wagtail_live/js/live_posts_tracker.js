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
     * @param {Array} newLivePosts - Represents the current live posts on this page.
     * @returns {Array} containing the IDs of the live posts to delete.
     */
    getLivePostsToDelete(newLivePosts) {
        /** A live post has been deleted if it's in currentLivePosts and not in newLivePosts */
        let postsToDelete = [];
        this.currentLivePosts.forEach(post => {
            if (!newLivePosts.includes(post)) {postsToDelete.push(post)};
        });

        return postsToDelete;
    }
}