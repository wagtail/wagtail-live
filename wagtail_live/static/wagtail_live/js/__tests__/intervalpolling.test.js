/**
 * @jest-environment jsdom
*/

const LivePostsTracker = require('../intervalpolling');

test('initiliazes tracker to empty set', () => {
    let tracker = new LivePostsTracker();
    expect(tracker.livePosts).toEqual(new Set());
});

test('sets live posts properly', () => {
    let tracker = new LivePostsTracker();
    tracker.setLivePosts(livePosts=[8, 15, 27, 867]);
    expect(tracker.livePosts.size).toEqual(4);
    expect(tracker.livePosts).toContain(27);
    expect(tracker.livePosts).not.toContain(866);
})

test('returns correct posts to delete', () => {
    let tracker = new LivePostsTracker();
    tracker.setLivePosts(livePosts=[1, 2, 3, 4]);

    let newLivePosts = [2, 3, 4, 5, 6];
    let postsToDelete = tracker.getLivePostsToDelete(newLivePosts=newLivePosts);
    expect(postsToDelete).toEqual([1]);
    expect(tracker.livePosts).toEqual(new Set(newLivePosts));

    newLivePosts = [2, 6, 8, 9, 10];
    postsToDelete = tracker.getLivePostsToDelete(newLivePosts);
    expect(postsToDelete).toEqual([3, 4, 5]);
    expect(tracker.livePosts).toEqual(new Set(newLivePosts));

    newLivePosts.push(12, 13);
    postsToDelete = tracker.getLivePostsToDelete(newLivePosts);
    expect(postsToDelete).toEqual([]);
    expect(tracker.livePosts).toEqual(new Set(newLivePosts));

    postsToDelete = tracker.getLivePostsToDelete([]);
    expect(postsToDelete).toEqual([2, 6, 8, 9, 10, 12, 13]);
    expect(tracker.livePosts).toEqual(new Set());
})