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

#### `rootMode`

- `single`, `multi`

When set to `single`, the script will assume the `rootInputPath` refers to a **file** and will ignore the value of `folderMode`.

If set to `multi`, the script will assume the `rootInputPath` is a folder and delegate the decision about it's contents to `folderMode` value.

if no `rootMode` is provided, the value is defaulted to `single`.

#### `folderMode`




## Requirements

- Python Version >= 3.10 (Although I wrote this using 3.13)
- [PyMuPDF](https://pymupdf.readthedocs.io)
