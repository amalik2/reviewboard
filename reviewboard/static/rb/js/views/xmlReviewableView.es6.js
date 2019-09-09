/**
 * Displays a review UI for XML files.
 */
RB.XMLReviewableView = RB.TextBasedReviewableView.extend({
    className: 'xml-review-ui',

    initialize(options) {
        RB.TextBasedReviewableView.prototype.initialize.call(
            this, options);

        this._$renderOptions = null;
        this._renderOptionsView = null;

        this.model.on('change:renderTextOnSameLine', (e) => {
            // TODO: send a GET request to endpoint
            this._renderOptionsView.hide();
            // TODO: on completion, show the options view again
            this._renderOptionsView.show();
        });
    },

    /**
     * Remove the reviewable from the DOM.
     */
    remove() {
        _super(this).remove.call(this);

        this._renderOptionsView.remove();
    },

    /**
     * Render the view.
     */
    renderContent() {
        RB.TextBasedReviewableView.prototype.renderContent.call(this);

        this._$renderOptions = this.$('#render_options');
        this._renderOptionsView = new RB.XmlRenderOptionsView({
            el: this._$renderOptions,
            model: this.model
        });

        this._renderOptionsView.render();
    }
});
