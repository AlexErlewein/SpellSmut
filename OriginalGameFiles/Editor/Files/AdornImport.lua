AdornList = dofile("AdornList.lua")

-- convert existing AdornObject.des file to AdornObjectDefinition.IMPORT.lua


-- import DES file ...

AdornTypes = {}
NumAdornTypes = 0
Objects = {}
ReadingObject = nil

print("Reading AdornObject.des...")

f = openfile("AdornObject.des", "r")

repeat
	local line = read(f)
	if not line then break end
	
	if strfind(line, "AdornType", 1, 1) then
		NumAdornTypes = NumAdornTypes + 1
		AdornTypes[NumAdornTypes] = {}
		--print("\nNew AdornType: " .. NumAdornTypes)
	end
	
	if strfind(line, "Object", 1, 1) then
		Objects = {}
		--print("New Object")
	end
	
	if strfind(line, "P = ", 1, 1) then
		start = strfind(line, "=", 1, 1) + 2
		local num = tonumber(strsub(line, start))
		Objects[2] = num
		--print("Found P = " .. num)
	end

	if strfind(line, "I = ", 1, 1) then
		start = strfind(line, "=", 1, 1) + 2
		local num = tonumber(strsub(line, start))
		Objects[1] = num
		tinsert(AdornTypes[NumAdornTypes], tcopy(Objects))
		--print("Found I = " .. num)
	end
	
until nil
closefile(f)

print("Reading " .. getn(AdornTypes) .. " AdornTypes.")

-- export to AdornObjectDefinition.IMPORT.lua

print("Writing AdornObjectDefinition.IMPORT.lua...")
f = openfile("AdornObjectDefinition.IMPORT.lua", "w+")
if not f then 
	print("ERROR: AdornObjectDefinition.IMPORT.lua is write protected.\nPlease check this out (the file)!\n")
	exit()
end
write(f, "-- exportfunktion einbinden\n")
write(f, "dofile(\"adornexport.lua\")\n")
write(f, "-- liste der adorn objects einbinden\n")
write(f, "AdornList = dofile(\"adornlist.lua\")\n\n\n")

for i = 1, NumAdornTypes do
	write(f, "Name = \"AdornType" .. i .. "\"\n")
	write(f, "CreateAdornGroup\n{\n")

	for k = 1, getn(AdornTypes[i]) do
		local Id = AdornTypes[i][k][1]
		local Percent = AdornTypes[i][k][2]

		-- look up string name of object in AdornList
		for l = 1, getn(AdornList) do
			if AdornList[l].Id == Id then
				Name = AdornList[l].Name
				break
			end
		end
		
		if not Name then
			print("ERROR: could not find a name for this ID: " .. Id)
			exit()
		end

		-- fix percent to 0-100 format
		Percent = ceil(Percent / 255 * 100)
		
		write(f, "\t\"" .. Name .. "\", " .. Percent .. ",\n")
	end
	
	write(f, "}\n\n")
end

write(f, "\n-- hiermit wird der export gestartet\n")
write(f, "-- das muss immer die letzte zeile sein!\n")
write(f, "ExportAdorns()\n")
closefile(f)

print("\nDone Importing!\n")
