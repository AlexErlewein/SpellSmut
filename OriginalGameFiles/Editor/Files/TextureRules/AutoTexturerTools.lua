----------------------------------------------------
-- CREATE AUTOTEXTURER .DES FILES FROM .LUA INPUT --
----------------------------------------------------

-- you are not supposed to edit this file!
-- however, who am i to stop you? ;)

-- just keep in mind that any modifications done here
-- might result in autotexturer conversion to not work
-- (properly) anymore.
-- Especially the output to .DES format is crucial, as
-- this file format is *very* picky about proper
-- formatting and syntax.

-- Let me also tell you that this script does just the
-- conversion to .DES files. The actual rules and behavior
-- of the autotexturer are hard-coded in the editor's .EXE
-- So you can't really make any significant changes here.

-- What could be done is more simplification or automation
-- of repetetive tasks, such as specialized functions for
-- texturing spots or roads.

-- You have been warned! ;)
-- Steffenj


Rectangle	= 0
Circle		= 1

-- global init
function InitAutoTextureHelper()

	-- take lua filename, strip it from extension and add ".des"
	outfile = arg[0]
	len = strlen(outfile)
	outfile = strsub(outfile, 1, len - 4)
	outfile = outfile .. ".des"
	
	-- init one-time init default values
	rules	= { }
	indx	= 0
	prio	= 0
	comm	= nil
	numtext	= { }
	numtextures	= 0
	nummixtextures = 0
	texturestring = ""
	mixtexturestring = ""
	unusedtexturestring = ""
	
	SetDefaults()
	ClearModifiedFlags()
end


function SetDefaults()
	hmin	= 1
	hmax	= 255
	smin	= 0
	smax	= 90
	perc	= 10000
	rang	= 0
	cond	= 0
	exmn	= 0
	exmx	= 0
	obmn	= 0
	obmx	= 0
	mark	= 0
	text	= 1
end

function ClearModifiedFlags()
	-- modified flags	
	prio_mod	= nil
	hght_mod	= nil
	stp_mod		= nil
	perc_mod	= nil
	rang_mod	= nil
	cond_mod	= nil
	expo_mod	= nil
	obj_mod		= nil
	mark_mod	= nil
	text_mod	= nil
end


function BeginRuleSet()
	assert(prio_mod == nil, "ERROR: BeginRuleSet called twice in Rule #" .. indx + 1)
	prio_mod = 1
	prio = prio + 1
end

function IncreasePriority()
	assert(prio_mod == nil, "ERROR: IncreasePriority called twice in Rule #" .. indx + 1)
	BeginRuleSet()
end


function SetHeight(HeightMin, HeightMax)
	assert(HeightMin ~= nil, "ERROR: SetHeight() missing parameter in Rule #" .. indx + 1)
	assert(HeightMax ~= nil, "ERROR: SetHeight() missing parameter in Rule #" .. indx + 1)
	assert(hght_mod == nil, "ERROR: Height changed twice in Rule #" .. indx + 1)
	hght_mod = 1
	hmin = floor(HeightMin)
	hmax = floor(HeightMax)
end

function AddHeight(HeightAdd)
	assert(HeightAdd ~= nil, "ERROR: AddHeight() missing parameter in Rule #" .. indx + 1)
	assert(hght_mod == nil, "ERROR: Height changed twice in Rule #" .. indx + 1)
	hght_mod = 1
	hmin = hmin + floor(HeightAdd)
	hmax = hmax + floor(HeightAdd)
end

function SetHeightRel(HeightMax)
	assert(HeightMax ~= nil, "ERROR: SetHeightRel() missing parameter in Rule #" .. indx + 1)
	assert(hght_mod == nil, "ERROR: Height changed twice in Rule #" .. indx + 1)
	hght_mod = 1
	hmin = hmax
	hmax = floor(HeightMax)
end


function SetSteep(SteepMin, SteepMax)
	assert(SteepMin ~= nil, "ERROR: SetSteep() missing parameter in Rule #" .. indx + 1)
	assert(SteepMax ~= nil, "ERROR: SetSteep() missing parameter in Rule #" .. indx + 1)
	assert(stp_mod == nil, "ERROR: Steep changed twice in Rule #" .. indx + 1)
	stp_mod = 1
	smin = floor(SteepMin)
	smax = floor(SteepMax)
end

function AddSteep(SteepAdd)
	assert(SteepAdd ~= nil, "ERROR: AddSteep() missing parameter in Rule #" .. indx + 1)
	assert(stp_mod == nil, "ERROR: Steep changed twice in Rule #" .. indx + 1)
	stp_mod = 1
	smin = smin + floor(SteepAdd)
	smax = smax + floor(SteepAdd)
end

function SetSteepRel(SteepMax)
	assert(SteepMax ~= nil, "ERROR: SetSteepRel() missing parameter in Rule #" .. indx + 1)
	assert(stp_mod == nil, "ERROR: Steep changed twice in Rule #" .. indx + 1)
	stp_mod = 1
	smin = smax
	smax = floor(SteepMax)
end


function SetPercent(Percent)
	assert(Percent ~= nil, "ERROR: SetPercent() missing parameter in Rule #" .. indx + 1)
	assert(perc_mod == nil, "ERROR: Percent changed twice in Rule #" .. indx + 1)
	perc_mod = 1
	perc = Percent
end

function SetRange(Range, Type)
	assert(Range ~= nil, "ERROR: SetRange() missing Range parameter in Rule #" .. indx + 1)
	assert(rang_mod == nil, "ERROR: Range changed twice in Rule #" .. indx + 1)
	rang_mod = 1
	rang = Range
	if (Type == Circle) then
		rang = rang * -1
	end
end

function SetCondition(Condition)
	assert(Condition ~= nil, "ERROR: SetCondition() missing parameter in Rule #" .. indx + 1)
	assert(cond_mod == nil, "ERROR: Condition changed twice in Rule #" .. indx + 1)
	cond_mod = 1
	cond = Condition
end

function SetExposMin(ExposureMin)
	assert(ExposureMin ~= nil, "ERROR: SetExposMin() missing parameter in Rule #" .. indx + 1)
	assert(expo_mod == nil, "ERROR: Exposure changed twice in Rule #" .. indx + 1)
	expo_mod = 1
	exmn = ExposureMin
	exmx = 0
end

function SetExposMax(ExposureMax)
	assert(ExposureMax ~= nil, "ERROR: SetExposMax() missing parameter in Rule #" .. indx + 1)
	assert(expo_mod == nil, "ERROR: Exposure changed twice in Rule #" .. indx + 1)
	expo_mod = 1
	exmn = 0
	exmx = ExposureMax
end

function SetObjRange(ObjectIdMin, ObjectIdMax)
	assert(ObjectIdMin ~= nil, "ERROR: SetObjRange() missing parameter in Rule #" .. indx + 1)
	assert(ObjectIdMax ~= nil, "ERROR: SetObjRange() missing parameter in Rule #" .. indx + 1)
	assert(obj_mod == nil, "ERROR: ObjectId changed twice in Rule #" .. indx + 1)
	obj_mod = 1
	obmn = ObjectIdMin
	obmx = ObjectIdMax
end

function SetObject(ObjectId)
	assert(ObjectId ~= nil, "ERROR: SetObject() missing parameter in Rule #" .. indx + 1)
	assert(obj_mod == nil, "ERROR: ObjectId changed twice in Rule #" .. indx + 1)
	obj_mod = 1
	obmn = ObjectId
	obmx = ObjectId
end


function SetMarker(Marker)
	assert(Marker ~= nil, "ERROR: SetMarker() missing parameter in Rule #" .. indx + 1)
	assert(mark_mod == nil, "ERROR: Marker changed twice in Rule #" .. indx + 1)
	mark_mod = 1
	mark = Marker
	text = 0
end

function SetTexture(Texture)
	assert(Texture ~= nil, "ERROR: SetTexture() missing parameter in Rule #" .. indx + 1)
	assert(mktx_mod == nil, "ERROR: Texture changed twice in Rule #" .. indx + 1)
	text_mod = 1
	text = Texture
	-- count number of textures
	numtext[text] = 1
end

function SetComment(Comment)
	assert(SetComment ~= nil, "ERROR: SetComment() missing parameter in Rule #" .. indx + 1)
	comm = Comment
end


function TextureBySteepness(params)
	assert(type(params) == "table")
	assert(params.MinHeight)
	assert(params.MaxHeight)
	assert(params.MinHeight > 0)
	
	if not params.DefaultPercent then params.DefaultPercent = 10000 end
	
	BeginRuleSet()
	SetDefaults	()
	
	for i = 1, getn(params) do
		SetHeight	(params.MinHeight, params.MaxHeight)
		if i == 1 then
			SetSteep(0, params[i].MaxAngle)
		else
			SetSteepRel	(params[i].MaxAngle)
		end
		SetTexture	(params[i].Texture)
		
		if params[i].Percent ~= nil then
			SetPercent(params[i].Percent)
		else
			SetPercent(params.DefaultPercent)
		end
		
		CreateRule	()
	end
end



-- count number of different textures used in all rules
function CountTextures()
	num = getn(numtext)
	for i = 1, num do
		if (i <= 31) then
			if (numtext[i] ~= nil) then
				 numtextures = numtextures + 1
				 if (i < 10) then
				 	texturestring = texturestring .. " " .. i .. ", "
				 else
				 	texturestring = texturestring .. i .. ", "
				 end
			else
				if (i < 10) then
					unusedtexturestring = unusedtexturestring .. " " .. i .. ", "
				else
					unusedtexturestring = unusedtexturestring .. i .. ", "
				end
			end -- if
		else
			if (numtext[i] ~= nil) then
				nummixtextures = nummixtextures + 1
				mixtexturestring = mixtexturestring .. i .. ", "
			end -- if
		end -- if
	end -- for
end


function CreateRule()

	-- a new rule increases the index
	indx = indx + 1

removed = [[
	-- screen output
	if (comm ~= nil) then
		print("// " .. comm)
	end
	print("Creating Rule #" .. indx)
]]
removed = nil

	-- ensure the current set of values is valid
	assert(indx >= 0,		"ERROR: Index < 0 in Rule #" .. indx)
	assert(indx <= 255,		"ERROR: Index > 255 in Rule #" .. indx)
	assert(prio >= 1,		"ERROR: Priority < 1 in Rule #" .. indx)
	assert(prio <= 255,		"ERROR: Priority > 255 in Rule #" .. indx)
	assert(hmin >= 1,		"ERROR: HeightMin < 1 in Rule #" .. indx)
	assert(hmax <= 255,		"ERROR: HeightMax > 255 in Rule #" .. indx)
	assert(hmax > hmin,		"ERROR: HeightMax <= HeightMin in Rule #" .. indx)
	assert(smin >= 0.0,		"ERROR: SteepMin < 0.0 in Rule #" .. indx)
	assert(smax <= 90.0,	"ERROR: SteepMax > 90.0 in Rule #" .. indx)
	assert(smax > smin,		"ERROR: SteepMax <= SteepMin in Rule #" .. indx)
	assert(perc > 0,		"ERROR: Percent <= 0 in Rule #" .. indx)
	assert(perc <= 10000,	"ERROR: Percent > 10000 in Rule #" .. indx)
	assert(rang >= -10,		"ERROR: Range < -10 in Rule #" .. indx)
	assert(rang <= 10,		"ERROR: Range > 10 in Rule #" .. indx)
	assert(cond >= 0,		"ERROR: Condition < 0 in Rule #" .. indx)
	assert(cond <= 255,		"ERROR: Condition > 255 in Rule #" .. indx)
	assert(exmn <= 1000,	"ERROR: ExposureMin > 1000 in Rule #" .. indx)
	assert(exmx <= 1000,	"ERROR: ExposureMax > 1000 in Rule #" .. indx)
	assert(exmn >= 0,		"ERROR: ExposureMin < 0 in Rule #" .. indx)
	assert(exmx >= 0,		"ERROR: ExposureMax < 0 in Rule #" .. indx)
	if (exmn >= 1) then
		assert(exmx == 0,	"ERROR: Both ExposureMin and Max > 0 in Rule #" .. indx)
	end
	if (exmx >= 1) then
		assert(exmn == 0,	"ERROR: Both ExposureMin and Max > 0 in Rule #" .. indx)
	end
	assert(obmn >= 0,		"ERROR: ObjectIdMin < 0 in Rule #" .. indx)
	assert(obmx >= 0,		"ERROR: ObjectIdMax < 0 in Rule #" .. indx)
	assert(obmn <= obmx,	"ERROR: ObjectIdMin > ObjectIdMax in Rule #" .. indx)
	assert(mark >= 224 or mark == 0,
							"ERROR: Marker < 224 in Rule #" .. indx)
	assert(mark <= 255,		"ERROR: Marker > 255 in Rule #" .. indx)
	assert(text >= 0,		"ERROR: Texture < 0 in Rule #" .. indx)
	assert(text <= 223,		"ERROR: Texture > 223 in Rule #" .. indx)
	if (mark >= 1 and text >= 1) then
		assert(nil,			"ERROR: Both Marker and Texture > 0 in Rule #" .. indx)
	end
	if (mark == 0 and text == 0) then
		assert(nil,			"ERROR: Neither Marker nor Texture > 0 in Rule #" .. indx)
	end
	

	-- store this rule
	rules[indx] =
	{
		Priority	= prio,
		HeightMin	= hmin,
		HeightMax	= hmax,
		SteepMin	= smin,
		SteepMax	= smax,
		Percent		= perc,
		Range		= rang,
		Condition	= cond,
		ExposureMin	= exmn,
		ExposureMax	= exmx,
		ObjectIdMin	= obmn,
		ObjectIdMax	= obmx,
		Marker		= mark,
		Texture		= text,
		Comment		= comm,
	}

	-- clear the comment, each comment should appear only once
	comm = nil
	
	-- reset texture and marker automatically
	text = 0
	mark = 0
	
	ClearModifiedFlags()
end


function WriteRule(Index, Rule)

	-- write comment if it exists
	if (Rule.Comment ~= nil) then
		write(des, "// " .. Rule.Comment .. "\n")
	end

	-- write rule settings
	write(des, "[Rule" .. Index .. "]\n{\n")
	write(des, "\tPriority\t= " .. Rule.Priority .. "\n")
	write(des, "\tHeight\t\t= " .. Rule.HeightMin .. ", " .. Rule.HeightMax .. "\n")
	write(des, "\tSteep\t\t= " .. Rule.SteepMin .. ", " .. Rule.SteepMax .. "\n")
	write(des, "\tPercent\t\t= " .. Rule.Percent .. "\n")
	write(des, "\n")
	
	-- write rule terms
	write(des, "\t[Terms]\n\t{\n")
	write(des, "\tRange\t\t= " .. Rule.Range .. "\n")
	write(des, "\tCondition\t= " .. Rule.Condition .. "\n")
	write(des, "\tExposureMin\t= " .. Rule.ExposureMin .. "\n")
	write(des, "\tExposureMax\t= " .. Rule.ExposureMax .. "\n")
	write(des, "\tObjectMin\t= " .. Rule.ObjectIdMin .. "\n")
	write(des, "\tObjectMax\t= " .. Rule.ObjectIdMax .. "\n")
	write(des, "\t}\n")
	
	-- write rule results
	write(des, "\t[Result]\n\t{\n")
	write(des, "\tMarker\t\t= " .. Rule.Marker .. "\n")
	write(des, "\tTexture\t\t= " .. Rule.Texture .. "\n")
	write(des, "\t}\n")
	write(des, "}\n\n")

end


function ExportAutoTexture()
	-- open autotexture file and destroy its contents
	des, msg = openfile(outfile, "w+")
	assert(des, "ERROR: File open failed! " .. tostring(outfile) .. "\n" .. tostring(msg))

	-- write header
	write(des, "// File created by ExportAutoTexture()\n")
	write(des, "// DO NOT MODIFY! ... modify .lua instead!\n\n")

	-- print statistics
	CountTextures()
	summary = "Created " .. indx .. " Rules with " .. prio .. " Passes and " .. numtextures .. "/" .. nummixtextures .. " (Base/Mix) Textures.\n"
	write(des, "// " .. summary .. "\n")
	print("\n" .. summary)

	write(des, "// textures used:\n")
	print("textures used:")
	write(des, "// base  : " .. texturestring .. "\n")
	print("base  : " .. texturestring)
	write(des, "// mix   : " .. mixtexturestring .. "\n\n")
	print("mix   : " .. mixtexturestring)
	write(des, "// unused: " .. unusedtexturestring .. "\n\n")
	print("unused: " .. unusedtexturestring)

	-- traverse the table of rules
	foreachi(rules, WriteRule)

	closefile(des)
end


rem = [[
-- TO DO:
-- wrapping format:

TextureExposure
{
	-- use either ExposMax or Min
}

TextureSpots
{
	MinHeight = 10, MaxHeight = 20,
	MinAngle = 0, MaxAngle = 15,
	Percent = 500, ObjectId = 0,	-- either one ...
	SpotSize = 5,
	OuterPercent = 100,	-- chance that farthest tile from center will be textured (center tile == 10000)
						-- maybe support non-linear degradation?
	Textures = { 20, 20, 31, 30, 15 },	-- there must be exactly "SpotSize" textures given, in this case 5
}

]]
