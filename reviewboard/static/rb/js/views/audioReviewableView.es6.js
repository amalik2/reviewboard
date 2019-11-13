(function() {

    /**
     * Calculates the time interval to render ticks in the audio waveform
     * graph.
     *
     * Taken from https://github.com/katspaugh/wavesurfer.js/blob/master/example/timeline-notches/main.js#L52
     * Licensed under the BSD-3-Clause license that Wavesurfer.js uses.
     *
     * Args:
     *     pxPerSec (number):
     *         How many pixels are used to render one second of the audio.
     *
     * Returns the time interval in seconds to render ticks at.
     */
    function timeInterval(pxPerSec) {
        if (pxPerSec >= 2500) {
            return 0.01;
        } else if (pxPerSec >= 1000) {
            return 0.025;
        } else if (pxPerSec >= 250) {
            return 0.1;
        } else if (pxPerSec >= 100) {
            return 0.25;
        } else if (pxPerSec >= 25) {
            return 1;
        } else if (pxPerSec * 5 >= 25) {
            return 5;
        } else if (pxPerSec * 15 >= 25) {
            return 15;
        }

        return Math.ceil(0.5 / pxPerSec) * 60;
    }

    /**
     * Displays a review UI for audio files.
     *
     * This supports reviewing individual audio files, and diffs between files.
     *
     * In the case of individual files, the waveform will be displayed,
     * centered, and all existing comments will be shown as regions in the
     * waveform graph. Users can click and drag across part of the audio to
     * leave a comment on that area.
     */
    RB.AudioReviewableView = RB.FileAttachmentReviewableView.extend({
        className: 'audio-review-ui',

        commentBlockView: RB.AudioCommentBlockView,

        captionItemTemplate: _.template([
            '<h1 class="caption">',
            ' <%- caption %>',
            '</h1>',
        ].join('')),

        errorTemplate: _.template([
            '<div class="review-ui-error">',
            ' <div class="rb-icon rb-icon-warning"></div>',
            ' <%- errorStr %>',
            '</div>'
            ].join('')),

        showSpectrogramTemplate: _.template([
            '<div class="spectrogram-checkbox">',
             '<input type="checkbox" id="<%= checkboxId %>" />',
             '<label for="<%= checkboxId %>">',
              '<%- labelText %>',
             '</label>',
            '</div>'
        ].join('')),

        /**
         * Initialize the view.
         */
        initialize() {
            RB.FileAttachmentReviewableView.prototype.initialize.apply(
                this, arguments);

            this._commentBlockViews = [];
            this._commentBlocksToAdd = [];
            this.laterRevisionPlayer = null;
            this.earlierRevisionPlayer = null;

            /*
             * Add any CommentBlockViews to the selection area when they're
             * created.
             */
            this.on('commentBlockViewAdded', commentBlockView => {
                this._commentBlockViews.push(commentBlockView);
                this._renderComment(commentBlockView);

                this.listenTo(
                    commentBlockView, 'removing', () => {
                        this._commentBlockViews =
                            _.without(this._commentBlockViews, commentBlockView);
                        this._commentBlocksToAdd =
                            _.without(this._commentBlocksToAdd, commentBlockView);

                        const player = this._getPlayerForComment(commentBlockView.model);
                        if (player) {
                            player.removeComment(commentBlockView);
                        }
                    });
            });

            this.model.on('change:showSpectrogram', () => {
                if (this.laterRevisionPlayer) {
                    this._updateSpectrogramVisibility(this.laterRevisionPlayer);
                }
                if (this.earlierRevisionPlayer) {
                    this._updateSpectrogramVisibility(this.earlierRevisionPlayer);
                }
            });
        },

        /**
         * Gets the audio player a comment should be added to.
         *
         * Args:
         *     comment (RB.AudioPlayer):
         *         The model for the comment.
         */
        _getPlayerForComment(comment) {
            if (comment.get('attachedToEarlierRevision')) {
                return this.earlierRevisionPlayer;
            }
            return this.laterRevisionPlayer;
        },

        /**
         * Renders the specified comment on its associated player.
         *
         * Args:
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment to render.
         */
        _renderComment(commentBlockView) {
            const player = this._getPlayerForComment(commentBlockView.model);

            if (this._canAddCommentsToPlayer(player)) {
                player.addComment(commentBlockView);
            } else {
                this._commentBlocksToAdd.push(commentBlockView);
            }
        },

        /**
         * Gets whether comments can be added to the specified player or not.
         *
         * Args:
         *     player (Wavesurver.Player):
         *         The player to check.
         * Returns:
         *     boolean:
         *     Whether comments can be added to the player or not.
         */
        _canAddCommentsToPlayer(player) {
            return player && player.hasLoaded();
        },

        /**
         * Updates whether the specified player displays the spectrogram
         * or not.
         *
         * Args:
         *     player (Wavesurver.Player):
         *         The player to update the spectrogram visibility for.
         */
        _updateSpectrogramVisibility(player) {
            if (this.model.get('showSpectrogram')) {
                player.showSpectrogram();
            } else {
                player.hideSpectrogram();
            }
        },

        /**
         * Gets options used to create an audio player.
         *
         * Args:
         *     containerSelector (string):
         *         A CSS selector to a div to render the player inside of.
         * Returns:
         *     object:
         *     Options used to create a new audio player.
         */
        _getPlayerOptions(containerSelector) {
            return {
                container: containerSelector,
                waveColor: 'violet',
                progressColor: 'purple',
                loaderColor: 'purple',
                cursorColor: 'navy',
                plugins: [
                    WaveSurfer.spectrogram.create({
                        container: containerSelector + '-spectrogram',
                        labels: true,
                        colorMap: RB.AudioSpectrogramHotmap
                    }),
                    WaveSurfer.timeline.create({
                        container: containerSelector + '-timeline',
                        timeInterval: timeInterval,
                    }),
                    WaveSurfer.regions.create({
                        regions: [],
                        dragSelection: {
                            slop: 5
                        }
                    })
                ],
                minPxPerSec: 100,
                scrollParent: true,
            };
        },

        /**
         * Gets options used to create an audio player.
         *
         * Args:
         *     containerSelector (string):
         *         A CSS selector to a div to render the player inside of.
         *     fileURL (string):
         *         The URL associated with an audio file.
         * Returns:
         *     Wavesurfer.Player:
         *     A newly created audio player.
         */
        _createAudioPlayer(containerSelector, fileURL) {
            const player = new RB.AudioPlayerView({
                el: $(`.${this.className}`),
                playerOptions: this._getPlayerOptions(`.${containerSelector}`),
                containerSelector,
                model: new RB.AudioPlayer({
                    audioURL: fileURL
                })
            });

            player.render();
            this._updateSpectrogramVisibility(player);
            player.on('fileLoaded', () => {
                this._addCommentsToPlayer(player);
            });
            return player;
        },

        /**
         * Adds all comments associated with the specified player to it.
         *
         * Args:
         *     player (Wavesurver.Player):
         *         The player to add comments to.
         */
        _addCommentsToPlayer(player) {
            const blocksToAdd = this._commentBlocksToAdd.filter((comment) => {
                const playerForComment = this._getPlayerForComment(
                    comment.model);
                return playerForComment === player;
            });

            blocksToAdd.forEach(this._renderComment.bind(this));
            this._commentBlocksToAdd =
                _.filter(this._commentBlocksToAdd, (comment) => {
                    return blocksToAdd.indexOf(comment) === -1;
                });
        },

        /**
         * Creates and initializes an audio player for either:
         *      The later revision of the file if this is a diff.
         *      The file if this is not a diff.
         */
        _createAudioPlayerForOriginalFile() {
            const audioURL = this.model.get('audioURL');
            this.laterRevisionPlayer = this._createAudioPlayer(
                'original-file-container', audioURL);

            this.laterRevisionPlayer.on('regionCreated', (region) => {
                region.attachedToEarlierRevision = false;
                this.createAndEditCommentBlock(region);
            });
        },

        /**
         * Creates and initializes an audio player for the earlier revision
         * of the current file.
         *
         * This should only be called when viewing diffs.
         */
        _createAudioPlayerForDiffFile() {
            const earlierRevisionPlayerURL = this.model.get(
                'diffAgainstAudioURL');
            this.earlierRevisionPlayer = this._createAudioPlayer(
                'diff-file-container', earlierRevisionPlayerURL);

            this.earlierRevisionPlayer.on('regionCreated', (region) => {
                region.attachedToEarlierRevision = true;
                this.createAndEditCommentBlock(region);
            });
        },

        /**
         * Render the view.
         *
         * This will set up an audio player interface for the base file, and
         * for the diff file as well if one is selected.
         */
        renderContent() {
            const hasDiff = !!this.model.get('diffAgainstFileAttachmentID');

            if (this.model.get('diffTypeMismatch')) {
                this.$el.append(this.errorTemplate({
                    errorStr: gettext('These revisions cannot be compared because they are different file types.')
                }));
            } else if (hasDiff) {
                this._createAudioPlayerForDiffFile();
                this._createAudioPlayerForOriginalFile();
            } else {
                this._createAudioPlayerForOriginalFile();
            }

            const $header = $('<div />')
                .addClass('review-ui-header')
                .prependTo(this.$el);

            if (this.model.get('numRevisions') > 1) {
                const $revisionLabel = $('<div id="revision_label" />')
                    .appendTo($header);
                this._revisionLabelView = new RB.FileAttachmentRevisionLabelView({
                    el: $revisionLabel,
                    model: this.model
                });
                this._revisionLabelView.render();
                this.listenTo(this._revisionLabelView, 'revisionSelected',
                              this._onRevisionSelected);

                const $revisionSelector = $('<div id="attachment_revision_selector" />')
                    .appendTo($header);
                this._revisionSelectorView = new RB.FileAttachmentRevisionSelectorView({
                    el: $revisionSelector,
                    model: this.model
                });
                this._revisionSelectorView.render();
                this.listenTo(this._revisionSelectorView, 'revisionSelected',
                              this._onRevisionSelected);

                if (!this.renderedInline) {
                    this._renderSpectrogramCheckbox($header);
                    if (hasDiff) {
                        const diffCaption = this.captionItemTemplate({
                            caption: interpolate(
                                gettext('%(caption)s (revision %(revision)s)'),
                                {
                                    caption: this.model.get('diffCaption'),
                                    revision: this.model.get('diffRevision')
                                },
                                true)
                        });
                        const caption = this.captionItemTemplate({
                            caption: interpolate(
                                gettext('%(caption)s (revision %(revision)s)'),
                                {
                                    caption: this.model.get('caption'),
                                    revision: this.model.get('fileRevision')
                                },
                                true)
                        });

                        const $audioPlayers = $('.audio-player-container');
                        $(diffCaption).insertBefore($audioPlayers[0]);
                        $(caption).insertBefore($audioPlayers[1]);
                    } else {
                        const $captionBar = $('<div>')
                            .appendTo($header);

                        $('<h1 class="caption" />')
                            .text(interpolate(
                                gettext('%(caption)s (revision %(revision)s)'),
                                {
                                    caption: this.model.get('caption'),
                                    revision: this.model.get('fileRevision')
                                },
                                true))
                            .appendTo($captionBar);
                    }
                }
            } else {
                if (!this.renderedInline) {
                    this._renderSpectrogramCheckbox($header);
                    $('<h1 class="caption" />')
                        .text(this.model.get('caption'))
                        .appendTo($header);
                }
            }
        },

        /**
         * Renders the checkbox used to toggle the spectrogram visibility
         * status.
         *
         * Args:
         *     $header (JQuery):
         *         The review UI header element.
         */
        _renderSpectrogramCheckbox($header) {
            const spectrogramCheckboxId = 'show-spectrogram-checkbox';
            const $spectrogramCheckboxWrapper = this.showSpectrogramTemplate({
                checkboxId: spectrogramCheckboxId,
                labelText: gettext('Show spectrogram')
            });
            $header.append($spectrogramCheckboxWrapper);

            this._bindSpectrogramCheckboxToModel(`#${spectrogramCheckboxId}`);
        },

        /**
         * Binds the checkbox used to toggle the spectrogram visibility
         * status to the review UI's model.
         *
         * Args:
         *     checkboxSelector (string):
         *         A CSS selector used to find the checkbox in the DOM.
         */
        _bindSpectrogramCheckboxToModel(checkboxSelector) {
            const $checkbox = $(checkboxSelector);
            $checkbox.prop(
                'checked', this.model.get('showSpectrogram'))
                .on('change', () => {
                    this.model.set(
                        'showSpectrogram', $checkbox.prop('checked'));
                });
        },

        /**
         * Callback for when a new file revision is selected.
         *
         * This supports single revisions and diffs. If 'base' is 0, a
         * single revision is selected, If not, the diff between `base` and
         * `tip` will be shown.
         *
         * Args:
         *     revisions (Array of number):
         *         A two-element array of [base, tip] revisions.
         */
        _onRevisionSelected(revisions) {
            const revisionIDs = this.model.get('attachmentRevisionIDs');
            const [base, tip] = revisions;

            // Ignore clicks on No Diff Label
            if (tip === 0) {
                return;
            }

            /*
             * Eventually these hard redirects will use a router
             * (see diffViewerPageView.js for example)
             * this.router.navigate(base + '-' + tip + '/', {trigger: true});
             */
            const revisionTip = revisionIDs[tip-1];
            let redirectURL;

            if (base === 0) {
                redirectURL = `../${revisionTip}/`;
            } else {
                const revisionBase = revisionIDs[base-1];
                redirectURL = `../${revisionBase}-${revisionTip}/`;
            }

            window.location.replace(redirectURL);
        },
    });
})();
