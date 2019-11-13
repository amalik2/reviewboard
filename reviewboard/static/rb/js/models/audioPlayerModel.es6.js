/**
 * Keeps track of audio player settings.
 *
 * Model Attributes:
 *     volume (number):
 *         How loud the playback volume is (0 to 1).
 *
 *     playbackSpeed (number):
 *         The speed to play the audio at.
 *
 *     audioURL (string):
 *         The URL of the audio to play.
 *
 *     currentCommentRegion (Region):
 *         The current wavesurfer.js region being edited.
 */
RB.AudioPlayer = Backbone.Model.extend({
    defaults: {
        volume: 0.5,
        playbackSpeed: 1.0,
        audioURL: '',
        currentCommentRegion: null
    },
});
