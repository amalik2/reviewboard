/**
 * Provides review capabilities for audio file attachments.
 *
 * Model Attributes:
 *     audioURL (string):
 *         The audio URL.
 *
 *     diffAgainstAudioURL (string):
 *         The audio URL of the original audio in the case of an audio diff.
 *
 *     showSpectrogram (boolean):
 *         Whether to show the spectrogram for the audio or not.
 */
RB.AudioReviewable = RB.FileAttachmentReviewable.extend({
    defaults: _.defaults({
        audioURL: '',
        diffAgainstAudioURL: '',
        showSpectrogram: false
    }, RB.FileAttachmentReviewable.prototype.defaults),

    commentBlockModel: RB.AudioCommentBlock,
});
