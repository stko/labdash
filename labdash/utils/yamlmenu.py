import os
import glob
#import collections

import oyaml
from ldmclass import LDMClass

class YAMLMenu:
    ''' Helper class to build the content out of a nested yaml file definition instead if hardcode everything'''


    # https://gist.github.com/angstwad/bf22d1822c38a92ec0a9

    def dict_merge(self, dct, merge_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k in merge_dct:
            if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict)):  #noqa
                self.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]


    def __init__(self, ui: LDMClass, yaml_file_or_path: str):
        self.ui=ui
        self.menu_structure={}
        if os.path.isdir(yaml_file_or_path):
            for file_name in glob.glob(yaml_file_or_path+"/*.yaml"):
                with open(file_name, encoding="utf8") as fin:
                    self.dict_merge(self.menu_structure, oyaml.load(fin, Loader=oyaml.Loader))
        else:
            with open(yaml_file_or_path, encoding="utf8") as fin:
                self.menu_structure = oyaml.load(fin, Loader=oyaml.Loader)
        print(self.menu_structure)
        self.menu_structure["_parent"] = None
        self.build_metadata(self.menu_structure, None)

    
    def has_submenu(self, menu_item):
        """returns submenu if the menu item contains another submenu"""
        if not isinstance(menu_item, dict):
            return False
        # tricky: a submenu can be found in the second nested level, if any
        for key, value in menu_item.items():
            if key[0] != "_" and isinstance(value, dict):
                return  True
        return False

    def build_metadata(self, menu_item: dict,  parent: dict):
        """adds internal properties
        
        returns true if the item contains submenus"""
        for key,value in menu_item.items():
            if isinstance(value, dict):
                self.build_metadata(value,  menu_item)
                value["_is_menu"] = self.has_submenu(value)
                value["_parent"] = parent
                value["_name"] = key


    def get_menu_id(self,menu_item:dict):
        """calculates the string representation of the sub menu element"""
        menu_id=menu_item["_name"]
        parent=menu_item["_parent"]
        while parent:
            menu_item=menu_item["_parent"]
            menu_id=menu_item["_name"]+"%%"+menu_id
            parent=menu_item["_parent"]
        return menu_id


    def create_menu(self,  oldvalue:str, id:str):
        """displays the (sub-) menu identified by the menu_id"""
        elements=id.split("%%",)
        sub_menu=self.menu_structure
        if id:
            for key in elements:
                sub_menu=sub_menu[key]
        if "_title" in sub_menu:
            title=sub_menu["_title"]
        else:
            title=elements[-1]
        self.ui.openPage(title)
        for key,element in sub_menu.items():

            if key[0] != "_":
                if "_is_menu" in element and element["_is_menu"]:
                    self.ui.addElement(
                        element["_title"],
                        "create_menu",
                        "->",
                        0,
                        self.get_menu_id(element),
                    )
                else:
                    self.ui.addElement(
                        key,
                        "get_value",
                        "-",
                        self.ui.VI_UPDATE | self.ui.VI_TIMER,
                        element["_format"],
                    )
        if id:
            self.ui.addElement("<-", "create_menu", "<-", self.ui.VI_BACK, "%%".join(elements[:-1]))
        self.ui.pageDone()
