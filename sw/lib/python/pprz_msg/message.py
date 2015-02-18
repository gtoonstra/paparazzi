"""
Paparazzi message representation

"""

from __future__ import print_function
import sys
import json
import messages_xml_map


class PprzMessageError(Exception):
    def __init__(self, message, inner_exception=None):
        self.message = message
        self.inner_exception = inner_exception
        self.exception_info = sys.exc_info()
    def __str__(self):
        return self.message


class PprzMessage(object):
    """base Paparazzi message class"""
    def __init__(self, class_name, name):
        self._class_name = class_name
        self._name = name
        self._id = messages_xml_map.get_msg_id(class_name, name)
        self._fieldnames = messages_xml_map.get_msg_fields(class_name, name)
        self._fieldtypes = messages_xml_map.get_msg_fieldtypes(class_name, self._id)
        self._fieldvalues = []
        # set empty values according to type
        for t in self._fieldtypes:
            if t == "char[]":
                self._fieldvalues.append('')
            elif '[' in t:
                self._fieldvalues.append([0])
            else:
                self._fieldvalues.append(0)

    def get_msgname(self):
        return self._name

    def get_classname(self):
        return self._class_name

    def get_fieldnames(self):
        return self._fieldnames

    def get_fieldvalues(self):
        return self._fieldvalues

    def get_field(self, idx):
        return self._fieldvalues[idx]

    def set_values(self, values):
        if len(values) == len(self._fieldnames):
            self._fieldvalues = values
        else:
            raise PprzMessageError("Error: fields not matching")

    def __str__(self):
        ret = '%s.%s {' % (self._class_name, self._name)
        for idx, f in enumerate(self._fieldnames):
            ret += '%s : %s, ' % (f, self._fieldvalues[idx])
        ret = ret[0:-2] + '}'
        return ret

    def to_dict(self, payload_only=False):
        d = {}
        if not payload_only:
            d['msgname'] = self._name
            d['msgclass'] = self._class_name
        for idx, f in enumerate(self._fieldnames):
            d[f] = self._fieldvalues[idx]
        return d

    def to_json(self, payload_only=False):
        return json.dumps(self.to_dict(payload_only))

    def payload_to_ivy_string(self):
        ivy_str = ''
        for idx, t in enumerate(self._fieldtypes):
            if "char[" in t:
                ivy_str += '"' + self._fieldvalues[idx] + '"'
            elif '[' in t:
                ivy_str += ','.join([str(x) for x in self._fieldvalues[idx]])
            else:
                ivy_str += str(self._fieldvalues[idx])
            ivy_str += ' '
        return ivy_str

def test():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="path to messages.xml file")
    parser.add_argument("-c", "--class", help="message class", dest="msg_class", default="telemetry")
    args = parser.parse_args()
    messages_xml_map.parse_messages(args.file)
    messages = [PprzMessage(args.msg_class, n) for n in messages_xml_map.get_msgs(args.msg_class)]
    print("Listing %i messages in '%s' msg_class" % (len(messages), args.msg_class))
    for msg in messages:
        print(msg)

if __name__ == '__main__':
    test()

