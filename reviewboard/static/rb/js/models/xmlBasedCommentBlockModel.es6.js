/**
 * Represents the comments on an element in a XML file attachment.
 *
 * XMLCommentBlock deals with creating and representing comments
 * that exist on a specific element of some content for XML files.
 *
 * Model Attributes:
 *     renderTextContentOnSameLine (boolean):
 *         Whether or not the text content of nodes in the file should
 *         be rendered on the same line as the opening tag of the node.
 *
 * See Also:
 *     :js:class:`RB.TextCommentBlock`:
 *         For the attributes defined on all text comment blocks.
 */
RB.XMLCommentBlock = RB.TextCommentBlock.extend({
    defaults: _.defaults({
        renderTextContentOnSameLine: false,
    }, RB.TextCommentBlock.prototype.defaults),

    serializedFields: ['renderTextContentOnSameLine'].concat(
        RB.TextCommentBlock.prototype.serializedFields),
});
