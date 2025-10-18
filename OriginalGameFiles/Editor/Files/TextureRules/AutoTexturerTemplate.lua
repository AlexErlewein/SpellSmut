--------------------------------
-- AUTOTEXTURER DOCUMENTATION --
--------------------------------

MultiLineComment = [[
This is a LUA script. For more information on LUA and documentation about 
its syntax and features go to:
http://www.lua.org

 LUA comments: everything following two dashes is considered a comment:
-- this is a single line comment
variable = 10	-- this is a comment at the end of a line


NOTE: it is generally NOT ADVISABLE to spray too many textures in one viewscreen (the
screen area the user actually sees from the zoomed out ISO perspective). The engine
takes a performance hit for every texture that lies directly next to another, and the
more different textures are surrounding a single tile the more fill rate is needed to
keep the graphics fluid in that particular area, so especially slower gfx cards which
lack in raw fill rate speeds will take a serious performance hit while modern gfx
cards will not be affected as much. However you can still make the game go to a serious
frame rate drop on any machine if you spray 20-30 different textures in one visible area.
Go ahead an try it in the editor, take a blank map, texture it with a single texture and
scroll over it. Now spray a small area with as many different textures as possible using
the spray feature, then scroll over the area .... your framerate might even drop to below
10 fps (on a reasonably fast machine, 2 GHz and GF4) just by over-texturing the terrain.
Now try to imagine what would happen when you begin adding details like adornments, objects
and play the maps with lots of buildings placed and units created... ;)


-- FUNCTION REFERENCE:

-- Use either one of these functions at the beginning of every "rule set".
-- A "rule set" is a rule or set of rules that are applied to the whole map
-- in a single iteration. Usually in a detailed autotexturer there are several
-- iterations over the whole map with different rules. For example, at first
-- texture everything above 100 meters with stone & snow (mountains) (rule set #1),
-- then texture 80% of the world between 80 and 100 meters with fewer snow but more
-- stones (rule set #2), then apply textures simply by looking at the steepness
-- (rule set #3). This is an abstract description of how you can "read" the rules.
-- To understand the iterations you need to know that once a tile has been assigned
-- a texture, it will keep this texture even if a following iteration tells it to
-- use a different texture. That's why the details of the autotexturing process,
-- for example roads or spraying mountain tops with snow must be processed FIRST.
-- Whereas functions like AT_BySteepness() must be the last one called.
	BeginRuleSet()
	IncreasePriority()	-- exactly the same as above, just a synonym

-- set all autotexturing values to safe default values:
	SetDefaults	()

-- the default values are:
--	Height		= 1, 255		-- Height should NEVER be 0 or the ocean will be textured!
								-- If Height is 1,255 everything within 1 and 255 meters will be textured.
--	Steep		= 0, 90			-- Steepness in degrees, a steepness of 0 is totally flat, 
								-- 90 degrees is actually not possible to achieve in any map
								-- usually there's hardly any tile steeper than 70-80 degrees.
--	Percent		= 10000			-- Percentages go from 0 to 10000 to allow for real numbers using
								-- an integer. That means 10000 = 100% and 100 = 1% and 10 = 0.1%
--	Range		= 0				-- Range is in Tiles, Range = 0 means the current tile, Range = 1
								-- also includes the 8 surrounding tiles and so on up to a Range of 10.
--	Condition	= 0				-- Condition is the ID of a texture marker, if this marker is set
								-- on the current tile the condition is met. All textures with IDs
								-- 224-255 are considered markers and not actual textures!
--	ExposureMin	= 0				-- condition for negative exposure (e.g. a hole or "dent" in the ground)
								-- the condition is met if the current tile's height difference to the
								-- surrounding tiles is greater than ExposureMin (unless it is 0)
								-- ExposureMin and ExposureMax are exclusive and can not be used together!
--	ExposureMax	= 0				-- condition for exposure (e.g. a "bump" or elevated tile)
								-- the condition is met if the current tile's height difference to the
								-- surrounding tiles is greater than ExposureMax (unless it is 0)
								-- ExposureMin and ExposureMax are exclusive and can not be used together!
--	ObjectMin	= 0				-- lowest Object Id of Object Range to check for
--	ObjectMax	= 0				-- highest Object Id of Object Range to check for
								-- if ObjectMin and ObjectMax are the same, only that object is included in the check
								-- get Object IDs from the editor's Object Placement window
--	Marker		= 0				-- a Marker Id, Markers are Texture Ids in the range from 224 to 255
--	Texture		= 1				-- Texture Id of the Texture to use, 0 is not a valid texture, 1 is the base texture.
								-- Texture IDs 1 to 31 are normal textures, higher texture IDs stand for mix
								-- textures. The textured map will look blurry if you autotexture with a
								-- Texture ID that is not defined in the map/texture mixer.
								-- To find out which texture has which ID, open the "Place Textures" Menu and
								-- hover the mouse cursor over a texture. Note that the texture IDs in the upper
								-- panel of the texture mixer are global IDs and not for use with the autotexturer.

-- finishes a rule
-- a rule is the minimum amount of information required to create a rule for texturing tiles
-- for example, using all default values and then using CreateRule() will create a rule that textures
-- the whole map with the base texture. However it makes more sense to at least change the Texture (let's say
-- we want a grass texture) and then maybe also say that we want to texture only flat areas from 0-10 degrees.
-- Then use CreateRule() and all flat areas will have the grass texture applied. Of course, to texture the
-- whole range of degrees from 0-90 with different textures you would create a rule for every range of steepness
-- and also change the texture for each rule. In most cases this is already enough to give your map an adequate
-- look, at least it will still save you a lot of work then if you would texture everything manually.
	CreateRule()


-- with these utility functions you can change the default values to specific values:

-- set height range from HeightMin to HeightMax meters. HeightMin must be smaller than or equal to HeightMax.
-- setting HeightMin to 0 will result in a square map because then even the "ocean tiles" will be textured,
-- so avoid setting HeightMin to 0.
	SetHeight(HeightMin, HeightMax)

-- increases both HeightMin and HeightMax from previous rule by the given amount.
	AddHeight(HeightAdd)

-- Increases height range relative to the previous height. This is very useful!
-- What it does is when you have set height to 1 to 10 meters and then call SetHeightRel with 20 meters you
-- actually do the same as calling SetHeight with parameters 10, 20.
-- Why is this so useful? Because if you need to adjust one rule to include 1 to 15 meters now, you don't need
-- to update the second rule because it will automatically adjust (15 to 20 meters now), unless you break the
-- rules and try to SetHeightRel with a height smaller than the last HeightMax.
	SetHeightRel(HeightMax)


-- set the steepness range in angles from 0-90 degrees. SteepMin must be smaller than or equal to SteepMax.
	SetSteep(SteepMin, SteepMax)

-- increases both SteepMin and SteepMax from previous rule by the given amount.
	AddSteep(SteepAdd)
	
-- Increases steepness range relative to the previous steepness. This is very useful!
-- What it does is when you have set steepness to 0 to 10 degrees and then call SetSteepRel with 20 degrees you
-- actually do the same as calling SetSteep with parameters 10, 20.
-- Why is this so useful? Because if you need to adjust one rule to include 0 to 15 degrees now, you don't need
-- to update the second rule because it will automatically adjust (15 to 20 degrees now), unless you break the
-- rules and try to SetSteepRel with a steepness angle smaller than the last SteepMax.
	SetSteepRel	(SteepMax)
	
-- set the percentage (chance) with which the texture is applied. Percentage is in the range 0 to 10000,
-- whereas 10000 would be 100%, 100 = 1% and 10 = 0.1% ... Note that a rule using percentages will leave
-- some tiles untextured (actually they remain textured with the ugly, grey stone base texture 1). 
-- To avoid logical "gaps" in your rules, it is best to copy the rule using a percentage lower than 10000
-- and applying another texture with 10000 percentage right after that. For example, say you want to have
-- a 50% chance of applying either texture 10 or 14, so you set percentage to 5000 (50%) with texture id 10 and copy
-- the rule and paste it just after this one, setting percentage to 10000 (100% because 50% of tiles have already
-- been textured and will NOT change!) and texture to 14 to get the desired result.
-- Another example with 3 textures, you want each texture 10, 14 and 17 to be applied with equal chances of 33%.
-- So you create the first rule with texture id 10 and percentage of 3333 (33.33%), good.
-- The next rule uses texture id 14 and percentage of ... (i'll keep you thinking here) ...
-- No, don't use a percentage of 33333! ;)
-- Why? Because 33% of all tiles have already been textured and will not change, so with the second texture
-- you actually have to texture with a percentage of 5000 (50% of the remaining untextured tiles!), while
-- the last texture id 17 gets a percentage of 10000 (100% .. because there are only 33% tiles left untextured).
	SetPercent(Percent)

-- Sets a marker with the Id of 224 to 255. A tile "textured" with a marker does not count as textured and thus
-- you can use markers to flag certain tiles in one rule or rule set and check for these markers in later
-- rules and then actually apply a texture to a marked tile. With markers you can make spots with fringes,
-- for example.
	SetMarker(Marker)
	
-- Set a texture Id to texture tiles with. Texture 0 is not a valid texture. Texture IDs 1-31 are the basic
-- textures and texture IDs 32 and above are the mix textures (2 or 3 textures mixed into one).
	SetTexture(Texture)

-- Checks for Texture or Marker with the given Id. Also takes into account the Range Parameter.
-- For example you could check whether one of the surrounding tiles (Range = 1) has been textured with the
-- given texture or marker Id and if so, the current texture or marker will be applied to the current tile.
	SetCondition(Texture)	-- or Marker

-- Checks for condition in Range tiles. By default Range is 0 which means check only the current tile whether
-- it meets the condition(s). Range can be up to 10 tiles and of type Rectangle or Circle.
	SetRange(Range, Type)	-- Type is either 'Rectangle' oder 'Circle' (without quotation marks)


-- Checks for negative exposure (holes, dents, or what you'd call it) of a tile.
-- the condition is met if the current tile's height difference to the surrounding tiles is greater than
-- ExposureMin (unless it is 0)
-- ExposureMin and ExposureMax are exclusive and can not be used together!
	SetExposMin(ExposureMin)

-- Checks for exposure (holes, dents, or what you'd call it) of a tile.
-- condition for exposure (e.g. a "bump" or elevated tile) the condition is met if the current tile's height
-- difference to the surrounding tiles is greater than ExposureMax (unless it is 0)
-- ExposureMin and ExposureMax are exclusive and can not be used together!
	SetExposMax(ExposureMax)

-- Checks whether there is an object with Object ID between Min and Max in the range.
	SetObjRange(ObjectIdMin, ObjectIdMax)
	
-- Checks whether there is an object with Object ID in the range. This is usually more useful than
-- the above function.
	SetObject(ObjectId)

-- Simply creates a comment that appears in the .DES file for the rule.
-- Not really useful since we don't look into the .DES files anymore and LUA comments are more convenient.
-- Might help the curious user in debugging and understanding.
	SetComment(Comment)
]]
MultiLineComment = nil		-- delete the comment string variable


-------------------------------------------
-- INITIALIZATION OF AUTOTEXTURER SCRIPT --
-------------------------------------------

-- DO NOT REMOVE THIS LINE !!
-- REQUIRED AT THE BEGINNING OF EVERY AUTOTEXTURER SCRIPT:
dofile("AutoTexturerTools.lua")


----------------------------------
-- DEFINE GLOBAL VARIABLES HERE --
----------------------------------

-- variable declaration is optional but helps readability
-- you can assign texture numbers to descriptive names like
-- texGreenGrass = 10
-- texGrassStoneTransition = 11
-- and use these names instead of fixed numbers in SetTexture()

-- this also helps in globally replacing textures, e.g. if you
-- rather want to have a different type of grass texture then you
-- would only have to change the texture number in this place, instead
-- of in every call to SetTexture()

texGrass = 3


------------------------------------
-- DEFINE AUTOTEXTURING FUNCTIONS --
------------------------------------

-- each function should cover a specific use
-- for example texturing a specific height, or simply by steepness,
-- or texturing roads, or creating spots of snow in flat areas, ...

function Test()
	-- Werte bleiben von Rule zu rule erhalten! (werden "durchgereicht")
	BeginRuleSet()
	SetDefaults	()
	
	-- Startwerte angeben (nur die die von defaults abweichen):
	SetComment	("Also los gehts!")
	SetHeight	(10, 20)
	SetSteep	(0, 5)
	SetPercent	(10000)
	SetTexture	(krass)
	CreateRule	()
	
	SetSteepRel	(9)	-- SteepMin wird dann SteepMax von voriger Rule (5-9°)
	SetTexture	(krassesgras)
	CreateRule	()
	
	SetComment	("Mehrzeilige comments\n// gehen auch aber halt nur\n// so wie hier!")
	SetHeightRel(30)	-- Height geht jetzt von 20 bis 30 meter
	AddSteep	(11)	-- Steep Min und Max werden je um 11° erhöht (16-20°)
	SetTexture	(krassenstein)
	CreateRule	()
	
	-- nächstes set regeln...
	SetComment	("hier gehts weiter...")
	BeginRuleSet()
	SetDefaults	()
	SetRange	(2, Circle)
	SetCondition(krassenstein)
	SetTexture	(krassgemisch)
	SetPercent	(2000)
	CreateRule	()
end

-- simply apply textures by steepness, no other special rules here
-- this usually suffices to get a decent texturing for most maps
-- also makes sure that every tile in the map is not left untextured
function AT_BySteepness()
	-- begin new iteration of rules
	BeginRuleSet()
	-- reset all values to defaults
	SetDefaults	()

	SetSteep	(0, 1)
	SetTexture	(texGrass)
	CreateRule	()

	SetSteepRel	(3)
	SetTexture	(krassesgras)
	CreateRule	()

	SetSteepRel	(6)
	SetTexture	(krassesgras)
	CreateRule	()

	SetSteepRel	(10)
	SetTexture	(krassesgras)
	CreateRule	()
end

-- special functions here:


---------------------------------------------------
-- CALL AUTOTEXTURING FUNCTIONS IN DESIRED ORDER --
---------------------------------------------------

-- the call order is most important!
-- begin with detailed texturing of certain areas of the map
-- and finish with globally applicable but general rules!


-- texturing by steepness should always be called last,
-- to make sure that every tile in the map has been
-- textured. Unhandled tiles do not pose a problem,
-- but it does look ugly because untextured tiles
-- remain textured with the base texture (always the first
-- texture in the set). Unless you have changed the
-- first texture in the set, this will be an ugly grey
-- stone texture...
-- Usually AT_BySteepness() is already a very fine start
-- and if you prefer you can leave it at that and texture
-- the details manually, as those details are mostly harder
-- to achieve using an autotexturer if you are not comfortable
-- and/or experienced with using autotexturing scripts.
AT_BySteepness()


-- and this should be called at the very end
-- this will actually create the corresponding .des file
-- that can be loaded in the editor.
-- never omit this line or you won't get a resulting .des file
-- never write anything below this line because it will be ignored
-- (at least it wouldn't change the texturing rules).
ExportAutoTexture()
---- EOF --------- EOF --------- EOF --------- EOF --------- EOF --------- EOF --------- EOF -----