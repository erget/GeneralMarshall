'''
Created on May 17, 2013
@author: Daniel Lee, DWD
'''

import logging
import os
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


class XML:
    """
    An XML file container.

    The XML structure is hidden from the user so that element content can be
    set as if it was a flat field. The hierarchy is stored in the class'
    fields. Missing fields are created when looked up.

    XML is designed as an abstract class. The fields necessary to use it should
    be set in subclasses.

    Fields:
        _namespace: The namespace the XML document should work in
        _root_name: The XML document's root tag
        _unique_tags: Unique tags that can occur in the document
        _unique_tag_attributes: Possible unique attributes that can be placed
                                on tags with the tag that should contain them.
                                Organized thusly:
                                    {attribute_identifier:
                                        (tag, xml_attribute_name)}
        _tag_hierarchy: A tag hierarchy organized as a dictionary. This is used
                        to place tags when they are generated. It is also used
                        to dynamically generate parent elements that may not
                        exist when creating child elements.
                        Organized thusly:
                            {tag_identifier: (parent, xml_tagname)}
                        Note:
                        After describing the field tags, this dictionary is
                        updated to contain the hierarchy of field tags, which
                        are all children of the unique select tag.

    Methods:
        get_or_create_tag
        __init__
        __str__
        __repr__
        __getattr__
        __setattr__
        generate_output_name
        export
        query
    """

    _namespace = None
    _root_name = None
    _unique_tags = None
    _unique_tag_attributes = None
    _tag_hierarchy = None

    def _get_or_create_tag(self, tag_name):
        """
        Get or create an tag.

        Check if parent exists. If needed, the call method recursively until
        all parent elements are created. The requested element is
        created, if necessary, and then returned.

        @param tag_name: The name of the element
        @param type: String
        """
        def get_or_create_field_tag(tag_name, elements):
            """
            Get or create a field tag.

            Scan elements and find any fields.
            If fields are found, check names to see if they match the queried
            tag.

            @param tag_name: Name of tag to be returned
            @param elements: Children of parent element
            @return: The correct field tag
            """
            logging.info("Element is a field, special case.")
            element = None
            field_elements = [x for x in elements if x.tag == "field"]
            logging.info("Found following field elements: "
                         "{}".format(field_elements))
            for tag in field_elements:
                # Check if tag has right name and if yes, return it.
                logging.info("Searching found elements "
                             "for {}.".format(tag_name))
                if tag.get("name") == self._field_tag_attribute_map[tag_name]:
                    element = tag
            logging.info("Returning {}.".format(element))
            return element

        # Does parent exist?
        parent_name = self._tag_hierarchy[tag_name][0]
        try:
            logging.info("Looking for {}'s parent.".format(tag_name))
            parent = self.__dict__[parent_name]
        # If not, create and retrieve parent
        except KeyError:
            logging.info("KeyError. Making parent {}.".format(parent_name))
            self.__dict__[parent_name] = self._get_or_create_tag(parent_name)
            parent = self.__dict__[parent_name]
        # Check if element exists
        child_name = self._tag_hierarchy[tag_name][1]
        logging.info("Parent {} exists. "
                     "{}'s XML name is {}.".format(parent,
                                                   tag_name,
                                                   child_name))
        elements = parent.getchildren()
        element = None
        if child_name == "field":
            element = get_or_create_field_tag(tag_name, elements)

        # If children are found and element child element is not found field
        if elements and child_name != "field":
            logging.info("{} has children: {}. "
                         "element={}".format(parent, elements, element))
            # Check if I can find the element the easy way
            element = parent.find(child_name)
            if element is not None:
                logging.info("Found tag the easy way. "
                             "It's {}.".format(element))
                return element
            # Otherwise search for it with full namespace
            else:
                element = parent.find("{ns}{element}".
                                      format(ns=self.ns, element=child_name))
                logging.info("Found tag with namespace. "
                             "It's {}.".format(element))
        # If I found the element, return it
        if element is not None:
            logging.info("Found tag. It's {}.".format(element))
            return element

        # Otherwise create it
        element_name = self._tag_hierarchy[tag_name][1]
        logging.info("Creating {} as {}.".format(tag_name, element_name))
        tag = etree.SubElement(parent, child_name)
        # If it's a field element, set its name
        if child_name == "field":
            tag.set("name", self._field_tag_attribute_map[tag_name])
        return tag

#==============================================================================
# Reserved methods
#==============================================================================

    def __init__(self, xml=""):
        """Parse input XML file. If none is provided, make XML structure."""
        if xml:
            self.source_file = xml
            self.tree = etree.parse(self.source_file)
            self.root = self.tree.getroot()
        else:
            self.source_file = ""
            self.root = etree.Element(self._root_name,
                                      nsmap={None: self._namespace})
            self.tree = etree.ElementTree(self.root)
            self.reference_date = ""
        self.ns = "{" + self.root.nsmap[None] + "}"

    def __str__(self):
        """
        The query string has to use single quotation marks in the first line,
        otherwise the parser used in SKY rejects it.
        """
        string = etree.tostring(self.root,
                                xml_declaration=True,
                                encoding="UTF-8",
                                pretty_print=True,
                                standalone=True)
        lines = string.splitlines()
        lines[0] = (lines[0].replace("'", '"'))
        return "\n".join(lines)

    def __repr__(self):
        return 'XML("{}")'.format(self.source_file)

    def __getattr__(self, key):
        """
        Getters are used here in order to ensure that the simple fields exposed
        to the user are synchronized with the internally stored XML elements
        """

        err_str = "SkyQuery instance has no attribute '{}'".format(key)

        if key == "reference_date":
            return self._get_or_create_tag("reference_date_value").text

        # If key is field tag, set the name
        if key in self._field_tag_identifiers:
            tag = self._get_or_create_tag(key)
            field_name = self._field_tag_identifiers[key][1]
            tag.set("name", field_name)
            return tag

        # If key is in field hierarchy, get it or create it
        if key in self._tag_hierarchy:
            return self._get_or_create_tag(key)

        # If key is attribute, get attribute value
        if key in self._unique_tag_attributes:
            tag_name = self._unique_tag_attributes[key][0]
            parent_tag = self._get_or_create_tag(tag_name)
            logging.info("{} is a tag attribute that belongs to tag {}"
                         ".".format(key, parent_tag))
            attribute = parent_tag.get(key)
            return attribute

        elif key == "field_tag_names":
            return self.select_element.findall("field")

        # If key refers to field attribute, return that tag's value text
        if key in self._field_tag_names:
            value_tag, attribute_text = self._field_tag_names[key]
            logging.info("{} is a field tag attribute with attribute text "
                         "{}. ".format(key, attribute_text))
            logging.info("Its value is stored in tag "
                         "{}.".format(value_tag))
            return self._get_or_create_tag(value_tag).text

        raise AttributeError(err_str)

#==============================================================================
# Setters
#==============================================================================

    def __setattr__(self, name, value):
        """
        Setters are used for the same reason as the getters - to ensure that
        what the user sets is reflected in the object's internal XML elements

        If field is known as a special case, it is assigned using the setter.
        Otherwise it is assigned normally as an object field.

        @param name: Name of attribute to be set
        @type name: String
        @param value: Value to be assigned
        """
        def set_field_element_text(name, value):
            """Sets field element text to value

            @param name: The field element whose text is to be set
            @type name: String
            @param value: The text value to be entered for the field
            @type value: String
            """
            field_element = self.find_field_tag(name)
            if field_element is not None:
                self._get_or_create_tag(field_element,
                                       "value").text = value
            else:
                etree.SubElement(self.select_element, "field").set("name",
                                                                   name)
                set_field_element_text(name, value)

        # name should be a tag attribute
        if name in self._unique_tag_attributes:
            tag_name = self._unique_tag_attributes[name][0]
            logging.info("{} is an attribute of {} tag.".format(name,
                                                                tag_name))
            tag = self._get_or_create_tag(tag_name)
            tag.set(self._unique_tag_attributes[name][1], value)

        # This is setting the field's value, rather than setting the value of
        # the value tag beneath the field.
        # Name is a field tag
        if name in self._field_tag_names:
            value_tag = self._field_tag_names[name][0]
            logging.info("{} is a field tag with tag name "
                         "{}.".format(name,
                                      value_tag))
            value_tag = self._get_or_create_tag(value_tag)
            logging.info("Value tag is {}. "
                         "Setting value to {}.".format(value_tag,
                                                       value))
            value_tag.text = value
#             set_field_element_text(self.field_tag_names[name], value)

        if name == "reference_date":
            self.reference_date_value.text = value
        else:
            self.__dict__[name] = value

    def export(self, path):
        """Writes query to XML file

        @param path: An output path
        """

        if os.path.isfile(path):
            overwrite = ""
            while overwrite != "y" and overwrite != "n":
                prompt = "File already exists. Overwrite? (y/n)\n"
                overwrite = raw_input(prompt)
                overwrite = overwrite.lower()
            if overwrite == "n":
                print("Please enter a new file name.")
                return

        with open(path, "w") as output_file:
            output_file.write(str(self))

# Show log info messages if desired
logging.basicConfig(format="%(message)s", level=logging.INFO)
