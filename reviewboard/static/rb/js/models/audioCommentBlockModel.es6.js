/**
 * Represents the comments on a region of an audio file.
 *
 * Model Attributes:
 *     start (number):
 *         The start time in seconds of the region being commented upon.
 *
 *     end (number):
 *         The end time in seconds of the region being commented upon.
 *
 *     attachedToEarlierRevision (boolean):
 *         Whether the comment is attached to the first audio revision or not.
 *         If this is false, it is attached to the second revision. This is
 *         for determining which player to attach the region to for in the
 *         diff viewer.
 *
 * See Also:
 *     :js:class:`RB.FileAttachmentCommentBlock`:
 *         For attributes defined on the base model.
 *
 *     :js:class:`RB.AbstractCommentBlock`:
 *         For attributes defined on all comment block models.
 */
RB.AudioCommentBlock = RB.FileAttachmentCommentBlock.extend({
    defaults: _.defaults({
        start: null,
        end: null,
        attachedToEarlierRevision: true
    }, RB.AbstractCommentBlock.prototype.defaults),

    serializedFields: ['start', 'end', 'attachedToEarlierRevision'],

    /**
     * Parse the incoming attributes for the comment block.
     *
     * The fields are stored server-side as strings, so we need to convert
     * them back to floats where appropriate.
     *
     * Args:
     *     fields (object):
     *         The serialized fields for the comment.
     *
     * Returns:
     *     object:
     *     The parsed data.
     */
    parse(fields) {
        fields.start = parseFloat(fields.start) || undefined;
        fields.end = parseFloat(fields.end) || undefined;

        return fields;
    },
});
