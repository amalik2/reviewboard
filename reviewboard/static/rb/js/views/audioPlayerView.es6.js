(function() {

    /**
     * Gets a list of playback speed options that the user can select.
     *
     * Return the raw HTML for option tags for each selectable playback speed.
     */
    function getPlaybackSpeedOptions() {
        const options = [0.1, 0.25, 0.4, 0.5, 0.75, 1, 1.25, 1.5, 2, 5];
        return options.map((option) => {
            const selected = option === 1 ? ' selected' : '';
            return `<option value="${option}"${selected}>${option}x</option>`;
        }).join('');
    }

    /**
     * Represents the player interface for an audio file.
     */
    RB.AudioPlayerView = Backbone.View.extend({
        template: _.template([
            '<div class="audio-player-container">',
             '<i class="fa fa-spinner fa-spin fa-3x fa-fw" />',
             '<div class="audio-player">',
              '<div class="<%- containerClass %>"></div>',
             '</div>',
             '<div class="<%- containerClass %>-timeline"></div>',
             '<div class="<%- containerClass %>-spectrogram"></div>',
             '<div class="audio-controls hidden">',
              '<div class="playback-speed-container">',
               '<label for="<%= playbackSpeedId %>">',
                '<%- playbackSpeedLabel %>',
               '</label>',
               '<select name="playback-speed" id="<%= playbackSpeedId %>">',
                 getPlaybackSpeedOptions(),
               '</select>',
              '</div>',
              '<i class="play-audio-button fa fa-play-circle" />',
              '<i class="pause-audio-button hidden fa fa-pause-circle" />',
              '<div class="audio-volume-container">',
               '<i class="volume-icon fa fa-volume-up" />',
               '<input type="range" min="0" max="1" step="0.05" class="volume">',
              '</div>',
             '</div>',
            '</div>'
        ].join('')),

        /**
         * Initialize the view.
         * Args:
         *     options (object):
         *         Options for the view.
         *
         * Option Args:
         *     containerSelector (string):
         *         The CSS selector of the container to create for this player.
         *
         *     playerOptions (object):
         *         Options used to initialize the WaveformJS player.
         *
         *     model (RB.AudioPlayer):
         *         The model keeping track of the audio player's settings.
         */
        initialize(options) {
            this.$commentRegion = null;

            const $container = $(this.template({
                containerClass: options.containerSelector,
                playbackSpeedId: _.uniqueId('playback-speed-select'),
                playbackSpeedLabel: gettext('Playback speed')
            }));
            this.$el.append($container);

            this.playerOptions = options.playerOptions;
            this.player = null;
            this.fileLoaded = false;

            this.$waveform = $container.find(options.playerOptions.container);
            this.$audioControls = $container.find('.audio-controls');
            this.$spectrogram = $container.find(
                `${options.playerOptions.container}-spectrogram`);
            this.$spinner = $container.find('.fa-spinner');

            this._initVolumeSlider($container);
            this._initPlayAndPauseButtons($container);
            this._initPlaybackSpeed($container);
        },

        /**
         * Initializes the volume slider.
         *
         * Args:
         *     $container (JQuery):
         *         The root node of this view.
         */
        _initVolumeSlider($container) {
            const $volumeSlider = $container.find('.volume');

            $volumeSlider.val(this.model.get('volume'));

            $volumeSlider.change(() => {
                const newVolume = $volumeSlider[0].valueAsNumber;
                this.model.set('volume', newVolume);
                if (this.player) {
                    this.player.setVolume(newVolume);
                }
            });
        },

        /**
         * Initializes the pause and play buttons.
         *
         * Args:
         *     $container (JQuery):
         *         The root node of this view.
         */
        _initPlayAndPauseButtons($container) {
            this.$playButton = $container.find('.play-audio-button');
            this.$pauseButton = $container.find('.pause-audio-button');

            this.$playButton.click(this._onPlayButtonClicked.bind(this));
            this.$pauseButton.click(this._onPauseButtonClicked.bind(this));
        },

        /**
         * Initializes the playback speed components of the view.
         *
         * Args:
         *     $container (JQuery):
         *         The root node of this view.
         */
        _initPlaybackSpeed($container) {
            this.$playbackSpeedSelect = $container.find(
                'select[name="playback-speed"]');

            this.$playbackSpeedSelect.on('change', () => {
                const newSpeed = parseFloat(this.$playbackSpeedSelect[0].value);
                this.model.set('playbackSpeed', newSpeed);
            });
        },

        /**
         * Displays the loading spinner icon.
         */
        _showLoadingIcon() {
            this.$spinner.removeClass('hidden');
        },

        /**
         * Hides the loading spinner icon.
         */
        _hideLoadingIcon() {
            this.$spinner.addClass('hidden');
        },

        /**
         * Gets options to set for a new region in the player.
         *
         * Args:
         *     extraOptions (object):
         *         Additional options for the region.
         * Returns:
         *      object:
         *      All options for the region.
         */
        _getRegionOptions(extraOptions) {
            return $.extend(false, {
                drag: false,
                resize: false
            }, extraOptions);
        },

        /**
         * Saves the currently selected region to the player.
         *
         * Args:
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment corresponding to the region.
         */
        _saveSelectedRegion(commentBlockView) {
            const currentRegion = this.model.get('currentCommentRegion');
            this._onCommentAdded(currentRegion, commentBlockView);

            this.model.set('currentCommentRegion', null);
        },

        /**
         * Creates a new region in the player for a comment.
         *
         * Args:
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment corresponding to the region.
         */
        _createNewRegionForComment(commentBlockView) {
            const regionOptions = this._getRegionOptions({
                start: commentBlockView.model.get('start'),
                end: commentBlockView.model.get('end')
            });

            const newRegion = this.player.addRegion(regionOptions);
            this._onCommentAdded(newRegion, commentBlockView);
        },

        /**
         * Handles a new region being added to the player.
         *
         * Args:
         *     region (Region):
         *         The added region.
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment corresponding to the region.
         */
        _onCommentAdded(region, commentBlockView) {
            region.comment = commentBlockView;
            commentBlockView.$el.appendTo(region.element);
        },

        /**
         * Adds the specified comment to the player.
         *
         * Args:
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment to add.
         */
        addComment(commentBlockView) {
            if (this.model.get('currentCommentRegion')) {
                this._saveSelectedRegion(commentBlockView);
            } else {
                this._createNewRegionForComment(commentBlockView);
            }
        },

        /**
         * Removes the comment region the user currently has selected.
         */
        _removeSelectedRegion() {
            const currentRegion = this.model.get('currentCommentRegion');
            currentRegion.remove();
            this.model.set('currentCommentRegion', null);
        },

        /**
         * Gets a list of all comment regions in the player
         *
         * Returns:
         *     Region[]:
         *     A list of all comment regions.
         */
        _getCommentRegions() {
            return Object.values(this.player.regions.list);
        },

        /**
         * Removes an existing comment from the player.
         *
         * Args:
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment to delete.
         */
        _removeCreatedComment(commentBlockView) {
            const regionToRemove = this._getCommentRegions().find((region) => {
                return region.comment === commentBlockView;
            });

            if (regionToRemove) {
                regionToRemove.remove();
            }
        },

        /**
         * Removes the specified comment from the player.
         *
         * Args:
         *     commentBlockView (RB.AudioCommentBlockView):
         *         The view for the comment to delete.
         */
        removeComment(commentBlockView) {
            if (this.model.get('currentCommentRegion')) {
                this._removeSelectedRegion();
            } else {
                this._removeCreatedComment(commentBlockView);
            }
        },

        /**
         * Gets whether the audio file has fully loaded or not.
         *
         * Returns:
         *     boolean:
         *     Whether the audio file has fully loaded or not.
         */
        hasLoaded() {
            return this.fileLoaded;
        },

        /**
         * Handles the audio file successfully being loaded.
         */
        _onFileLoaded() {
            this._hideLoadingIcon();
            this.$audioControls.removeClass('hidden');

            this.player.disableDragSelection();
            this.player.enableDragSelection(this._getRegionOptions({}));

            this.fileLoaded = true;
            this.trigger('fileLoaded');
        },

        /**
         * Handles the player reaching the end of the audio file.
         */
        _onAudioFinished() {
            this.$pauseButton.addClass('hidden');
            this.$playButton.removeClass('hidden');
        },

        /**
         * Handles the user creating a region in the waveform graph.
         *
         * Args:
         *     region (Region):
         *         The region that was created.
         */
        _onRegionCreated(region) {
            if (this.model.get('currentCommentRegion')) {
                region.remove();
                return;
            }

            this.model.set('currentCommentRegion', region);
            this.trigger('regionCreated', region);
        },

        /**
         * Handles the user clicking a region in the waveform graph.
         *
         * Args:
         *     region (Region):
         *         The region that was clicked.
         *     e (ClickEvent):
         *         The HTML click event.
         */
        _onRegionClicked(region, e) {
            e.stopPropagation();
            if (e.shiftKey) {
                region.play();
            } else if (!this.model.get('currentCommentRegion')) {
                region.comment.click();
            }
        },

        /**
         * Handles an error occurring while loading or playing the audio file.
         *
         * Args:
         *     errorMsg (string):
         *         The message corresponding to the error.
         */
        _onAudioError(errorMsg) {
            const errorNotification =
                'An error occurred while loading the audio file:\n';
            alert(`${errorNotification}${errorMsg}`);
            console.error(errorMsg);
        },

        /**
         * Initializes listeners for events emitted by the player.
         */
        _listenToPlayerEvents() {
            this.player.on('load', this._showLoadingIcon.bind(this));
            this.player.on('ready', this._onFileLoaded.bind(this));
            this.player.on('destroy', this._hideLoadingIcon.bind(this));
            this.player.on('error', this._hideLoadingIcon.bind(this));
            this.player.on('finish', this._onAudioFinished.bind(this));
            this.player.on('region-update-end', this._onRegionCreated.bind(this));
            this.player.on('region-click', this._onRegionClicked.bind(this));
            this.player.on('error', this._onAudioError.bind(this));
        },

        /**
         * Renders the audio player with a waveform graph.
         */
        render() {
            this.player = WaveSurfer.create(this.playerOptions);

            this.player.setVolume(this.model.get('volume'));
            this.player.setPlaybackRate(this.model.get('playbackSpeed'));
            this._listenToPlayerEvents();
            this.player.load(this.model.get('audioURL'));

            this.model.on('change:playbackSpeed', () => {
                this.player.setPlaybackRate(this.model.get('playbackSpeed'));
            });
        },

        /**
         * Displays the spectrogram for this audio file
         */
        showSpectrogram() {
            this.$spectrogram.removeClass('hidden');
        },

        /**
         * Hides the spectrogram for this audio file
         */
        hideSpectrogram() {
            this.$spectrogram.addClass('hidden');
        },

        /**
         * Handler for when the play button is clicked.
         *
         * Starts playing the audio file from the current position.
         */
        _onPlayButtonClicked() {
            if (this.player.isPlaying()) {
                return;
            }

            this.player.play();
            this.$playButton.addClass('hidden');
            this.$pauseButton.removeClass('hidden');
        },

        /**
         * Handler for when the pause button is clicked.
         *
         * Stops playing the audio file.
         */
        _onPauseButtonClicked() {
            if (!this.player.isPlaying()) {
                return;
            }

            this.player.pause();
            this.$pauseButton.addClass('hidden');
            this.$playButton.removeClass('hidden');
        },
    });

})();