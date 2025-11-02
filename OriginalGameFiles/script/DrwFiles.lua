--local Anims, Meshes, Bones, Used

function list_append(list1, list2)
	for i = 1, getn(list2), 1 do
		list_insert(list1, list2[i])
	end
end

local modnum = UtlMod:GetInstalledModCount()

BonesDir = dir_readdirectory("animation\\*.bor")
BonesFile = strsplit("\n", gsub(readfile("animation\\bones.txt"), "\r", ""))
Bones = list_concat(BonesFile, BonesDir)

AnimsDir = dir_readdirectory("animation\\*.*")
AnimsFile = strsplit("\n", gsub(readfile("animation\\anims.txt"), "\r", ""))
Anims = list_concat(AnimsFile, AnimsDir)

MeshesDir = dir_readdirectory("mesh\\*.*")
MeshesFile = strsplit("\n", gsub(readfile("mesh\\meshes.txt"), "\r", ""))
Meshes = list_concat(MeshesFile, MeshesDir)


for i = 0, modnum, 1 do
	local moddir = UtlMod:GetInstalledModDirectory(i)
	if moddir == "" then break end

	local modfiles = doscript(moddir .. "\\script\\assets.lua")
	if modfiles then
		list_append(Bones, modfiles["Bones"])
		list_append(Anims, modfiles["Anims"])
		list_append(Meshes, modfiles["Meshes"])
	end
end

Bones = list_converttoset(Bones)
Anims = list_converttoset(Anims)
Meshes = list_converttoset(Meshes)

Used = {}

-- strip bones from anims
local nAnims = getn(Anims)
for i = nAnims, 1, -1 do
	local v = Anims[i]
	if (strfind(v, ".bor")) then
		tremove(Anims, i)
		--print(v)
	end
end


-- dump(Bones)
-- dump(Anims)
-- dump(Meshes)

function Find(sName, tDirectory)
	for i, v in tDirectory do
		if (sName == strsub(v,1,strlen(v)-4)) then
			return i
        end
	end
	return nil
end

function FindAnim(sName)
	return Find(sName, %Anims)
end

function FindBones(sName)
	return Find(sName, %Bones)
end

function FindMesh(sName)
	return Find(sName, %Meshes)
end