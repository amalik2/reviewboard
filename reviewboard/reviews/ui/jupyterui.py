from __future__ import unicode_literals

import logging
import json
import nbformat

from django.utils.translation import ugettext as _
from djblets.markdown import iter_markdown_lines
from pygments.lexers import JsonLexer
from nbconvert import HTMLExporter
from lxml import etree

from reviewboard.reviews.chunk_generators import MarkdownDiffChunkGenerator
from reviewboard.reviews.ui.text import TextBasedReviewUI
from reviewboard.reviews.markdown_utils import render_markdown_from_file


class CustomHTMLExporter(HTMLExporter):

    template_file = 'basic'

    @property
    def default_config(self):
        config = super(CustomHTMLExporter, self).default_config
        config.merge({
            'CSSHTMLHeaderPreprocessor': {
                'enabled': False
            }
        })
        return config


nb_exporter = CustomHTMLExporter()
print(nb_exporter.default_config)

def filter_generated_html(root):
    for anchor in root.xpath('//a[@class="anchor-link"]'):
        anchor.getparent().remove(anchor)

    for prompt in root.xpath('//div[@class="prompt input_prompt"]'):
        prompt.getparent().remove(prompt)


def convert_node_to_string(node):
    return etree.tostring(node).replace('\\&lt;', '&lt;')


def render_notebook_data(notebook):
    data = nb_exporter.from_notebook_node(notebook)[0]
    parser = etree.HTMLParser()
    root = etree.fromstring(
        '<html>%s</html>' % data, parser=parser).getchildren()[0]

    filter_generated_html(root)
    elements = []
    for node in root.getchildren():
        elements.append(convert_node_to_string(node))

    return elements


class JupyterReviewUI(TextBasedReviewUI):
    """A Review UI for Jupyter notebook files.

    This renders the notebook to HTML, and allows users to comment on each
    cell.
    """
    # TODO: test this
    supported_mimetypes = ['application/ipynb+json']
    object_key = 'jupyter'
    can_render_text = True

    extra_css_classes = ['jupyter-review-ui']

    js_view_class = 'RB.JupyterReviewableView'

    def generate_render(self):
        try:
            with self.obj.file as f:
                f.open()
                nb = nbformat.read(f, as_version=4)
                data = render_notebook_data(nb)

            for line in data:
                yield line
        except Exception as e:
            logging.error('Failed to parse resulting Jupyter XHTML for '
                          'file attachment %d: %s',
                          self.obj.pk, e,
                          exc_info=True)
            yield _('Error while rendering Jupyter content: %s') % e

    def get_source_lexer(self, filename, data):
        return JsonLexer()
