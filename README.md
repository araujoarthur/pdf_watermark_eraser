# PDF Watermark Eraser

Erases *horizontal string* watermarks from PDF files.

## Usage

```bash
python main.py [OPTIONS]

OPTIONS:
    -h, --help: shows the help message
    -p, --plan PLAN_PATH: inputs a custom plan path.
```

If `-p` is not used, the script expects a file `plan.json` to exist in the working directory.

### Plan Format

```json
{
    "rootMode":"multi" | "single",
    "folderMode":"list" | "single" | "parenting" | "recursive",
    "ignoreOutputPathIntegrity":true | false,
    "deleteOriginal": true | false,
    "rootInputPath":"./EXAMPLE_PATH",
    "excludedFolderNames":[
        "EXAMPLE_FOLDER_NAME"
    ],
    "outputPath":"./example_output_directory",
    "redactionTexts": [
        "TEXT_TO_BE_REDACTED"
    ]
}
```

---

#### `rootMode`

- `single`, `multi`

This option declares the nature of the `rootInputPath`.

When set to `single`, the script will assume the `rootInputPath` refers to a **file** and will ignore the value of `folderMode`.

When set to `multi`, the script will assume the `rootInputPath` is a folder and delegate the decision about it's contents to `folderMode` value.

if no `rootMode` is provided, the value is defaulted to `single`.

---

#### `folderMode`

- `single`, `list`, `parenting`, `recursive`

This option declares the structure of the `rootInputPath` and is pivotal for redaction strategy selection.

When set to `single`, the script will assume the `rootInputPath` is a single file.

When set to `list`, the script will assume the `rootInputPath` is a folder containing one or more PDF files.

When set to `parenting`, the script will assume the `rootInputPath` contents are folders whose direct children are files.

When set to `recursive`, the script will assume `rootInputPath` contents are files or folders, the latter having other folders or files as children.

---

#### `ignoreOutputPathIntegrity`

- `true`, `false`

This option defines the behavior of the outputing portion of the script.

When set to `true`, it will continue the execution even if the output path or file already exists on the target destination.

---

#### `deleteOriginal`

- `true`, `false`

This option defines the behavior regarding the original file after a successful redaction.

When set to `true`, the script will delete the original file after a successful redaction.

---

#### `rootInputPath`

- *path string*

This option defines the starting (*root*) point of the redaction. It's nature (`file` or `folder`) must match what is expected from the `rootMode` and `folderMode` options.

---

#### `excludedFolderNames`

- `list` of *strings*

This option holds the folder names to be ignored within the process.

>[!warning]
> As of now, this option hold folder names to be ignored within the whole TREE.
> **Eventually**, an option will be added to ignore certain paths.

---

#### `outputPath`

- *path string*

This option holds the directory where the converted files will be saved. If you're running with `folderMode` set to `parenting` or `recursive`, the structure of the `rootInputPath` will be recreated within `outputPath`.

---

#### `redactionTexts`

- `list` of *string*

This option holds the *exact* strings to be searched and removed from the file.

>[!danger]
> As of now, the script will not try to distinguish an watermark of actual file content,
> so **be careful when passing too simple values or single words**.

> [!warning]
> *Exact* here means **exact**. When passing strings, the elements `Text` and `text` are not equal.

---

## Requirements

- Python Version >= 3.10 (Although I wrote this using 3.13)
- [PyMuPDF](https://pymupdf.readthedocs.io)
