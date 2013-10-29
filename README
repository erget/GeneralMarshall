=====================
About GeneralMarshall
=====================

``GeneralMarshall`` is a package for manipulating XML. It is comprised of an
abstract class that should be subclassed for usage.

*******
License
*******

``GeneralMarshall`` is released under the GNU Greater Public License. Feel free
to reuse or distribute it in any way you see fit. I would appreciate
`being notified <Daniel.Lee@dwd.de>`_ if you use the library and/or have any
feature requests or suggestions.

*****
Usage
*****

The class makes extensive use of an overriden ``__getattr__`` and
``__setattr__`` in order to allow XML tag values to be set with a pythonic
programming interface. In order to make this possible, the XML file's tag
heirarchy must be defined in the subclass that implements ``GeneralMarshall``.
This is done by setting the private class attributes ``_namespace``,
``_root_name``, ``_unique_tags``, ``_unique_tag_attributes`` and
``_tag_hierarchy``.

When the subclass knows the possible structure of XML files it should use, the
interaction can look like this::

    import general_marshall
    class MyXML(general_marshall.XML):
        ...
    
    # Load XML file
    xml_object = MyXML("file_name.xml")
    # Print pretty printed XML to stdout
    print(xml_object)
    # Create empty XML object
    new_xml = MyXML()
    # Set a tag value, creating parent nodes if necessary
    new_xml.value = "something"
    # Export to file
    new_xml.export("output_file.xml")
    
Although ``lxml`` is used to interface with the XML file that is either read or
created, not all of the functions that ``GeneralMarshall`` would profit from
``lxml`` most are used in order to maintain compatibility with Python's builtin
``xml`` library. This is due to the fact that ``GeneralMarshall`` is used in
some places where ``lxml`` is not available.

**********
Versioning
**********
Version numbers are set using `Semantic Versioning <http://semver.org>`_.
