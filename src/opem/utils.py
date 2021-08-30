import collections
import csv
from dataclasses import asdict, dataclass
from typing import DefaultDict, List
import codecs

import pkg_resources


def fill_calculated_cells(target_table_ref, func_to_apply, included_rows=[], included_cols=[], excluded_rows=[], excluded_cols=[], other_tables_keymap={}, other_table_refs=None):
    print("in calc function")
    print(included_cols)
    if (included_rows and excluded_rows):
        raise ValueError(
            "Please only pass arguments for one of excluded_rows/included_rows, not both")
    if (included_cols and excluded_cols):
        raise ValueError(
            "Please only pass arguments for one of excluded_cols/included_cols, not both")

    # handle included rows/ cols as well
    for row_key, row in target_table_ref.items():
        # skip label for the row index and full table name and
        if row_key not in ["row_index_name", "full_table_name"] \
                and (not excluded_rows or (row_key not in excluded_rows)) and (not included_rows or (row_key in included_rows)):
            # handle column that needs special treatment
            for col_key in row.keys():
                print(col_key)
                print(included_cols)
                print(col_key in included_cols)
                if (not excluded_cols or (col_key not in excluded_cols)) and (not included_cols or (col_key in included_cols)):
                    # get a reference to current cell and write calculated value
                    print(row[col_key])
                    row[col_key] = func_to_apply(
                        row_key, col_key, target_table_ref, other_table_refs, other_tables_keymap)
                    print(row[col_key])


def build_dict_from_defaults(table_name):
    table_array = read_model_table_defaults(table_name)
    dict = {}
    headers = table_array[0]
    dict["full_table_name"] = table_name
    dict['row_index_name'] = headers[0]
    for row in table_array[1:]:
        if row[0] != '':
            print(table_name)
            print(row)
            dict[row[0]] = {k: float(v)
                            for (k, v) in filter(lambda x: True if (x[0] != '' and x[1] != '') else False, zip(headers[1:], row[1:]))}
    return dict


def read_model_table_defaults(table_name):
    rows_and_header = []
    csvfile = pkg_resources.resource_stream(
        "opem.defaults", f"{table_name}.csv")
    # if only 'utf-8' is specified then BOM character '\ufeff' is included in output
    utf8_reader = codecs.getreader("utf-8-sig")

    print("no error in with")
    print(type(csvfile))
    reader = csv.reader(utf8_reader(csvfile))
    print("no error after reader")
    for row in reader:
        rows_and_header.append(row)
    return rows_and_header


def visit_dict(d, path=[]):
    for k, v in d.items():
        if not isinstance(v, dict):
            yield path + [k], v
        else:
            yield from visit_dict(v, path + [k])


def initialize_from_dataclass(target, source: DefaultDict):
    # this allows us to get input from a dict generated from another dataclass
    for key in source.keys():
        if key in asdict(target).keys():

            for path in visit_dict(source[key]):
                # print(user_input[key])

                if len(path[0]) == 1:
                    print('path length = 1')
                    print(source[key])
                    setattr(target, key, source[key][path[0]])
                else:

                    keys_length = len(path[0]) - 1
                # get a reference to the object the holds the key/value pair we want to mutate
                    ref = nested_access(
                        dict=getattr(target, key), keys=path[0][0:keys_length])

                    ref[path[0][-1]] = path[-1]


def nested_access(dict, keys):
    for key in keys:
        dict = dict[key]
    return dict


def initialize_from_list(target, source: List):
    # this allows us to get input from csv

    for row in source:
        if row[0] in asdict(target).keys():
            if len(row) == 2:
                setattr(target, row[0], row[1])
            else:
                print('keys from input row')
                print(row[1:-2])
                # get a reference to the object the holds the key/value pair we want to mutate
                ref = nested_access(
                    dict=getattr(target, row[0]), keys=row[1:-2])
                ref[row[-2]] = row[-1]


######################### NOT USED #######################


def isDict(d):
    return isinstance(d, collections.Mapping)


def isAtomOrFlat(d):
    return not isDict(d) or not any(isDict(v) for v in d.values())


def leafPaths(nestedDicts, noDeeper=isAtomOrFlat):
    """
        For each leaf in NESTEDDICTS, this yields a 
        dictionary consisting of only the entries between the root
        and the leaf.
    """
    for key, value in nestedDicts.items():
        if noDeeper(value):
            yield {key: value}
        else:
            for subpath in leafPaths(value):
                yield {key: subpath}
###########################################################