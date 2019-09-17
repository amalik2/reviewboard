from __future__ import unicode_literals

import logging
import json

from django.utils.translation import ugettext as _

from pygments import highlight
from pygments.lexers import JsonLexer, PythonLexer

from reviewboard.reviews.chunk_generators import MarkdownDiffChunkGenerator
from reviewboard.reviews.ui.text import TextBasedReviewUI
from reviewboard.diffviewer.chunk_generator import NoWrapperHtmlFormatter
from reviewboard.reviews.markdown_utils import render_markdown


cell_indicator_template = '<div style="text-align: center">Cell %d (%s)</div>'


def escape_text(text):
    return text.replace('\\<', '&lt;').replace('\\>', '&rt;')


def render_contents_inside_div(contents, preserve_whitespace=False):
    contents = escape_text(contents)
    if preserve_whitespace:
        return '<div class="cell-with-whitespace">%s</div>' % contents
    return '<div>%s</div>' % contents


def render_markdown_cell(cell):
    content = []
    for line in cell['source']:
        rendered_line = render_markdown(
            line.replace('\\<', '<').replace('\\>', '>'))
        content.append(render_contents_inside_div(rendered_line))

    return content


def get_cell_execution_details(cell, exec_type='In'):
    exec_count = cell['execution_count'] if 'execution_count' in cell else None
    if not exec_count:
        exec_count = ' '
    return '%s [%s]:' % (exec_type, exec_count)


def render_code_cell(cell):
    code = [
        get_cell_execution_details(cell)
    ]

    for line in cell['source']:
        highlighted_code = highlight(
            line, PythonLexer(), NoWrapperHtmlFormatter())
        rendered_input = render_contents_inside_div(
            highlighted_code, preserve_whitespace=True)
        code.append('<div class="input-area">%s</div>' % rendered_input)

    return code


def render_raw_cell(cell):
    content = []
    for line in cell['source']:
        content.append(render_contents_inside_div(line))
    return content


def render_cell(cell):
    cell_type = cell['cell_type']

    if cell_type == 'markdown':
        return render_markdown_cell(cell)
    elif cell_type == 'code':
        return render_code_cell(cell)
    elif cell_type == 'raw':
        return render_raw_cell(cell)

    raise ValueError(cell_type + ' is not a valid cell type')


def render_data_contents(data_type, contents):
    if 'image/' in data_type:
        return '<img src="data:%s;base64, %s" alt="cell output" />' % (
            data_type, contents.strip())

    return render_contents_inside_div(contents)


def get_data_type_and_value(data):
    sorted_items = sorted(
        data.items(), key=lambda pair: 1 if pair[0] == 'text/plain' else 0)
    return sorted_items[0]


def render_data(data):
    data_type, data_value = get_data_type_and_value(data)

    if isinstance(data_value, list):
        return render_data_contents(data_type, ''.join(data_value))
    else:
        return render_data_contents(data_type, data_value)


def render_execute_result(output):
    return [render_data(output['data'])]


def render_display_data(output):
    return [render_data(output['data'])]


def render_stream(output):
    text = ''.join(output['text'])
    return [render_contents_inside_div(text, preserve_whitespace=True)]


def render_error(output):
    error = output['evalue']
    return [render_contents_inside_div(error)]


def render_output(output):
    output_type = output['output_type']

    output_exec = get_cell_execution_details(output, exec_type='Out')
    rendered_output = ['<div>%s</div>' % output_exec]

    if output_type == 'execute_result':
        return rendered_output + render_execute_result(output)
    elif output_type == 'display_data':
        return rendered_output + render_display_data(output)
    elif output_type == 'stream':
        return rendered_output + render_stream(output)
    elif output_type == 'error':
        return rendered_output + render_error(output)

    raise ValueError(output_type + ' is not a valid output type')


def render_notebook_data(notebook):
    lines = []

    i = 1
    for cell in notebook['cells']:
        lines.append(cell_indicator_template % (i, cell['cell_type']))
        lines += render_cell(cell)

        if 'outputs' in cell:
            for output in cell['outputs']:
                lines += render_output(output)

        lines.append('<hr />')
        i += 1

    return lines


class JupyterReviewUI(TextBasedReviewUI):
    """A Review UI for Jupyter notebook files.

    This renders the notebook to HTML, and allows users to comment on each
    cell.
    """
    supported_mimetypes = ['application/ipynb+json']
    object_key = 'jupyter'
    can_render_text = True
    rendered_chunk_generator_cls = MarkdownDiffChunkGenerator

    extra_css_classes = ['jupyter-review-ui']

    js_view_class = 'RB.JupyterReviewableView'

    def generate_render(self):
        try:
            with self.obj.file as f:
                f.open()
                nb = json.load(f)
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
