from __future__ import unicode_literals

import logging

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import date
from django.utils.formats import localize
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from django.utils.translation import ugettext
from djblets.views.generic.base import (CheckRequestMethodViewMixin,
                                        PrePostDispatchViewMixin)
from reviewboard.accounts.mixins import CheckLoginRequiredViewMixin
from reviewboard.attachments.models import FileAttachment
from reviewboard.diffviewer.models import DiffSet
from reviewboard.reviews.models import ReviewRequest
# from reviewboard.reviews.ui.base import FileAttachmentReviewUI
from reviewboard.site.mixins import CheckLocalSiteAccessViewMixin


class ReviewRequestViewMixin(CheckRequestMethodViewMixin,
                             CheckLoginRequiredViewMixin,
                             CheckLocalSiteAccessViewMixin,
                             PrePostDispatchViewMixin):
    """Common functionality for all review request-related pages.

    This performs checks to ensure that the user has access to the page,
    returning an error page if not. It also provides common functionality
    for fetching a review request for the given page, returning suitable
    context for the template, and generating an image used to represent
    the site when posting to social media sites.
    """

    permission_denied_template_name = \
        'reviews/review_request_permission_denied.html'

    def pre_dispatch(self, request, review_request_id, *args, **kwargs):
        """Look up objects and permissions before dispatching the request.

        This will first look up the review request, returning an error page
        if it's not accessible. It will then store the review request before
        calling the handler for the HTTP request.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            review_request_id (int):
                The ID of the review request being accessed.

            *args (tuple):
                Positional arguments to pass to the handler.

            **kwargs (dict):
                Keyword arguments to pass to the handler.

                These will be arguments provided by the URL pattern.

        Returns:
            django.http.HttpResponse:
            The resulting HTTP response to send to the client, if there's
            a Permission Denied.
        """
        self.review_request = self.get_review_request(
            review_request_id=review_request_id,
            local_site=self.local_site)

        if not self.review_request.is_accessible_by(request.user):
            return self.render_permission_denied(request)

        return None

    def render_permission_denied(self, request):
        """Render a Permission Denied page.

        This will be shown to the user if they're not able to view the
        review request.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            django.http.HttpResponse:
            The resulting HTTP response to send to the client.
        """
        return render(request,
                      self.permission_denied_template_name,
                      status=403)

    def get_review_request(self, review_request_id, local_site=None):
        """Return the review request for the given display ID.

        Args:
            review_request_id (int):
                The review request's display ID.

            local_site (reviewboard.site.models.LocalSite):
                The Local Site the review request is on.

        Returns:
            reviewboard.reviews.models.review_request.ReviewRequest:
            The review request for the given display ID and Local Site.

        Raises:
            django.http.Http404:
                The review request could not be found.
        """
        q = ReviewRequest.objects.all()

        if local_site:
            q = q.filter(local_site=local_site,
                         local_id=review_request_id)
        else:
            q = q.filter(pk=review_request_id)

        q = q.select_related('submitter', 'repository')

        return get_object_or_404(q)

    def get_diff(self, revision=None, draft=None):
        """Return a diff on the review request matching the given criteria.

        If a draft is provided, and ``revision`` is either ``None`` or matches
        the revision on the draft's DiffSet, that DiffSet will be returned.

        Args:
            revision (int, optional):
                The revision of the diff to retrieve. If not provided, the
                latest DiffSet will be returned.

            draft (reviewboard.reviews.models.review_request_draft.
                   ReviewRequestDraft, optional):
                The draft of the review request.

        Returns:
            reviewboard.diffviewer.models.diffset.DiffSet:
            The resulting DiffSet.

        Raises:
            django.http.Http404:
                The diff does not exist.
        """
        # Normalize the revision, since it might come in as a string.
        if revision:
            revision = int(revision)

        # This will try to grab the diff associated with a draft if the review
        # request has an associated draft and is either the revision being
        # requested or no revision is being requested.
        if (draft and draft.diffset_id and
            (revision is None or draft.diffset.revision == revision)):
            return draft.diffset

        query = Q(history=self.review_request.diffset_history_id)

        # Grab a revision if requested.
        if revision is not None:
            query = query & Q(revision=revision)

        try:
            return DiffSet.objects.filter(query).latest()
        except DiffSet.DoesNotExist:
            raise Http404

    def get_social_page_image_url(self, file_attachments):
        """Return the URL to an image used for social media sharing.

        This will look for the first attachment in a list of attachments that
        can be used to represent the review request on social media sites and
        chat services. If a suitable attachment is found, its URL will be
        returned.

        Args:
            file_attachments (list of reviewboard.attachments.models.
                              FileAttachment):
                A list of file attachments used on a review request.

        Returns:
            unicode:
            The URL to the first image file attachment, if found, or ``None``
            if no suitable attachments were found.
        """
        for file_attachment in file_attachments:
            if file_attachment.mimetype.startswith('image/'):
                return file_attachment.get_absolute_url()

        return None

    def get_review_request_status_html(self, review_request_details,
                                       close_info, extra_info=[]):
        """Return HTML describing the current status of a review request.

        This will return a description of the submitted, discarded, or open
        state for the review request, for use in the rendering of the page.

        Args:
            review_request_details (reviewboard.reviews.models
                                    .base_review_request_details
                                    .BaseReviewRequestDetails):
                The review request or draft being viewed.

            close_info (dict):
                A dictionary of information on the closed state of the
                review request.

            extra_info (list of dict):
                A list of dictionaries showing additional status information.
                Each must have a ``text`` field containing a format string
                using ``{keyword}``-formatted variables, a ``timestamp`` field
                (which will be normalized to the local timestamp), and an
                optional ``extra_vars`` for the format string.

        Returns:
            unicode:
            The status text as HTML for the page.
        """
        review_request = self.review_request
        status = review_request.status
        review_request_details = review_request_details

        if status == ReviewRequest.SUBMITTED:
            timestamp = close_info['timestamp']

            if timestamp:
                text = ugettext('Created {created_time} and submitted '
                                '{timestamp}')
            else:
                text = ugettext('Created {created_time} and submitted')
        elif status == ReviewRequest.DISCARDED:
            timestamp = close_info['timestamp']

            if timestamp:
                text = ugettext('Created {created_time} and discarded '
                                '{timestamp}')
            else:
                text = ugettext('Created {created_time} and discarded')
        elif status == ReviewRequest.PENDING_REVIEW:
            text = ugettext('Created {created_time} and updated {timestamp}')
            timestamp = review_request_details.last_updated
        else:
            logging.error('Unexpected review request status %r for '
                          'review request %s',
                          status, review_request.display_id,
                          request=self.request)

            return ''

        parts = [
            {
                'text': text,
                'timestamp': timestamp,
                'extra_vars': {
                    'created_time': date(localtime(review_request.time_added)),
                },
            },
        ] + extra_info

        html_parts = []

        for part in parts:
            if part['timestamp']:
                timestamp = localtime(part['timestamp'])
                timestamp_html = format_html(
                    '<time class="timesince" datetime="{0}">{1}</time>',
                    timestamp.isoformat(),
                    localize(timestamp))
            else:
                timestamp_html = ''

            html_parts.append(format_html(
                part['text'],
                timestamp=timestamp_html,
                **part.get('extra_vars', {})))

        return mark_safe(' &mdash; '.join(html_parts))


class ReviewFileAttachmentViewMixin(CheckLoginRequiredViewMixin):

    def get_attachments(self, request, file_attachment_id, review_request,
                        file_attachment_diff_id=None):
        # Make sure the attachment returned is part of either the review
        # request or an accessible draft.
        draft = review_request.get_draft(request.user)
        review_request_q = (Q(review_request=review_request) |
                            Q(inactive_review_request=review_request))

        if draft:
            review_request_q |= Q(drafts=draft) | Q(inactive_drafts=draft)

        file_attachment = get_object_or_404(
            FileAttachment,
            Q(pk=file_attachment_id) & review_request_q)

        if file_attachment_diff_id:
            file_attachment_revision = get_object_or_404(
                FileAttachment,
                Q(pk=file_attachment_diff_id) &
                Q(attachment_history=file_attachment.attachment_history) &
                review_request_q)
        else:
            file_attachment_revision = None

        return file_attachment, file_attachment_revision

    def set_attachment_ui(self, file_attachment):
        review_ui = file_attachment.review_ui

        # if not review_ui:
        #   review_ui = FileAttachmentReviewUI(self.review_request,
        #   file_attachment)

        return review_ui

    def set_enabled_for(self, request, review_ui, review_request,
                        file_attachment):
        try:
            # print(request.user)
            is_enabled_for = review_ui.is_enabled_for(
                user=request.user,
                review_request=review_request,
                file_attachment=file_attachment)
        except Exception as e:
            logging.error('Error when calling is_enabled_for for '
                          'FileAttachmentReviewUI %r: %s',
                          review_ui, e, exc_info=1)
            is_enabled_for = False
        return is_enabled_for
