from __future__ import unicode_literals

from reviewboard.reviews.ui.base import FileAttachmentReviewUI


class AudioReviewUI(FileAttachmentReviewUI):
    name = 'Audio'
    supported_mimetypes = ['audio/*']

    allow_inline = True
    supports_diffing = True

    js_model_class = 'RB.AudioReviewable'
    js_view_class = 'RB.AudioReviewableView'

    def get_js_model_data(self):
        data = super(AudioReviewUI, self).get_js_model_data()
        data['audioURL'] = self.obj.file.url

        if self.diff_against_obj:
            data['diffAgainstAudioURL'] = self.diff_against_obj.file.url

        return data

    def serialize_comments(self, comments):
        result = {}
        serialized_comments = \
            super(AudioReviewUI, self).serialize_comments(comments)

        for serialized_comment in serialized_comments:
            try:
                position = '%(start)sx%(end)s-%(attachedToEarlierRevision)s' \
                           % serialized_comment
            except KeyError:
                # It's possible this comment was made before the review UI
                # was provided, meaning it has no data. If this is the case,
                # ignore this particular comment, since it doesn't have a
                # region.
                continue

            result.setdefault(position, []).append(serialized_comment)

        return result
