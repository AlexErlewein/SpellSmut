SFCFF - SpellForce 1 database manipulation program

Table of contents:
1. Purpose of the tool
2. Structure of gamedata file
3. Command usage


1. Purpose of the tool

SFCFF.exe is an command line application which allows opening and extracting data from GameData.cff file - main database file for SpellForce 1. The file is located in "data" folder in the game folder.
GameData.cff contains various data used by the game to determine the values used for most of the gameplay features, such as, but not limited to, units, spells, items and buildings. It also contains all text used by the game, in multiple languages. Being able to modify contents of this file means being able to modify various gameplay features of the game.
In addition to extracting the data, SFCFF.exe also allows to pack the data back to original format, and to create a difference file of two separate GameData.cff files - a feature useful in tandem with the upcoming mod support.


2. Structure of gamedata file

GameData.cff stores all data in chunks. Each chunk is identified using chunk ID and chunk version. For each data type, there exists a separate chunk. Currently there are 49 different chunks in GameData.cff, each storing data of different type.


3. Command usage

These are the available commands:
- "l <fname>" - list the contents of given gamedata file
- "u <fname> <a/iX/tX/nX> [export_raw]" - extract content of given gamedata file
- "p <fname> <a/iX/tX/nX>" - pack content of gamedata file back to the gamedata
- "d <fname1> <fname2>" - create a difference file of two gamedata files

"l <fname>" prints the information of every chunk contained in a given gamedata file. <fname> is a full filename, including path, of the CFF file. The following information is printed for every chunk: chunk ID, chunk type, chunk name, chunk subtype/version, size of data (in bytes) contained in the chunk.

"u <fname> <a/iX/tx/nx> [export_raw]" extracts selected (or all) chunks from given file to a separate folder, named after the gamedata file. Data is extracted to XML files, so it can be modified in any text editor. <fname> is a full filename, including path, of the CFF file.
The following selection arguments can be used:
- "a" - all chunks in the file are extracted".
- "iX" - only extract Xth chunk in the file.
- "tX" - only extract chunk with ID X in the file.
- "nX" - only extract chunk with name X in the file.
IDs and names of the available chunks are listed in SFCFF.cdt file.
If the optional "export_raw" is present, the chunks are exported in raw binary form instead of XML files.

"p <fname> <a/iX/tX/nX>" imports selected (or all) chunks from given location (determined by the filename of the resulting gamedata file) which contains the data in XML format. If the file under <fname> already exists, the chunks contained in it are replaced with the chunks described by the XML files, otherwise it is created with these chunks.
Similarly to "u" command, you can specify selection argument to only import/replace selected chunk:
- "a" - all chunks from the directory are imported.
- "iX" - only import Xth chunk from the directory.
- "tX" - only import chunk with ID X from the directory.
- "nX" - only import chunk with name X from the directory.

"d <fname1> <fname2>" creates a difference file of two specified gamedata files. The resulting CFF file is created/replaced in the directory determined by the filename of the 2nd specified gamedata.
The difference file is structured as follows:
- If a chunk exists in 2nd gamedata and not in 1st gamedata, it is imported from 2nd gamedata.
- If a chunk exists in both gamedata files, the contents are compared, and only those entries that either only exist in 2nd gamedata, or differ between the two gamedata files, are added to the difference file.
The difference file is typically much smaller than the entire GameData.cff, and so is well suited for mod support functionality.
Note: This command performs additional operations on resulting difference file which attempt to ensure validity of data the game would load.