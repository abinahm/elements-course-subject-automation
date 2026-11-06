# Symplectic Elements Bulk Option Uploader

A Selenium script that bulk-adds dropdown choices ("options") to a field in the Symplectic Elements admin interface, using a list of display names from an Excel file.

Instead of clicking **Add new option**, typing a name, and saving hundreds of times,
you log in once and let the script do the repetitive work.

## Features

- Reads unique, trimmed display names from an Excel spreadsheet
- Skips options that already exist on the page (case-insensitive match)
- Verifies each option appears in the list after saving
- **Dry-run mode** to preview what would be added without changing anything
- Stops on the first error to avoid creating duplicate entries
- Writes a status report (`Added`, `Already Exists`, `Dry Run`, or `Unverified - Check Manually`) to `results.xlsx`

## Requirements

- Python 3.8+
- Google Chrome or Edge (Changeable based on the code)
- Python packages:
  - `pandas`
  - `openpyxl` (for reading/writing `.xlsx` files)
  - `selenium` (4.6+ recommended; it downloads a matching ChromeDriver automatically)

Install the dependencies:

```bash
MAC:
pip install pandas openpyxl selenium
```

## Input file

Create an Excel file named `option.xlsx` in the same folder as the script, with a
column headed exactly **`Display Name`**:

| Display Name |
|--------------|
| Option A     |
| Option B     |
| Option C     |

Blank cells and duplicate values are ignored.

## Configuration

Settings are constants at the top of the script:

| Setting       | Default                                        | Description                                                  |
|---------------|------------------------------------------------|--------------------------------------------------------------|
| `EXCEL_FILE`  | `option.xlsx`                                  | Path to the spreadsheet containing the options               |
| `COLUMN_NAME` | `Display Name`                                 | Column to read option names from                             |
| `URL`         | `https://elements.symplectic.org/underlyingfield.html?` | Starting page. Replace with your institution's Elements URL and field |
| `DRY_RUN`     | `False`                                        | Set to `True` to log what would be added without adding it   |

> **Tip:** Run with `DRY_RUN = True` first to confirm the script detects the
> existing options and the spreadsheet is read correctly.

## Usage

1. Prepare `option.xlsx` as described above.
2. Update `URL` to point at your Elements instance, and review `DRY_RUN`.
3. Run the script:

   ```bash
   python your_script_name.py
   ```

4. A Chrome window opens. **Log in manually** and navigate to the field
   configuration page where the options are listed.
5. Return to the terminal and press **ENTER**. The script will begin adding options.
6. When it finishes, review the summary in the terminal and `results.xlsx`,
   then press **ENTER** to close the browser.

## Output

`results.xlsx` contains one row per processed option:

| Status                         | Meaning                                                                 |
|--------------------------------|-------------------------------------------------------------------------|
| `Added`                        | Saved and confirmed in the options list                                 |
| `Already Exists`               | Found on the page before adding, so skipped                             |
| `Dry Run`                      | Would have been added (only when `DRY_RUN = True`)                      |
| `Unverified - Check Manually`  | An error occurred; the script stopped. Check the page before re-running |

Options after an error are not listed in the report, since the script halts at that
point. After checking the page, you can safely re-run: options already added are
detected and skipped.

## How it works

The script relies on the following `data-qa-id` attributes in the Elements UI:

- `add-item` – the "Add new option" button
- `display-name-field` – the Display name input in the dialog
- `save` – the Save button

Existing options are detected by scanning the page for text matching
`Display name: <value>`. If Symplectic changes its markup, these selectors may need updating.

## Troubleshooting

- **"Excel must contain a 'Display Name' column"** – check the header spelling,
  or change `COLUMN_NAME`.
- **Timeouts waiting for a button or input** – make sure you're on the correct
  field configuration page before pressing ENTER, and that the page has fully loaded.
- **Script stops with "Unverified"** – open the page and check whether the last
  option was actually saved before re-running.
- **Chrome driver errors** – update Chrome and Selenium (`pip install -U selenium`).

## Notes

- This script drives the admin UI on your behalf; use it only with a field and
  instance you're authorized to modify.
- Credentials are never stored. You log in manually in the browser window.
- Consider testing on a non-production instance or a single field first.
