/**
 * Displays the different render options available for XML files.
 */
RB.XMLRenderOptionsView = Backbone.View.extend({
    template: _.template(dedent`
         <input type="checkbox" id="<%= checkboxId %>"/>
         <label for="<%= checkboxId %>">
          <%- labelText %>
         </label>
    `),

    /**
     * Render the view.
     */
    render() {
        const checkboxId = _.uniqueId('xml-render-on-same-line');

        this._$container = this.template({
            checkboxId: checkboxId,
            labelText: gettext('Render node text on same line')
        });
        this.$el.append(this._$container);

        this._bindCheckboxToModel(checkboxId);
    },

    _bindCheckboxToModel(checkboxId) {
        const attributeName = 'renderTextContentOnSameLine';
        const renderOnSameLineChecked = this.model.get(attributeName);
        const $checkbox = $(`#${checkboxId}`);

        $checkbox
            .prop('checked', renderOnSameLineChecked)
            .on('change', () => {
                this.model.set(
                    attributeName, $checkbox.prop('checked'));
            });
    }
});
