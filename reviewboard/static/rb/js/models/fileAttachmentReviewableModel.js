/*
 * Provides generic review capabilities for file attachments.
 */
RB.FileAttachmentReviewable = RB.AbstractReviewable.extend({
    defaults: _.defaults({
        caption: '',
        fileAttachmentID: null
    }, RB.AbstractReviewable.prototype.defaults),

    defaultCommentBlockFields: ['fileAttachmentID'],

    /*
     * Adds comment blocks for the serialized comments passed to the
     * reviewable.
     */
    addCommentBlocks: function(serializedComments) {
        this.createCommentBlock(_.extend({
            fileAttachmentID: this.get('fileAttachmentID'),
            serializedComments: serializedComments || []
        }, this.commentBlockModel.prototype.parse(
            _.pick(serializedComments[0],
                   this.commentBlockModel.prototype.serializedFields))));
    }
});
