groupname	= "AdornType"
adornname	= "Object"
objectcount	= 0
typecount	= 0
adorngroups = {}

-- create adorn names from sql_object.lua and write to AdornList.lua
sql_objects = dofile("..\\..\\redist\\script\\sql_object.lua")

f = openfile("AdornList.lua", "w+")
if not f then 
	print("ERROR: AdornList.lua is write protected. Please check this out (the file)!\n")
	exit()
end
	
write(f, "-- AdornList.lua\n")
write(f, "-- Hier stehen alle Adorn Object IDs mit den beschreibenden Namen...\n")
write(f, "-- DO NOT EDIT - THIS FILE IS AUTO GENERATED!\n\n")
write(f, "return {\n")

for i = 1024, 1279 do
	local adorn = sql_objects[i]
	if (adorn) then
		write(f, "{ Id = " .. tostring(i) .. ", Name = \"" .. adorn.name .. "\"\t\t},\n")
	end
end

write(f, "}\n")
closefile(f)
print("Updated: AdornList.lua")


-- write the adorn object sections
function WriteAdornObject(index, object)
	
	-- only write to file after each 2nd parameter
	if (mod(index, 2) == 0) then
		-- fix percentage to 0-255 format
		percentage = floor(object * 255 / 100)
		
		-- write object data
		write(des, "\t\tP = " .. percentage .. "\n")
		write(des, outstring)

		write(txt, percentage .. "%]\n")
		
		-- write section closer
		write(des, "\t}\n")
		return
	end

	-- write section opener
	objectcount = objectcount + 1
	write(des, "\t[" .. adornname .. objectcount .. "]\n\t{\n")

	write(txt, "\t" ..object .. "\t[")

	-- look up string name of object in AdornList
	if type(object) == "string" then
		for i = 1, getn(AdornList) do
			if AdornList[i].Name == object then
				object = AdornList[i].Id
				break
			end
		end
	end

	
	-- if object is still a string, it could not be found in AdornList!
	if type(object) == "string" then
		print("ERROR: could not find the Object Id for:\n")
		print("\"" .. object .. "\"\n")
		print("You most likely made a typing error, shame on you! Aborting...")
		exit()
	end
		
	-- write the object data (has to be second write, so just store it)
	outstring = "\t\tI = " .. object .. "\n"
end


-- write the adorn type sections
function WriteAdornType(index, type)

	-- write section opener
	objectcount = 0
	typecount = typecount + 1
	write(des, "[" .. groupname .. typecount .. "]\n{\n")
	write(txt, "\nType " .. typecount .. ":\n")
	
	-- write each object
	foreachi(type, WriteAdornObject)
	
	-- write section closer
	write(des, "}\n\n")
end


function CreateAdornGroup(group)
	assert2(type(group) == "table", "NOT A TABLE!")
	tinsert(adorngroups, group)
end


-- main export, loop through each table entry
function ExportAdorns()

	-- open adorns file and destroy its contents
	des = openfile("AdornObject.des", "w+")
	assert(des, "AdornObject.des: file open failed! FILE AUSGECHECKT?")

	txt = openfile("AdornObjects.txt", "w+")
	assert(txt, "AdornObjects.txt: file open failed! FILE AUSGECHECKT?")

	-- traverse the adorn groups
	foreachi(adorngroups, WriteAdornType)

	closefile(des)
	closefile(txt)
	
	print("Updated: AdornObject.des")
	print("\nFinished converting to DES file!")
end
