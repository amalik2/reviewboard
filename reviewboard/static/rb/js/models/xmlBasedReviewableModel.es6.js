/**
 * Provides XML specific review capabilities for xml file attachments.
 * Additionally, it provides all of the capabilities that normal text file
 * attachments have.
 *
 * Model Attributes:
 *     renderTextOnSameLine (boolean):
 *         Whether or not to render text content on the same line as the start
 *         and close tag for a node
 */
RB.XMLBasedReviewable = RB.TextBasedReviewable.extend({
    defaults: _.defaults({
        renderTextOnSameLine: false
    }, RB.TextBasedReviewable.prototype.defaults)
});
