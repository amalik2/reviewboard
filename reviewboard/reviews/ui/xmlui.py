from __future__ import unicode_literals

import logging

from lxml import etree

from django.utils.translation import ugettext as _
from django.utils.encoding import force_text, force_bytes

from pygments.lexers import XmlLexer
from pygments import highlight
from pygments.formatters import HtmlFormatter

from reviewboard.reviews.ui.text import TextBasedReviewUI


def get_indent_str(indent_level):
    """Gets the string to use for indentation with the specified indentation
    level.
    """
    return '    ' * indent_level


def is_comment_element(element):
    """Gets whether the specified element is a comment or not."""
    return element.tag is etree.Comment


def parse_text_from_element_source(tag_name, element_source):
    """Parses the inner text content of the specified element."""
    tag_as_bytes = force_bytes(tag_name)

    start_indicator = b'<' + tag_as_bytes + b'>'
    start_index = element_source.find(start_indicator) + len(start_indicator)

    end_indicator = b'</' + tag_as_bytes + b'>'
    end_index = element_source.rfind(end_indicator)

    return force_text(element_source[start_index:end_index])


def get_element_text(element):
    """Gets the text content that the specified element has.

    If it does not have any text, a blank string will be returned.
    If it has actual text, the text will have leading and trailing whitespace
    stripped.
    """
    element_as_string = etree.tostring(element)
    has_cdata = element_as_string.find(b'<![CDATA[') > -1

    if has_cdata:
        text = parse_text_from_element_source(element.tag, element_as_string)
    else:
        text = element.text

    return text.strip() if text else ''


def get_attributes_str(element):
    """Gets the attributes associated with the specified element has as a
    space separated string of key-value pairs.
    """
    attributes = ''
    for attribute in element.attrib:
        if attributes:
            attributes += ' '

        attributes += '{}="{}"'.format(attribute, element.attrib[attribute])
    return attributes


def get_formatted_attributes(element):
    """Formats the attributes an element has for display."""
    attributes = get_attributes_str(element)
    if attributes:
        return ' ' + attributes

    return ''


def indent_text(text, indent_level):
    """Indents each line in the specified text based on the given
    indentation level.
    """
    indent_str = get_indent_str(indent_level)
    lines = text.split('\n')

    for i in range(0, len(lines)):
        lines[i] = indent_str + lines[i]

    return '\n'.join(lines)


def format_empty_element_tag(element, indent_level):
    """Formats the specified element as an empty element tag.
    Indentation is applied according to the specified indentation level.
    """
    indent = get_indent_str(indent_level)
    attributes = get_formatted_attributes(element)

    return '%(indent)s<%(tag)s%(attributes)s />\n' % {
        'indent': indent, 'tag': element.tag, 'attributes': attributes}


def format_element_with_text(element, indent_level, same_line=False):
    """Formats the specified element as one with text content.
    Indentation is applied according to the specified indentation level.
    """
    indent = get_indent_str(indent_level)
    text = get_element_text(element)
    attributes = get_formatted_attributes(element)

    if same_line:
        line_separator = ''
        closing_indent = ''
    else:
        text = indent_text(text, indent_level + 1)
        line_separator = '\n'
        closing_indent = indent

    format_options = {
        'indent': indent, 'tag': element.tag, 'text': text,
        'attr': attributes, 'separator': line_separator,
        'closing_indent': closing_indent
    }

    return '%(indent)s<%(tag)s%(attr)s>%(separator)s' \
        '%(text)s%(separator)s' \
        '%(closing_indent)s</%(tag)s>\n' % format_options


def format_comment_element(element, indent_level):
    """Formats the specified element as one that is a comment.
    Indentation is applied according to the specified indentation level.
    """
    indent = get_indent_str(indent_level)

    return '%(indent)s<!--%(comment)s-->\n' % {
        'indent': indent, 'comment': element.text}


def format_element_with_children(element, indent_level, same_line_text=False):
    """Formats the specified element as one with children.
    Indentation is applied according to the specified indentation level.
    """
    indent = get_indent_str(indent_level)
    attributes = get_formatted_attributes(element)
    children = element.getchildren()

    contents = '%(indent)s<%(tag)s%(attributes)s>\n' % {
        'indent': indent, 'tag': element.tag, 'attributes': attributes}

    for child in children:
        contents += format_element(child, indent_level + 1, same_line_text)

    closing_tag = '%(indent)s</%(tag)s>\n' % {
        'indent': indent, 'tag': element.tag}

    return contents + closing_tag


def format_element(element, indent=0, keep_text_on_same_line=False):
    """Formats the specified element.
    Indentation is applied according to the specified indentation level.
    """
    children = element.getchildren()

    if children:
        return format_element_with_children(element, indent,
                                            keep_text_on_same_line)
    elif is_comment_element(element):
        return format_comment_element(element, indent)

    text = get_element_text(element)
    if text:
        return format_element_with_text(element, indent,
                                        same_line=keep_text_on_same_line)
    else:
        return format_empty_element_tag(element, indent)


def get_xml_declaration(raw_xml):
    """Gets the declaration tag associated with the specified xml contents.
    If no declaration tag is found, an empty string is returned.
    """
    raw_xml = force_text(raw_xml)

    if raw_xml.find('<?xml') == 0:
        end_index = raw_xml.find('?>') + 2
        return force_text(raw_xml[:end_index], encoding='ascii')
    return ''


def get_encoding_from_declaration(declaration):
    """Parses the specified xml declaration tag to find the encoding version
    that is specified in it. If no encoding attribute exists, ASCII is
    returned as the default value.
    """
    search_text = "encoding="
    encoding_index = declaration.find(search_text)

    if encoding_index > -1:
        value = declaration[encoding_index + len(search_text):]
        quote_type = value[0]

        return value.split(quote_type)[1]

    return 'ASCII'


def parse_xml_to_tree(xml):
    """Parses the specified xml contents into an abstract syntax tree.
    The contents will be coerced into byte form if it is not already a
    bytestring.
    """
    declaration = get_xml_declaration(xml)
    encoding = get_encoding_from_declaration(declaration)

    xml_as_bytes = force_bytes(xml, encoding=encoding)
    parser = etree.XMLParser(strip_cdata=False)
    return etree.fromstring(xml_as_bytes, parser)


def get_siblings_before_root(root):
    """Gets a list of root level non-content nodes that are siblings
    of the root, and appear before the root. The items in the list are
    formatted as strings.
    """
    root_level_siblings = []

    root_level_it = root.getprevious()
    while root_level_it is not None:
        formatted_element = format_element(root_level_it, 0)
        root_level_siblings.insert(0, formatted_element)

        root_level_it = root_level_it.getprevious()

    return root_level_siblings


def get_siblings_after_root(root):
    """Gets a list of root level non-content nodes that are siblings
    of the root, and appear after the root. The items in the list are
    formatted as strings.
    """
    root_level_siblings = []

    root_level_it = root.getnext()
    while root_level_it is not None:
        formatted_element = format_element(root_level_it, 0)
        root_level_siblings.append(formatted_element)

        root_level_it = root_level_it.getnext()

    return root_level_siblings


def get_formatted_tree(root, keep_text_on_same_line=False):
    """Gets the contents of the specified XML abstract syntax tree formatted
    with proper indentation.
    """
    siblings_before_root = get_siblings_before_root(root)
    siblings_after_root = get_siblings_after_root(root)

    return '\n'.join(siblings_before_root) \
        + format_element(
            root, keep_text_on_same_line=keep_text_on_same_line) \
        + '\n'.join(siblings_after_root)


def prettify_xml(xml, keep_text_on_same_line=False):
    """Prettifies the specified xml contents, creating consistently nested
    tags and content.
    """
    if not xml:
        return ''

    root = parse_xml_to_tree(xml)

    declaration = get_xml_declaration(xml)
    formatted_contents = get_formatted_tree(root, keep_text_on_same_line)

    if declaration:
        return declaration + '\n' + formatted_contents

    return formatted_contents


def remove_empty_lines_from_html(html_contents):
    """Removes empty content from the specified HTML."""
    contents = html_contents.replace('<span></span>', '')
    if contents.endswith('\n'):
        contents = contents[:-1]

    return contents


def render_xml_as_html(xml, keep_text_on_same_line=False):
    """Converts the specified xml into syntax-highlighted HTML, with proper
    escaping of the contents according to html requirements.
    """
    pretty_contents = prettify_xml(xml, keep_text_on_same_line)

    html_contents = highlight(pretty_contents, XmlLexer(), HtmlFormatter())

    return html_contents


def iter_htmlified_xml_lines(html):
    """Iterates through each line in the specified html contents. Yields
    each line wrapped by <pre> tags.
    """
    for line in html.split('\n'):
        if line.strip():
            yield '<pre>%s</pre>' % line


class XMLReviewUI(TextBasedReviewUI):
    """A Review UI for XML files.

    This renders the XML to HTML, and allows users to comment on each
    tag and property value.
    """
    supported_mimetypes = ['application/xml', 'text/xml']
    object_key = 'xml'
    can_render_text = True

    extra_css_classes = ['xml-review-ui']

    js_model_class = 'RB.XMLBasedReviewable'
    js_view_class = 'RB.XMLReviewableView'

    def generate_render(self):
        try:
            with self.obj.file as f:
                f.open()
                contents = f.read()
                rendered = render_xml_as_html(contents)

            for line in iter_htmlified_xml_lines(rendered):
                yield line
        except Exception as e:
            logging.error('Failed to parse resulting XML HTML for '
                          'file attachment %d: %s',
                          self.obj.pk, e,
                          exc_info=True)
            yield _('Error while rendering XML content: %s') % e

    def get_source_lexer(self, filename, data):
        return XmlLexer()
