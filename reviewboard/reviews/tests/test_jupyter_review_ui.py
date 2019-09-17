from reviewboard.reviews.ui.jupyterui import (
    render_notebook_data, get_cell_execution_details,
    get_data_type_and_value, render_output, render_data, escape_text)
from reviewboard.testing import TestCase


def get_notebook(cells):
    return {
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


def get_cell_with_output(data, output_type='display_data'):
    cell = {
        'cell_type': 'code',
        'metadata': {
            'id': 'tuhrMYoWxDYc'
        },
        'source': [],
        'execution_count': 0,
        'outputs': [{
            'output_type': output_type,
            'data': data,
            'metadata': {
                'tags': []
            }
        }]
    }

    input_cell_details = [
        'In [ ]:']

    return cell, input_cell_details


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
        expected_html = '<div><h1>Jupyter ' \
            'markdown test</h1></div>'

        rendered_data = render_notebook_data(notebook_data)
        expected_data = [
            '<div style="text-align: center">Cell 1 (markdown)</div>',
            expected_html,
            '<hr />'
        ]
        self.assertEqual(rendered_data, expected_data)

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

        first_cell_html = '<div><h1>First cell</h1></div>'
        second_cell_html = '<div><h1>Second cell</h1></div>'

        rendered_data = render_notebook_data(notebook_data)
        expected_data = [
            '<div style="text-align: center">Cell 1 (markdown)</div>',
            first_cell_html,
            '<hr />',
            '<div style="text-align: center">Cell 2 (markdown)</div>',
            second_cell_html,
            '<hr />'
        ]
        self.assertEqual(rendered_data, expected_data)

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
        expected_html = '<div><ul>\n<li>&lt;array&gt;.tolist()</li>\n</ul>' \
            '</div>'

        rendered_data = render_notebook_data(notebook_data)
        expected_data = [
            '<div style="text-align: center">Cell 1 (markdown)</div>',
            expected_html,
            '<hr />'
        ]
        self.assertEqual(rendered_data, expected_data)

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
            'execution_count': 24,
            'outputs': []
        }])

        expected_html = [
            '<div style="text-align: center">Cell 1 (code)</div>',
            'In [24]:', '<div class="input-area">'
            '<div class="cell-with-whitespace"><span class="n">myint</span> '
            '<span class="o">=</span> <span class="mi">7</span>\n</div></div>',
            '<div class="input-area"><div class="cell-with-whitespace">'
            '<span class="k">print</span><span class="p">(</span>'
            '<span class="n">myint</span>'
            '<span class="p">)</span>\n</div></div>', '<hr />']

        rendered_data = render_notebook_data(notebook_data)
        self.assertEqual(rendered_data, expected_html)

    def test_render_notebook_data_with_image_output(self):
        """Testing render_notebook_data with image output data"""
        cell_with_output, input_cell_details = get_cell_with_output({
            'image/png': 'iawejkiawjeiaiwe\n'
        })

        notebook_data = get_notebook([cell_with_output])

        expected_output_html = '<img src="' \
            'data:image/png;base64, iawejkiawjeiaiwe" alt="cell output" />'

        rendered_data = render_notebook_data(notebook_data)
        expected_data = ['<div style="text-align: center">Cell 1 (code)</div>']
        expected_data += input_cell_details
        expected_data += [
            '<div>Out [ ]:</div>',
            expected_output_html,
            '<hr />'
        ]
        self.assertEqual(rendered_data, expected_data)

    def test_render_notebook_data_with_text_output(self):
        """Testing render_notebook_data with text output data"""
        cell_with_output, input_cell_details = get_cell_with_output({
            'text/plain': [
                'first output line\n',
                'second output line\n'
            ]
        })

        notebook_data = get_notebook([cell_with_output])

        expected_output_html = '<div>' \
            'first output line\nsecond output line\n</div>'

        rendered_data = render_notebook_data(notebook_data)
        expected_data = ['<div style="text-align: center">Cell 1 (code)</div>']
        expected_data += input_cell_details
        expected_data += [
            '<div>Out [ ]:</div>',
            expected_output_html,
            '<hr />'
        ]
        self.assertEqual(rendered_data, expected_data)

    def test_render_output_with_display_data(self):
        """Testing render_output with display_data"""
        output = render_output({
            'output_type': 'display_data',
            'data': {
                'text/plain': [
                    'test'
                ]
            }
        })

        self.assertEqual(['<div>test</div>'], output[1:])

    def test_render_output_with_execute_result(self):
        """Testing render_output with execute_result"""
        output = render_output({
            'output_type': 'execute_result',
            'data': {
                'text/plain': [
                    'test'
                ]
            }
        })

        self.assertEqual(['<div>test</div>'], output[1:])

    def test_render_output_with_stream(self):
        """Testing render_output with stream"""
        output = render_output({
            'output_type': 'stream',
            'text': [
                'test'
            ]
        })

        self.assertEqual(
            ['<div class="cell-with-whitespace">test</div>'], output[1:])

    def test_render_output_with_error(self):
        """Testing render_output with error"""
        output = render_output({
            'output_type': 'error',
            'evalue': 'error message'
        })

        self.assertEqual(['<div>error message</div>'], output[1:])

    def test_get_cell_execution_details_with_null(self):
        """Testing get_cell_execution_details with a null value"""
        result = get_cell_execution_details({
            'execution_count': None
        })

        self.assertEqual(u'In [ ]:', result)

    def test_get_cell_execution_details_with_0(self):
        """Testing get_cell_execution_details with value of 0"""
        result = get_cell_execution_details({
            'execution_count': 0
        })

        self.assertEqual(u'In [ ]:', result)

    def test_get_cell_execution_details_with_value_above_0(self):
        """Testing get_cell_execution_details with value above 0"""
        result = get_cell_execution_details({
            'execution_count': 99
        })

        self.assertEqual(u'In [99]:', result)

    def test_get_data_type_and_value_should_return_non_plaintext_value(self):
        """
            Testing if get_data_type_and_value returns the first
            non plaintext value
        """
        key, value = get_data_type_and_value({
            'text/plain': 'first',
            'text/markdown': 'second'
        })

        self.assertEqual('text/markdown', key)
        self.assertEqual('second', value)

    def test_render_data_splits_up_list(self):
        """Testing if render_data splits up a list into a string"""
        result = render_data({
            'text/plain': ['line1', 'line2']
        })

        self.assertEqual('<div>line1line2</div>', result)

    def test_render_data_with_string(self):
        """Testing if render_data with a string"""
        result = render_data({
            'text/plain': 'line'
        })

        self.assertEqual('<div>line</div>', result)

    def test_escape_text_with_left_angle_bracket(self):
        """Testing if escape_text replaces \\< for HTML rendering"""
        escaped_text = escape_text('\\<')

        self.assertEqual('&lt;', escaped_text)

    def test_escape_text_with_right_angle_bracket(self):
        """Testing if escape_text replaces \\> for HTML rendering"""
        escaped_text = escape_text('\\>')

        self.assertEqual('&rt;', escaped_text)
