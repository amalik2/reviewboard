suite('rb/views/XMLReviewableView', function() {
    const template = dedent`
      <div id="container">
       <div class="text-review-ui-views">
        <ul>
         <li class="active" data-view-mode="rendered">
          <a href="#rendered">Rendered</a>
         </li>
         <li data-view-mode="source"><a href="#source">Source</a></li>
        </ul>
       </div>
       <table class="text-review-ui-rendered-table"></table>
       <table class="text-review-ui-text-table"></table>
      </div>
    `;

    let $container;
    let reviewRequest;
    let model;
    let view;
    let review;

    beforeEach(function() {
        $container = $(template).appendTo($testsScratch);

        reviewRequest = new RB.ReviewRequest({
            reviewURL: '/r/124/',
        });

        review = new RB.Review({});

        model = new RB.XMLBasedReviewable({
            hasRenderedView: true,
            viewMode: 'rendered',
            fileAttachmentID: 456,
            reviewRequest: reviewRequest,
        });

        view = new RB.XMLReviewableView({
            model: model,
            el: $container,
        });

        /*
         * Disable the router so that the page doesn't change the URL on the
         * page while tests run.
         */
        spyOn(window.history, 'pushState');
        spyOn(window.history, 'replaceState');

        /*
         * Bypass all the actual history logic and get to the actual
         * router handler.
         */
        spyOn(Backbone.history, 'matchRoot').and.returnValue(true);
        spyOn(view.router, 'trigger').and.callThrough();
        spyOn(view.router, 'navigate').and.callFake((url, options) => {
            if (!options || options.trigger !== false) {
                Backbone.history.loadUrl(url);
            }
        });
    });

    afterEach(function() {
        $container.remove();

        Backbone.history.stop();
    });

    it('Does not show source mode comments in render mode', function() {
        model.set('viewMode', 'rendered');
        const comment = new RB.XMLCommentBlock({
            viewMode: 'source',
            reviewRequest,
            review
        });

        expect(view.shouldRenderCommentBlock(comment)).toBe(false);
    });

    it('Does not show render mode comments in source mode', function() {
        model.set('viewMode', 'source');
        const comment = new RB.XMLCommentBlock({
            viewMode: 'rendered',
            reviewRequest,
            review
        });

        expect(view.shouldRenderCommentBlock(comment)).toBe(false);
    });

    it('Does not show comments with different render options', function() {
        model.set('viewMode', 'rendered');
        model.set('renderTextContentOnSameLine', false);

        const comment = new RB.XMLCommentBlock({
            viewMode: 'rendered',
            renderTextContentOnSameLine: true,
            reviewRequest,
            review
        });

        expect(view.shouldRenderCommentBlock(comment)).toBe(false);
    });

    it('Shows comments with the current selected render options', function() {
        model.set('viewMode', 'rendered');
        model.set('renderTextContentOnSameLine', true);

        const comment = new RB.XMLCommentBlock({
            viewMode: 'rendered',
            renderTextContentOnSameLine: true,
            reviewRequest,
            review
        });

        expect(view.shouldRenderCommentBlock(comment)).toBe(true);
    });
});
