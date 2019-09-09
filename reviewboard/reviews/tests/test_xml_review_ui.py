# -*- coding: utf-8 -*-

from reviewboard.reviews.ui.xmlui import (
    get_xml_declaration,
    parse_xml_to_tree,
    get_attributes_str,
    format_empty_element_tag,
    format_element_with_text,
    format_element_with_children,
    prettify_xml,
    render_xml_as_html,
    is_comment_element,
    get_encoding_from_declaration,
    get_siblings_before_root,
    get_siblings_after_root,
    parse_text_from_element_source)

from reviewboard.testing import TestCase


def get_encoding_string(encoding):
    return " encoding='%s'" % encoding


class XmlUiTests(TestCase):
    """Unit tests for reviewboard.reviews.ui.xmlui."""

    def parse_tree_and_validate(self, encoding=None, content=''):
        if encoding is None:
            encoding_string = get_encoding_string('ASCII')
        else:
            encoding_string = get_encoding_string(encoding)

        xml_contents = "<?xml version='1.0'%s?>\n<root>%s</root>" % (
            encoding_string, content)

        root = parse_xml_to_tree(xml_contents)
        parsed_string = format_element_with_text(root, 0)
        expected_string = u'<root>\n    %s\n</root>\n' % (content)

        self.assertEqual(parsed_string, expected_string)

    def test_get_xml_declaration_no_declaration(self):
        """Testing get_xml_declaration with no declaration tag in the xml"""
        xml_contents = '<root></root>'

        declaration = get_xml_declaration(xml_contents)
        self.assertEqual(declaration, '')

    def test_get_xml_declaration_with_declaration(self):
        """Testing get_xml_declaration with a declaration tag in the xml"""
        expected_declaration = '<?xml version="1.0"?>'
        xml_contents = expected_declaration + '<root></root>'

        declaration = get_xml_declaration(xml_contents)
        self.assertEqual(declaration, expected_declaration)

    def test_get_xml_declaration_with_declaration_on_separate_line(self):
        """Testing get_xml_declaration with a declaration tag in the xml
            that is on a different line from the actual contents
        """
        expected_declaration = '<?xml version="1.0"?>'
        xml_contents = expected_declaration + '\n<root></root>'

        declaration = get_xml_declaration(xml_contents)
        self.assertEqual(declaration, expected_declaration)

    def test_parse_xml_to_tree_default_encoding(self):
        """Testing parse_xml_to_tree with no encoding specified"""
        self.parse_tree_and_validate(content='test parsing default')

    def test_parse_xml_to_tree_utf8_encoding(self):
        """Testing parse_xml_to_tree with utf8 encoding specified"""
        self.parse_tree_and_validate('UTF-8', u'¢')

    def test_parse_xml_to_tree_utf16_encoding(self):
        """Testing parse_xml_to_tree with utf16 encoding specified"""
        self.parse_tree_and_validate('UTF-16', u'€')

    def test_get_encoding_from_declaration_no_encoding(self):
        declaration = '<?xml version="1.0">'

        encoding = get_encoding_from_declaration(declaration)

        self.assertEqual(encoding, 'ASCII')

    def test_get_encoding_from_declaration_utf16(self):
        declaration = '<?xml version="1.0" encoding="UTF-16">'

        encoding = get_encoding_from_declaration(declaration)

        self.assertEqual(encoding, 'UTF-16')

    def test_get_attributes_str_no_attributes(self):
        """Testing get_attributes_str when an element has no attributes"""
        root = parse_xml_to_tree('<root/>')

        attributes = get_attributes_str(root)

        self.assertEqual(attributes, '')

    def test_get_attributes_str_with_one_attribute(self):
        """Testing get_attributes_str when an element has one attribute"""
        root = parse_xml_to_tree('<root test_key="test_value" />')

        attributes = get_attributes_str(root)

        self.assertEqual(attributes, 'test_key="test_value"')

    def test_get_attributes_str_with_single_quotes(self):
        """Testing get_attributes_str when single quotes are used"""
        root = parse_xml_to_tree('<root test_key=\'test_value\' />')

        attributes = get_attributes_str(root)

        self.assertEqual(attributes, 'test_key="test_value"')

    def test_get_attributes_str_with_multiple_attributes(self):
        """Testing get_attributes_str when an element has attributes"""
        root = parse_xml_to_tree('<root test_key="value" int_key="999" />')

        attributes = get_attributes_str(root)

        self.assertEqual(attributes, 'test_key="value" int_key="999"')

    def test_format_empty_element_tag_no_attributes(self):
        """Testing format_empty_element_tag with no attributes"""
        root = parse_xml_to_tree('<root />')

        formatted_string = format_empty_element_tag(root, 2)

        self.assertEqual(formatted_string, '        <root />\n')

    def test_format_empty_element_tag_one_attribute(self):
        """Testing format_empty_element_tag with one attribute"""
        root = parse_xml_to_tree('<root key="value" />')

        formatted_string = format_empty_element_tag(root, 2)

        self.assertEqual(formatted_string, '        <root key="value" />\n')

    def test_format_empty_element_tag_no_indent(self):
        """Testing format_empty_element_tag with no indentation"""
        root = parse_xml_to_tree('<root />')

        formatted_string = format_empty_element_tag(root, 0)

        self.assertEqual(formatted_string, '<root />\n')

    def test_format_element_with_text_no_attributes(self):
        """Testing format_element_with_text with no attributes"""
        root = parse_xml_to_tree('<root>test text</root>')

        formatted_string = format_element_with_text(root, 2)

        self.assertEqual(formatted_string, """\
        <root>
            test text
        </root>
""")

    def test_format_element_with_text_same_line(self):
        """Testing format_element_with_text with content on the same line"""
        root = parse_xml_to_tree('<root>test text</root>')

        formatted_string = format_element_with_text(root, 2, True)

        self.assertEqual(formatted_string, '        <root>test text</root>\n')

    def test_format_element_with_multiline_text(self):
        """Testing format_element_with_text with multiline text"""
        root = parse_xml_to_tree('<root>test\ntext</root>')

        formatted_string = format_element_with_text(root, 2)

        self.assertEqual(formatted_string, """\
        <root>
            test
            text
        </root>
""")

    def test_format_element_with_text_prefixed_with_whitespace(self):
        """Testing format_element_with_text beginning with whitespace"""
        root = parse_xml_to_tree('<root>       test text</root>')

        formatted_string = format_element_with_text(root, 2)

        self.assertEqual(formatted_string, """\
        <root>
            test text
        </root>
""")

    def test_format_element_with_text_with_cdata(self):
        """Testing format_element_with_text when text includes data"""
        xml_contents = '<root>cdata<![CDATA[<test>Test CDATA</test>]]></root>'
        root = parse_xml_to_tree(xml_contents)

        formatted_string = format_element_with_text(root, 2)

        self.assertEqual(formatted_string, """\
        <root>
            cdata<![CDATA[<test>Test CDATA</test>]]>
        </root>
""")

    def test_format_element_with_text_one_attribute(self):
        """Testing format_element_with_text with one attribute"""
        root = parse_xml_to_tree('<root test_key="value">test text</root>')

        formatted_string = format_element_with_text(root, 2)

        self.assertEqual(formatted_string, """\
        <root test_key="value">
            test text
        </root>
""")

    def test_format_element_with_children_no_attributes(self):
        """Testing format_element_with_children with no attributes"""
        root = parse_xml_to_tree('<root><child /></root>')

        formatted_string = format_element_with_children(root, 2)

        self.assertEqual(formatted_string, """\
        <root>
            <child />
        </root>
""")

    def test_format_element_with_children_one_attribute(self):
        """Testing format_element_with_children with one attribute"""
        root = parse_xml_to_tree('<root test_key="value"><child /></root>')

        formatted_string = format_element_with_children(root, 2)

        self.assertEqual(formatted_string, """\
        <root test_key="value">
            <child />
        </root>
""")

    def test_get_siblings_before_root_no_siblings(self):
        """Testing get_siblings_before_root with no nodes before the root"""
        root = parse_xml_to_tree('<root></root><!-- after root -->')

        before_root = get_siblings_before_root(root)

        self.assertEqual(before_root, [])

    def test_get_siblings_before_root_with_siblings(self):
        """Testing get_siblings_before_root with nodes before the root"""
        root = parse_xml_to_tree('<!--first--><!--second--><root></root>')

        before_root = get_siblings_before_root(root)

        self.assertEqual(before_root, ['<!--first-->\n', '<!--second-->\n'])

    def test_get_siblings_after_root_no_siblings(self):
        """Testing get_siblings_after_root with no nodes after the root"""
        root = parse_xml_to_tree('<!-- before root --><root></root>')

        after_root = get_siblings_after_root(root)

        self.assertEqual(after_root, [])

    def test_get_siblings_after_root_with_siblings(self):
        """Testing get_siblings_after_root with nodes after the root"""
        root = parse_xml_to_tree('<root></root><!--first--><!--second-->')

        after_root = get_siblings_after_root(root)

        self.assertEqual(after_root, ['<!--first-->\n', '<!--second-->\n'])

    def test_prettify_xml_no_declaration(self):
        """Testing prettify_xml with no xml declaration tag"""
        xml = '<root test_key="test value"><child /></root>'

        formatted_string = prettify_xml(xml)

        self.assertEqual(formatted_string, """\
<root test_key="test value">
    <child />
</root>
""")

    def test_prettify_xml_with_external_dtd(self):
        """Testing prettify_xml with a doctype tag with external entities"""
        xml = '<?xml version="1.0"?>' \
            + '<!DOCTYPE root SYSTEM "pathTo.dtd">' \
            + '<root test_key="test value">' \
            + '<child /></root>'

        formatted_string = prettify_xml(xml)

        self.assertEqual(formatted_string, """\
<?xml version="1.0"?>
<!DOCTYPE root SYSTEM "pathTo.dtd">
<root test_key="test value">
    <child />
</root>
""")

    def test_prettify_xml_with_internal_dtd(self):
        """Testing prettify_xml with a doctype tag with internal entities"""
        xml = '<?xml version="1.0"?>' \
            + '<!DOCTYPE root [<!ELEMENT root (child)>' \
            + '<!ELEMENT child (#PCDATA)>]><root test_key="test value">' \
            + '<child /></root>'

        formatted_string = prettify_xml(xml)

        self.assertEqual(formatted_string, """\
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ELEMENT root (child)>
    <!ELEMENT child (#PCDATA)>
]>
<root test_key="test value">
    <child />
</root>
""")

    def test_prettify_xml_with_declaration(self):
        """Testing prettify_xml with an xml declaration tag"""
        xml = '<?xml version="1.0"?><root test_key="value"><child /></root>'

        formatted_string = prettify_xml(xml)

        self.assertEqual(formatted_string, """\
<?xml version="1.0"?>
<root test_key="value">
    <child />
</root>
""")

    def test_prettify_xml_with_empty_string(self):
        """Testing prettify_xml with an empty string passed in"""
        formatted_string = prettify_xml('')

        self.assertEqual(formatted_string, '')

    def test_prettify_xml_with_detailed_xml(self):
        """Testing prettify_xml with detailed xml"""

        xml = """\
<?xml version="1.0"?>
<!-- Test Comment 1-->
<test>
<!-- Test Comment 2-->
<fake>
    Not
    Real
    XML
            </fake>
    <h3 test="one" value="two">test</h3>
<div>test</div><xyz /><xyza />
<nestedroot>
    <realnest>
        Test nest
    </realnest>
    <wow></wow>
    <cdatatest><![CDATA[<sender>Example CDATA</sender>]]></cdatatest>
</nestedroot>
</test>
<!-- Test Comment 4-->
"""
        formatted_string = prettify_xml(xml)

        self.assertEqual(formatted_string, """\
<?xml version="1.0"?>
<!-- Test Comment 1-->
<test>
    <!-- Test Comment 2-->
    <fake>
        Not
            Real
            XML
    </fake>
    <h3 test="one" value="two">
        test
    </h3>
    <div>
        test
    </div>
    <xyz />
    <xyza />
    <nestedroot>
        <realnest>
            Test nest
        </realnest>
        <wow />
        <cdatatest>
            <![CDATA[<sender>Example CDATA</sender>]]>
        </cdatatest>
    </nestedroot>
</test>
<!-- Test Comment 4-->
""")

    def test_render_xml_as_html_double_quotes(self):
        """Testing render_xml_as_html escaping and prettifying xml"""
        xml = '<root test_key="test value"><child /></root>'

        formatted_string = render_xml_as_html(xml)

        self.assertEqual(formatted_string, u"""\
<span class="nt">&lt;root</span> \
<span class="na">test_key=</span><span class="s">&quot;test value&quot;\
</span><span class="nt">&gt;</span>
    <span class="nt">&lt;child</span> <span class="nt">/&gt;</span>
<span class="nt">&lt;/root&gt;</span>
""")

    def test_render_xml_as_html_single_quotes(self):
        """Testing render_xml_as_html escaping single quotes"""
        xml = '<root test_key=\'test value\'><child /></root>'

        formatted_string = render_xml_as_html(xml)

        self.assertEqual(formatted_string, u"""\
<span class="nt">&lt;root</span> \
<span class="na">test_key=</span><span class="s">&quot;test value&quot;\
</span><span class="nt">&gt;</span>
    <span class="nt">&lt;child</span> <span class="nt">/&gt;</span>
<span class="nt">&lt;/root&gt;</span>
""")

    def test_is_comment_element_with_comment(self):
        """Testing is_comment_element with an element being a comment"""
        xml_contents = '<root><!-- Test Comment --></root>'
        tree_root = parse_xml_to_tree(xml_contents)
        element_node = tree_root.getchildren()[0]

        comment = is_comment_element(element_node)
        self.assertTrue(comment)

    def test_is_comment_element_with_normal_tag(self):
        """Testing is_comment_element with an non-comment element"""
        xml_contents = '<notAComment></notAComment>'
        tree_root = parse_xml_to_tree(xml_contents)

        comment = is_comment_element(tree_root)
        self.assertFalse(comment)

    def test_parse_text_from_element_source(self):
        """Testing parse_text_from_element_source returning the text"""
        xml_contents = b'<root><![CDATA[<root>Test CDATA</root>]]></root>'

        parsed_contents = parse_text_from_element_source('root', xml_contents)

        self.assertEqual(
            parsed_contents, '<![CDATA[<root>Test CDATA</root>]]>')
