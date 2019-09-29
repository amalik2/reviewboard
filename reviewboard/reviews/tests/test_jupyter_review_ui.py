import json

from nbformat.v4 import to_notebook

from reviewboard.reviews.ui.jupyterui import render_notebook_data
from reviewboard.testing import TestCase


def get_notebook(cells):
    data = {
        'nbformat': 4,
        'nbformat_minor': 0,
        'metadata': {
            'kernelspec': {
                'name': 'python3',
                'display_name': 'Python 3'
            }
        },
        'cells': cells
    }

    return to_notebook(data)


def get_cell_with_output(data):
    cell = {
        'cell_type': 'code',
        'metadata': {
            'id': 'tuhrMYoWxDYc'
        },
        'source': [],
        'execution_count': 0,
        'outputs': [{
            'output_type': 'display_data',
            'data': data,
            'metadata': {
                'tags': []
            }
        }]
    }

    expected_source_html = '<div class="inner_cell">\n    ' \
            '<div class="input_area">\n<div class=" highlight hl-ipython3">' \
            '<pre><span/>\n</pre></div>\n\n    </div>\n</div>\n'

    return cell, expected_source_html


class JupyterReviewUITests(TestCase):
    """Unit tests for reviewboard.reviews.ui.jupyterui."""

    def test_render_notebook_data_with_empty_notebook(self):
        """Testing render_notebook_data with an empty notebook"""
        notebook_data = get_notebook([])

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data, [])

    def test_render_notebook_data_with_markdown(self):
        """Testing render_notebook_data with a markdown cell"""
        notebook_data = get_notebook([{
            'cell_type': 'markdown',
            'metadata': {
                'id': 'ZN7m0ivNclYs'
            },
            'source': [
                '# Jupyter markdown test\n'
            ]
        }])
        expected_html = '<div class="text_cell_render border-box-sizing ' \
            'rendered_html">\n<h1 id="Jupyter-markdown-test">Jupyter ' \
            'markdown test</h1>\n</div>\n'

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data, [expected_html])

    def test_render_notebook_data_with_multiple_cells(self):
        """Testing render_notebook_data with multiple cells"""
        notebook_data = get_notebook([{
            'cell_type': 'markdown',
            'metadata': {
                'id': 'ZN7m0ivNclYs'
            },
            'source': [
                '# First cell\n'
            ]
        }, {
            'cell_type': 'markdown',
            'metadata': {
                'id': '1f9wW8xOc63w'
            },
            'source': [
                '# Second cell'
            ]
        }])

        first_cell_html = '<div class="text_cell_render border-box-sizing ' \
            'rendered_html">\n<h1 id="First-cell">First cell</h1>\n</div>\n'

        second_cell_html = '<div class="text_cell_render border-box-sizing ' \
            'rendered_html">\n<h1 id="Second-cell">Second cell</h1>\n</div>\n'

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data, [first_cell_html, second_cell_html])

    def test_render_notebook_data_with_angle_brackets(self):
        """Testing render_notebook_data with text containing angle brackets"""
        notebook_data = get_notebook([{
            'cell_type': 'markdown',
            'metadata': {
                'id': 'ZN7m0ivNclYs'
            },
            'source': [
                '* \\<array\\>.tolist()'
            ]
        }])
        expected_html = '<div class="text_cell_render border-box-sizing ' \
            'rendered_html">\n<ul>\n<li>&lt;array&gt;.tolist()</li>\n</ul>' \
            '\n\n</div>\n'

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data, [expected_html])

    def test_render_notebook_data_with_code(self):
        """Testing render_notebook_data with a code cell"""
        notebook_data = get_notebook([{
            'cell_type': 'code',
            'metadata': {
                'id': 'tuhrMYoWxDYc'
            },
            'source': [
                'myint = 7\n',
                'print(myint)\n'
            ],
            'execution_count': 0,
            'outputs': []
        }])

        expected_html = '<div class="inner_cell">\n' \
            '    <div class="input_area">\n<div class=" highlight ' \
            'hl-ipython3"><pre><span/><span class="n">myint</span> ' \
            '<span class="o">=</span> <span class="mi">7</span>\n' \
            '<span class="nb">print</span><span class="p">' \
            '(</span><span class="n">myint</span><span class="p">)</span>\n' \
            '</pre></div>\n\n    </div>\n</div>\n'

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data, [expected_html])

    def test_render_notebook_data_with_image_output(self):
        """Testing render_notebook_data with image output data"""
        cell_with_output, expected_source_html = get_cell_with_output({
            'image/png': 'iawejkiawjeiaiwe\n'
        })

        notebook_data = get_notebook([cell_with_output])

        expected_output_html = '<div class="output">\n\n\n' \
            '<div class="output_area">\n\n    <div class="prompt"/>' \
            '\n\n\n\n\n<div class="output_png output_subarea ">\n' \
            '<img src="data:image/png;base64,iawejkiawjeiaiwe&#10;"/>\n' \
            '</div>\n\n</div>\n\n</div>\n'

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data,
            [expected_source_html, expected_output_html])

    def test_render_notebook_data_with_text_output(self):
        """Testing render_notebook_data with text output data"""
        cell_with_output, expected_source_html = get_cell_with_output({
            'text/plain': [
                'first output line\n',
                'second output line\n'
            ]
        })

        notebook_data = get_notebook([cell_with_output])

        expected_output_html = '<div class="output">\n\n\n' \
            '<div class="output_area">\n\n    <div class="prompt"/>' \
            '\n\n\n\n\n<div class="output_text output_subarea ">\n<pre>' \
            'first output line\nsecond output line\n</pre>\n</div>\n\n</div>' \
            '\n\n</div>\n'

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data,
            [expected_source_html, expected_output_html])
