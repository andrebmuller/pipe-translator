# pipe-translator

A Python utility for translating pipe layout files from CAESAR II (.NTXT format) to PIPESTRESS (.FRE format).

## Overview

This tool converts piping system data exported from CAESAR II stress analysis software into a format readable by PIPESTRESS. It processes .NTXT files and generates .FRE files with appropriate PIPESTRESS cards for piping elements.

## Features

- **Automatic File Detection**: Scans the working directory for .NTXT files
- **Interactive File Selection**: Allows users to choose from multiple .NTXT files
- **Comprehensive Element Support**: Currently translates some piping elements including:
  - `CROS` - Cross-sections/pipe properties
  - `TANG` - Tangent/straight pipe sections
  - `BRAD` - Bend radius definitions
  - `VALV` - Valve components
  - `CRED` - Concentrated reducers
  - `ERED` - Eccentric reducers
  - `SUPP` - Support points
  - `JUNC` - Junction points
  - `ANCH` - Anchor points
- **Logging**: Detailed operation logging with timestamps
- **Error Handling**: Robust error handling for file operations

## Requirements

- Python 3.x
- pandas library
- os (built-in)
- datetime (built-in)

## Installation

1. Clone or download the repository
2. Install required dependencies:
   ```bash
   pip install pandas
   ```

## Usage

1. Place your .NTXT files in the same directory as `pipe-translator.py`
2. Run the script:
   ```bash
   python pipe-translator.py
   ```
3. If multiple .NTXT files are found, select the desired file when prompted
4. The translated .FRE file will be generated as `output.FRE`

## File Structure

### Input Format (.NTXT)
- Fixed-width format exported from CAESAR II
- Contains element types: ELMT, REST, RIGD, BEND, RED
- Includes node information, displacements, and pipe properties

### Output Format (.FRE)
- PIPESTRESS-compatible format
- Organized into two sections:
  - **PROPERTIES**: CROS cards defining pipe cross-sections
  - **PIPING**: Element cards defining the piping layout

## Classes

### Base
Base class providing common functionality:
- File system operations
- Logging capabilities
- Working directory management

### NtxtObj
Handles .NTXT file operations:
- File discovery and listing
- User file selection
- File parsing and dataframe creation

### PepsObj
Manages PIPESTRESS file generation:
- Element translation logic
- PIPESTRESS card generation
- Output file writing

## Translation Logic

The translator processes elements in the following manner:

1. **ELMT (Elements)**: Converted to TANG cards with displacement and property data
2. **REST (Restraints)**: Converted to SUPP cards for support points
3. **RIGD (Rigid)**: Converted to VALV cards for valve components
4. **BEND (Bends)**: Converted to BRAD cards with radius information
5. **RED (Reducers)**: Converted to CRED or ERED cards based on displacement data

## Output

- **Log File**: `pipe-translator.log` - Contains detailed operation logs
- **Output File**: `output.FRE` - PIPESTRESS-compatible piping data
- **Console Output**: Real-time operation status and prompts

## Example

```
> Base class created...
> NtxtObj class created...
> PepsObj class created...
> output.FRE file created...
>>> .NTXT file [0] --> example_pipe
>>> Read file [0]
> output.FRE file cleared...
> Translation job started...
> Translation job finished...
> Writing .FRE file...
>>> 5 CROS cards created!
>>> 25 element cards created!
```

## Error Handling

The application includes error handling for:
- File access issues
- Invalid file formats
- Missing data elements
- Index out of range errors

## Notes

- The tool assumes node numbering starts from 10 (anchor point)
- Cross-section properties are automatically numbered starting from 100
- Junction cards are automatically cleaned up to prevent duplicates
- All output includes proper PIPESTRESS formatting and syntax

## Software Information

- **Source Software**: CAESAR II
- **Target Software**: PIPESTRESS
- **File Formats**: .NTXT (CAESAR II export) → .FRE (PIPESTRESS input)

## Version History

- **v1.0.0**: First and current version
- Previous versions available in `/old` directory

## Author

[André Buchmann Müller](https://andrebmuller.notion.site/abm-eng)

## License

See LICENSE.md file for licensing information.