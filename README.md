# DupliCut
A Python project created in order to remove duplicate files in given folder (could be a root of the driver as well). 
The application scans the entire folder recursively and removes the duplicated files (leaves only the last modified).
The algorithm makes sure that the files are bitwise identical using SHA and size (for optimization).

V0.1 (Current): The duplicate files printed to the terminal

V0.2 (Future): The duplicate files will be deleted automatically or moved to a temp folder (for manual removal by the user) [according to a flag]

V1.0 (Future): GUI will be added
