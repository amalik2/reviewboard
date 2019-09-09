/*
 * Displays XML-specific render options.
 *
 * This renders the options that allow the user to toggle certain
 * features in the XML rendered view on or off.
 */
RB.XmlRenderOptionsView = Backbone.View.extend({

    template: _.template(dedent`
        <div id="render-same-line-container">
            <input type="checkbox" id="<%= checkboxId %>" />
            <label for="<%= checkboxId %>">
                <%- labelText %>
            </label>
        </div>
    `),

    /**
     * Initialize the commenting selector.
     *
     * Args:
     *     options (object):
     *         Options for initializing the view.
     */
    initialize(options) {
        this.options = options;
    },

    /**
     * Render the selector.
     *
     * Returns:
     *     RB.XmlRenderOptionsView:
     *     This object, for chaining.
     */
    render() {
        const checkboxId = _.uniqueId('render_same_line_check');

        this.$el.append(this.template({
            checkboxId: checkboxId,
            labelText: gettext('Render on same line')
        }));

        this._bindCheckboxToModel(checkboxId);
        return this;
    },

    _bindCheckboxToModel(checkboxId) {
        const attributeName = 'renderTextOnSameLine';
        const renderSameLineChecked = this.model.get(attributeName);
        const $checkbox = $(`#${checkboxId}`);

        $checkbox
            .prop('checked', renderSameLineChecked)
            .on('change', () => {
                this.model.set(attributeName, $checkbox.prop('checked'));
            });
    },

    hide() {
        this.$el.toggle();
    },

    show() {
        this.$el.toggle();
    }
});
