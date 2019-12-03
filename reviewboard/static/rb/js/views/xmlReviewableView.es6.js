/**
 * Displays a review UI for XML files.
 */
RB.XMLReviewableView = RB.TextBasedReviewableView.extend({
    /**
     * Initialize the view.
     *
     * Args:
     *     options (object):
     *         Options for the view.
     */
    initialize(options) {
        RB.TextBasedReviewableView.prototype.initialize.call(this, options);

        this.model.on('change:renderTextContentOnSameLine', (e) => {
            // TODO: make AJAX request
            // TODO: refresh comments (should be handled automatically by the ajax function)
        });
    },

    shouldRenderCommentBlock(commentBlock) {
        if (commentBlock.get('viewMode') !== this.model.get('viewMode')) {
            return false;
        }

        return commentBlock.get('renderTextContentOnSameLine')
            === this.model.get('renderTextContentOnSameLine');
    },

    renderContent() {
        RB.TextBasedReviewableView.prototype.renderContent.call(this);

        const $renderOptionsContainer = $('.render-options');
        const renderOptionsView = new RB.XMLRenderOptionsView({
            model: this.model,
            el: $renderOptionsContainer
        });

        renderOptionsView.render();
    }
});
