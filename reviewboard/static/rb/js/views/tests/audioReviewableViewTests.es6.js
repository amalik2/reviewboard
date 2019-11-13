suite('rb/views/AudioReviewableView', function() {
    function getNewCommentBlockView(attachedToEarlierRevision = false) {
        const commentModel = new RB.AudioCommentBlock({
            start: 0.5,
            end: 1.0,
            attachedToEarlierRevision,
            reviewRequest,
            review: new RB.Review()
        });

        return new RB.AudioCommentBlockView({
            model: commentModel
        });
    }

    let reviewRequest;
    let model;
    let view;

    beforeEach(function() {
        reviewRequest = new RB.ReviewRequest({
            reviewURL: '/r/123/',
        });

        model = new RB.AudioReviewable({
            hasRenderedView: true,
            viewMode: 'rendered',
            fileAttachmentID: 456,
            reviewRequest: reviewRequest,
        });

        view = new RB.AudioReviewableView({
            model: model,
        });
    });

    it('Store a comment to add later if its player has not been loaded',
        function() {
            const commentBlockView = getNewCommentBlockView();

            view.trigger('commentBlockViewAdded', commentBlockView);
            expect(view._commentBlocksToAdd.length).toBe(1);
            expect(view._commentBlocksToAdd[0]).toBe(commentBlockView);
        });

    it('Add a comment to its player if it has loaded', function() {
        const playerSpy = jasmine.createSpyObj(
            'laterRevisionPlayer', ['hasLoaded', 'addComment']);
        playerSpy.hasLoaded.and.returnValue(true);
        view.laterRevisionPlayer = playerSpy;

        const commentBlockView = getNewCommentBlockView();
        view.trigger('commentBlockViewAdded', commentBlockView);

        expect(view._commentBlocksToAdd.length).toBe(0);
        expect(playerSpy.addComment).toHaveBeenCalledWith(commentBlockView);
    });

    it('Add all comments stored for a player once it loads', function() {
        const playerSpy = jasmine.createSpyObj(
            'laterRevisionPlayer', ['hasLoaded', 'addComment']);
        playerSpy.hasLoaded.and.returnValue(false);
        view.laterRevisionPlayer = playerSpy;

        const commentBlockView = getNewCommentBlockView();
        view.trigger('commentBlockViewAdded', commentBlockView);
        playerSpy.hasLoaded.and.returnValue(true);
        view._addCommentsToPlayer(playerSpy);

        expect(view._commentBlocksToAdd.length).toBe(0);
        expect(playerSpy.addComment).toHaveBeenCalledWith(commentBlockView);
    });

    it('Should not load comments stored for another player', function() {
        const playerSpy = jasmine.createSpyObj(
            'laterRevisionPlayer', ['hasLoaded', 'addComment']);
        playerSpy.hasLoaded.and.returnValue(false);
        view.laterRevisionPlayer = playerSpy;

        const commentBlockView = getNewCommentBlockView(true);
        view.trigger('commentBlockViewAdded', commentBlockView);
        playerSpy.hasLoaded.and.returnValue(true);
        view._addCommentsToPlayer(playerSpy);

        expect(view._commentBlocksToAdd.length).toBe(1);
    });
});
