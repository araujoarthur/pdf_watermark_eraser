
from pathlib import Path
import json

class RedactionPlan:
    _root_mode: str
    _folder_mode: str
    _delete_original: bool
    _continue_even_if_exists: bool
    _root_input_path: Path
    _output_path: Path
    _disallowed_folders: list[str]
    _redaction_texts: list[str]

    def __init__(self, plan_path):
        if plan_path:
            self._read_plan_data(plan_path)
        else:
            self._root_mode = 'single'
            self._folder_mode = 'single'
            self._delete_original = False
            self._continue_even_if_exists = False
            self._root_input_path = None
            self._output_path = None
            self._disallowed_folders = []
            self._redaction_texts = []


    def _read_plan_data(self, plan_path):
        """
        Validates and read the plan file into a JSON object.        
        :param self: Description
        :param plan_path: Description
        """
        plan_path = Path(plan_path)

        if not (plan_path.exists() and plan_path.is_file()):
            raise FileNotFoundError(f"the path '{plan_path}' was not found.")
        
        plan_data = {}
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_data = json.load(f)
        
        return plan_data
    

    def _fill_with_file_data(self, data):
        if data is None:
            raise TypeError("the data parameter cannot be null")
        
        try:
            self._root_mode = data['rootMode'].lower() if ('rootMode' in data) else 'single'
            # only useful if root_mode is 'multi'. 
            # folderMode can be:
            #  "single", effectively disabling this option. Only used if the root_mode is "single"
            #  "list", meaning the root folder itself contains multiple files. This is the default if root_mode is not single but folder_mode is not given
            #  "parenting", meaning the root folder is parent of other folders with files.
            #  "recursive", meaning the root folder is parent of other folders containing files and possibly subfolders.
            if self._root_mode == "single":
                self._folder_mode =  self._root_mode
            else:
                self._folder_mode = data['folderMode'].lower() if ('folderMode' in data) else 'list'
        except KeyError:
            print(f"FAILED: at least one required key was not found{get_help_text}")
