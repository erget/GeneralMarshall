'''
Created on Apr 16, 2013
@author: Daniel Lee, DWD
'''

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
import os


class SkyQuery:
    """
    A SKY query. This class is designed for use with request collections
    containing one single read request, containing a select element with one
    category, one reference date and one field, and a transfer element with one
    file.

    Dates should be specified in the form of YYYYMMDDHH.

    The class works extensively with getters and setters in order to maintain
    close ties with the XML document it contains.

    Missing fields are returned as an empty string rather than as an error.
    This is on purpose,
    """
#==============================================================================
# Data
#==============================================================================

    category_paths = {"/Routine/Local Model/COSMO 3 DE/Main Run/Forecast":
                      "c3_main_fc_rout"}

#==============================================================================
# Reserved methods
#==============================================================================

    def __init__(self, xml):
        self.source_file = xml
        self.tree = etree.parse(self.source_file)
        self.root = self.tree.getroot()
        self.NS = "{" + self.root.nsmap[None] + "}"

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
        return 'SkyQuery("{}")'.format(self.source_file)

    def __getattr__(self, key):
        """
        Getters are used here in order to ensure that the simple fields exposed
        to the user are synchronized with the internally stored XML elements
        """
        if key == "read_element":
            return self.tree.findall("//{NS}read".format(NS=self.NS))[0]
        if key == "database":
            return self.read_element.attrib["database"]
        if key == "select_element":
            return self.tree.findall("//{NS}select".format(NS=self.NS))[0]
        if key == "category":
            return self.select_element.attrib["category"]
        if key == "reference_date_element":
            val = self.tree.findall("//{NS}referenceDate".format(NS=self.NS))
            return val[0]
        if key == "reference_date":
            return self.reference_date_element.getchildren()[0].text
        if key == "field_elements":
            return self.tree.findall("//{NS}field".format(NS=self.NS))
        if key == "field":
            return self.find_field_element_text("PARAMETER_SHORTNAME")
        if key == "ensemble_member":
            return self.find_field_element_text("ENSEMBLE_MEMBER")
        if key == "forecast_time":
            return self.find_field_element_text("FORECAST_TIME")
        if key == "station_number":
            raise NotImplementedError
        if key == "file_element":
            return self.tree.findall("//{NS}file".format(NS=self.NS))[0]
        if key == "file":
            return self.file_element.attrib["name"]
        else:
            err_str = "SkyQuery instance has no attribute '{}'".format(key)
            raise AttributeError(err_str)

    def find_field_element_text(self, name):
        """Finds text of field element

        @param name: Name of field element to find text of
        @return: Element's text
        @rtype: String
        """
        try:
            return self.find_field_element(name).getchildren()[0].text
        except AttributeError:
            return ""

#==============================================================================
# Setters
#==============================================================================

    def __setattr__(self, name, value):
        """
        Setters are used for the same reason as the getters - to ensure that
        what the user sets is reflected in the object's internal XML elements
        """
        if name == "database":
            self.read_element.attrib[name] = value
        if name == "category":
            self.select_element.attrib[name] = value
        if name == "reference_date":
            self.reference_date_element.getchildren()[0].text = value
        if name == "field":
            self.set_field_element_text("PARAMETER_SHORTNAME", value)
        if name == "ensemble_member":
            self.set_field_element_text("ENSEMBLE_MEMBER", value)
        if name == "forecast_time":
            self.set_field_element_text("FORECAST_TIME", value)
        if name == "station_number":
            raise NotImplementedError
        if name == "file":
            self.file_element.attrib["name"] = value
        else:
            self.__dict__[name] = value

    def set_field_element_text(self, name, value):
        """Sets field element text to value

        @param name: The field element whose text is to be set
        @type name: String
        @param value: The text value to be entered for the field
        @type value: String
        """
        self.find_field_element(name).getchildren()[0].text = value

#==============================================================================
# Object methods
#==============================================================================

    def find_field_element(self, name):
        """Find a field element of a certain name

        @param name: Name of the element to return
        @type name: String
        @return: Element with matching name
        @rtype: XML element
        """
        for element in self.field_elements:
            if element.attrib["name"] == name:
                return element

    def generate_output_name(self):
        """
        Generate output names from the data source, fields queried and
        reference date.
        """
        ensemble_member = self.ensemble_member
        forecast_time = self.forecast_time
        if self.ensemble_member:
            ensemble_member = "m{}".format(ensemble_member.zfill(3))
        if forecast_time:
            forecast_time = "lfff{}0000".format(forecast_time.zfill(4))

        output = os.path.join(self.reference_date,
                              ensemble_member,
                              self.field,
                              forecast_time)
        return output

#==============================================================================
# Side effects
#==============================================================================

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

    def query(self):
        """Performs the query with SKY"""
        os.system("echo '{}' | sky".format(str(self)))
