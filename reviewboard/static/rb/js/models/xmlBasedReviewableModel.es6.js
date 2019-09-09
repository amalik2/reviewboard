/**
 * Provides review capabilities for XML file attachments.
 *
 * Model Attributes:
 *     renderTextContentOnSameLine (boolean):
 *         Whether or not the text content of nodes in the file should
 *         be rendered on the same line as the opening tag of the node.
 */
RB.XMLBasedReviewable = RB.TextBasedReviewable.extend({
    defaults: _.defaults({
        renderTextContentOnSameLine: false,
    }, RB.TextBasedReviewable.prototype.defaults),

    commentBlockModel: RB.XMLCommentBlock,

    defaultCommentBlockFields: [
        'renderTextContentOnSameLine',
    ].concat(RB.TextBasedReviewable.prototype.defaultCommentBlockFields),
});
