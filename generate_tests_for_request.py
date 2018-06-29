#!/usr/bin/env python3
import subprocess
import json

tests = []
properties = []

class Property:
        def __init__(self, path, value):
            self.path = path
            self.value = value
            self.type = str(type(value)).split("'")[1::2][0]

        @property
        def parent(self):
            """ Return the parent of the key """
            return self.path.split('.')[-2]

        @property
        def key(self):
            return self.path.split('.')[-1]

        def __str__(self):
            return self.path + ': ' + self.write_test() + "\n"

        def __repr__(self):
            return self.__str__()

        def get_type_test(self):
            if self.type == 'int':
                return 'tests["{}"] = typeof {} == "{}";'.format(self.path, self.path, 'number')

            if self.type == 'str':
                return 'tests["{}"] = typeof {} == "{}";'.format(self.path, self.path, 'string')

            if self.type == 'list':
                return 'tests["{}"] = Array.isArray({});'.format(self.path, self.path)

            if self.type == 'bool':
                return 'tests["{}"] = typeof {} == "{}";'.format(self.path, self.path, 'boolean')

            if self.type == 'NoneType':
                return 'tests["{}"] = {} === null || {}.hasOwnProperty({});'.format(self.path, self.path, self.parent, self.key)

            return

        def get_value_test(self):
            if self.type == 'int':
                return 'tests["{}"] = {} === {};'.format(self.path, self.path, self.value)

            if self.type == 'str':
                if not self.value:
                    return
                return 'tests["{}"] = {} == "{}";'.format(self.path, self.path, self.value)

            if self.type == 'list':
                tests = []
                for v in self.value:
                    tests.append('tests["{}"] = {}.includes({});'.format(self.path, self.path, v))
                return "\n".join(tests)

            if self.type == 'bool':
                return 'tests["{}"] = {} === {};'.format(self.path, self.path, str(self.value).lower())

            return


def main():
    global tests
    global properties

    tests = []
    properties = []
    status = input("What is the expected status? (optional)\n")
    if not status:
        status = 200

    tests.append('tests["status is {0}"] = responseCode.code === {0};'.format(status))
    tests.append("\n")
    user_input = subprocess.check_output(['pbpaste'])
    try:
        input_json = json.loads(user_input)
    except (json.decoder.JSONDecodeError):
        print('Invalid json.')
        return

    tests.append("data = JSON.parse(responseBody);\n")

    # if json is list
    # write tests for first object
    if isinstance(input_json, list):
        traverse_properties(input_json[0], 'data[0]')

    # json is object
    else:
        traverse_properties(input_json)

    type_tests = [p.get_type_test() for p in properties if p.get_type_test()]
    value_tests = [p.get_value_test() for p in properties if p.get_value_test()]


    user_input = input("Type tests? (y/n)\n")
    if not 'n' in user_input:
        tests.append("// Type tests")
        tests.extend(type_tests)


    user_input = input("Value tests? (y/n)\n")
    if not 'n' in user_input:
        tests.append("\n// Value tests")
        tests.extend(value_tests)

    write_to_clipboard("\n".join(tests))
    print("The tests are in your clipboard.")



def traverse_properties(node, path='data'):
    global properties
    for item in node.items():
        key, value = item
        try:
            traverse_properties(value, path + '.' + key)
        except:
            prop = Property(path + '.' + key, value)
            properties.append(prop)


def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))

if __name__ == '__main__':
    done = False
    while not done:
        main()
        again = input("Again? (y/n)\n")
        if 'n' in again.lower():
            done = True
