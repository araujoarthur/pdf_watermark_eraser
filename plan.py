
import sys
import json
from functools import wraps
from pathlib import Path

from consts import get_help_text

class RedactionPlanInternalError(Exception):
    pass

class RedactionPlanNotInitializedError(Exception):
    pass

def must_have_initialized(func):
    @wraps(func)
    def validator(self, *args, **kwargs):
        if not self._initialized:
            raise RedactionPlanNotInitializedError("plan not initialized")

        return func(self, *args, **kwargs)
    
    return validator


class RedactionPlan:
    _initialized: bool
    _root_mode: str
    _folder_mode: str
    _delete_original: bool
    _continue_even_if_exists: bool
    _root_input_path: Path
    _output_path: Path
    _disallowed_folders: list[str]
    _redaction_texts: list[str]

    def __init__(self, plan_path):
        self._initialized = False
        if plan_path:
            data = self._read_plan_data(plan_path)
            self._fill_with_file_data(data)
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

            self._delete_original = data['deleteOriginal'] if ('deleteOriginal' in data) else False

            self._continue_even_if_exists = data['ignoreOutputPathIntegrity'] if ('ignoreOutputPathIntegrity' in data) else False

            # Sanitizes, validates and saves the Root Input Path
            self._root_input_path = Path(data['rootInputPath']).resolve()
            if not self._root_input_path.exists():
                raise RedactionPlanInternalError("input root path not Found")
            elif self._root_mode == 'single' and (not self._root_input_path.is_file()):
                raise RedactionPlanInternalError("the running mode is set to 'SINGLE', but the rootInputPath is not a file")
            elif self._root_mode != 'single' and (not self._root_input_path.is_dir()):
                raise RedactionPlanInternalError("the running mode is set to 'MULTI', but the rootInputPath is not a folder")
            
            # Sanitizes, validates and saves the Output Path
            self._output_path = Path(data['outputPath']).resolve()

            if self._output_path.exists():
                if not self._continue_even_if_exists:
                    raise RedactionPlanInternalError(f"the output path already exists, set the option 'ignoreOutputPathIntegrity' to true to continue anyways{get_help_text}")
                if self._root_mode != 'single' and self._output_path.is_file():
                    raise RedactionPlanInternalError(f"the output path is a file, but the running mode is not 'single'{get_help_text}")
    
            # Fills disallowed folders
            disallowed_folders = data['excludedFolderNames'] if ('excludedFolderNames' in data) else []
            self._disallowed_folders = disallowed_folders

            # Fills the redaction texts
            self._redaction_texts = data['redactionTexts'] if ('redactionTexts' in data) else None
            if not self._redaction_texts:
                raise RedactionPlanInternalError(f"there are no texts to redact{get_help_text}")
            
        except KeyError:
            print(f"FAILED: at least one required key was not found{get_help_text}")
            sys.exit()
        except RedactionPlanInternalError as rpie:
            print(f"FAILED: {rpie}{get_help_text}")
            sys.exit()

        self._initialized = True

    def fill_with_file(self, plan_path):
        plan_path = Path(plan_path)
        data = self._read_plan_data(plan_path)
        self._fill_with_file_data(data)

    def initialized(self) -> bool:
        return self._initialized
    
    @must_have_initialized
    def root_mode(self) -> str:
        return self._root_mode
    
    @must_have_initialized
    def folder_mode(self) -> str:
        return self._folder_mode

    @must_have_initialized
    def delete_original(self) -> bool:
        return self._delete_original
    
    @must_have_initialized
    def continue_even_if_exists(self) -> bool:
        return self._continue_even_if_exists

    @must_have_initialized
    def root_input_path(self) -> Path:
        return self._root_input_path

    @must_have_initialized
    def output_path(self) -> Path:
        return self._output_path
    
    @must_have_initialized
    def disallowed_folders(self) -> list[str]:
        return list(self._disallowed_folders)

    @must_have_initialized
    def redaction_texts(self) -> list[str]:
        return list(self._redaction_texts)