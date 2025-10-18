FilePacker - SpellForce 1 PAK archive creator


Table of contents:

1. What is a PAK archive?
2. Usage
3. PAK folder structure


1. What is a PAK archive?

PAK archive is a file which stores other files in itself - you can think of it as a folder which contains many of the game assets: sounds, textures, 3D models and animations, and so on. They're a convenient file format, since you can store all files you need in a single PAK archive.
The upcoming mod support allows creating and loading mods, which consist of several files. One of those files is a PAK archive with all of the mod assets. Another is a script file which lists all assets included in the PAK archive. This tool allows you to create a PAK archive, and the asset script file, out of a folder of files.


2. Usage

You can use this tool in one of two ways:
1. Drag and drop a folder onto the tool.
2. Run the tool in command line like this:
tool_filepacker.exe <folder_path> [-notable]
Drag and dropping a folder is equivalent to using the tool in command line: tool_filepacker.exe <dragged_folder_path>.

The program will organize and pack all files (and directories, and files/directories in those directories, etc.) into one PAK archive with the name "folder_path.pak". Additionally, it will generate a file "assets.lua" inside of the "folder_path" folder.
If "-notable" argument is specified, the program will not generate the "assets.lua" file.

Note: Packing "data/GameData.cff" into a PAK file may have adverse side effects in the game.
Note: There should be no files in the directory you choose to pack - only subdirectories. Those subdirectories can contain files.

3. PAK folder structure

SpellForce looks for game assets in PAK archives after it has not found the files in game folder. The following are the folders the game looks for the assets in:
- Textures: /texture, /texture/water; .dds format
- 3D models: /mesh; .msb format
- Sounds: /sound, /sound/speech/battle; .wav format
- Music: /sound; .mp3 format
- Speech: /sound/speech/female, /sound/speech/male, /sound/speech/messages; .wav format
- Skeleton files: /animation; .bor format
- Animations: /animation; .bob format
- Figure templates: /figure_template; .des format
- Skin files: /skinning/b20; .msb format
- Bone index files: /skinning/b20; .bsi format
- Scripts: /object, /script, /script/p####; .lua format (#### is map ID)
Your PAK folder should contain files structured as described above.