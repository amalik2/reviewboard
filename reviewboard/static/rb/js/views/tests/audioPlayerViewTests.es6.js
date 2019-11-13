suite('rb/views/AudioPlayerView', function() {
    function mockPlayerVolume(playerSpy) {
        let volume = 0.5;
        playerSpy.setVolume.and.callFake((v) => {
            volume = v;
        });
        playerSpy.getVolume.and.callFake(() => volume);
    }

    function mockPlayerPlaybackRate(playerSpy) {
        let rate = 1;
        playerSpy.setPlaybackRate.and.callFake((v) => {
            rate = v;
        });
        playerSpy.getPlaybackRate.and.callFake(() => rate);
    }

    function mockPlayStatus(playerSpy) {
        let isPlaying = false;
        playerSpy.play.and.callFake(() => {
            isPlaying = true;
        });
        playerSpy.pause.and.callFake(() => {
            isPlaying = false;
        });
        playerSpy.isPlaying.and.callFake(() => isPlaying);
    }

    function mockPlayerRegions(playerSpy) {
        const regions = [];
        playerSpy.addRegion.and.callFake((regionData) => {
            regions.push(regionData);
            regionData.remove = () => {
                const index = regions.indexOf(regionData);
                regions.splice(index, 1);
            };
            return regionData;
        });

        playerSpy.regions = {
            list: regions
        };
    }

    function createMockAudioPlayer() {
        const waveSurferSpy = jasmine.createSpyObj(
            'WaveSurfer', ['create']);
        const playerSpy = jasmine.createSpyObj(
            'player',
            ['setVolume', 'setPlaybackRate', 'getPlaybackRate', 'getVolume',
                'on', 'isPlaying', 'load', 'disableDragSelection',
                'enableDragSelection', 'addRegion', 'play', 'pause']
        );
        
        waveSurferSpy.create.and.returnValue(playerSpy);
        mockPlayerVolume(playerSpy);
        mockPlayerPlaybackRate(playerSpy);
        mockPlayStatus(playerSpy);
        mockPlayerRegions(playerSpy);

        waveSurferModule = window.WaveSurfer;
        window.WaveSurfer = waveSurferSpy;
    }

    function createComment() {
        const commentModel = new RB.AudioCommentBlock({
            start: 0.5,
            end: 1.0,
            reviewRequest: new RB.ReviewRequest({
                reviewURL: '/r/123/',
            }),
            review: new RB.Review()
        });
        return new RB.AudioCommentBlockView({
            model: commentModel
        });
    }

    const template = dedent`
      <div id="container">
      </div>
    `;

    let $container;
    let model;
    let view;
    let waveSurferModule;

    beforeEach(function() {
        $container = $(template).appendTo($testsScratch);

        model = new RB.AudioPlayer();

        view = new RB.AudioPlayerView({
            el: $container,
            playerOptions: {
                container: '.test-container'
            },
            containerSelector: 'test-container',
            model,
        });
        createMockAudioPlayer();

        view.render();
    });

    afterEach(function() {
        view.remove();
        $container.remove();
        window.WaveSurfer = waveSurferModule;
    });

    it('Hides the audio controls while the audio loads', function() {
        expect($('.audio-controls.hidden').length).toBe(1);
    });

    it('Shows the audio controls after the audio loads', function() {
        view._onFileLoaded();
        expect($('.audio-controls:not(.hidden)').length).toBe(1);
    });

    it('Shows the play button and hides the pause button', function() {
        expect($('.play-audio-button:not(.hidden)').length).toBe(1);
        expect($('.pause-audio-button.hidden').length).toBe(1);
    });

    it('Shows hides play button and shows the pause button while playing',
        function() {
            view._onPlayButtonClicked();
            expect($('.play-audio-button.hidden').length).toBe(1);
            expect($('.pause-audio-button:not(.hidden)').length).toBe(1);
        });

    it('Clicking pause should pause the audio', function() {
        view._onPlayButtonClicked();
        view._onPauseButtonClicked();
        expect(view.player.isPlaying()).toBe(false);
    });

    it('Clicking play should resume the audio', function() {
        view._onPlayButtonClicked();
        expect(view.player.isPlaying()).toBe(true);
    });

    it('Adjusting the volume should update the player', function() {
        const $volume = $('.volume');
        $volume.val(0.85);
        $volume.change();
        expect(view.player.getVolume()).toBe(0.85);
    });

    it('Adjusting the playback speed should update the player', function() {
        const $playbackSpeed = $(
            'select[name="playback-speed"] option[value="0.5"]');
        $playbackSpeed.prop('selected', true);
        $playbackSpeed.parent().change();
        expect(view.player.getPlaybackRate()).toBe(0.5);
    });

    it('Adding a comment should add a region to the player', function() {
        const commentBlockView = createComment();

        view.addComment(commentBlockView);

        const comments = view._getCommentRegions();
        expect(comments.length).toBe(1);
        expect(comments[0].comment).toBe(commentBlockView);
    });

    it('Removing a comment should remove that region from the player',
        function() {
            const commentBlockView = createComment();

            view.addComment(commentBlockView);
            view.removeComment(commentBlockView);
            expect(view._getCommentRegions().length).toBe(0);
        });

    it('The spectrogram should be visible after toggling it on', function() {
        view.showSpectrogram();
        expect($('.test-container-spectrogram:not(.hidden)').length).toBe(1);
    });

    it('The spectrogram should be hidden after toggling it off', function() {
        view.showSpectrogram();
        view.hideSpectrogram();
        expect($('.test-container-spectrogram.hidden').length).toBe(1);
    });
});
