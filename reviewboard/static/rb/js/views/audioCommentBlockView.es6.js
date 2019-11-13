/**
 * Provides details about a region of audio that was commented on.
 *
 * This will show the timestamp of the region. It will also show a tooltip
 * showing comment summaries.
 *
 * This is meant to be used with a AudioCommentBlock model.
 */
RB.AudioCommentBlockView = RB.AbstractCommentBlockView.extend({
    // ignore the click event that gets set in RB.AbstractCommentBlockView
    events: {},

    /**
     * Formats the specified seconds into a timestamp.
     *
     * Args:
     *     seconds (number):
     *         The seconds to format.
     * Returns:
     *     string:
     *     The seconds formatted as a timestamp.
     */
    _formatSecondsToTimestamp(seconds) {
        return moment.utc(seconds * 1000).format('mm:ss.SSS');
    },

    /**
     * Gets the text to render in the comment flag.
     *
     * Returns:
     *     string:
     *     The text to render in the comment flag.
     */
    _getFlagText() {
        const startSeconds = this.model.get('start');
        const endSeconds = this.model.get('end');
        const startTimestamp = this._formatSecondsToTimestamp(startSeconds);
        const endTimestamp = this._formatSecondsToTimestamp(endSeconds);

        return `${startTimestamp} - ${endTimestamp}`;
    },

    /**
     * Render the comment block.
     *
     * Along with the block's rectangle, a floating tooltip will also be
     * created that displays summaries of the comments.
     */
    renderContent() {
        const flagText = this._getFlagText();
        this._$flag = $(`<div class="selection-flag">${flagText}</div>`)
            .appendTo(this.$el);
    },

    /**
     * Position the comment dialog to the side of the flag.
     *
     * Args:
     *     commentDlg (RB.CommentDialogView):
     *         The comment dialog.
     */
    positionCommentDlg(commentDlg) {
        commentDlg.positionBeside(this._$flag, {
            side: 'b',
            fitOnScreen: true
        });
    },

    /**
     * Triggers a click event.
     */
    click() {
        this.trigger('clicked');
    }
});
