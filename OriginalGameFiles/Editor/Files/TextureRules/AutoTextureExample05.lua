---------------------------------
-- AUTOTEXTURER EXAMPLE SCRIPT --
---------------------------------

-------------------------------------------
-- INITIALIZATION OF AUTOTEXTURER SCRIPT --
-------------------------------------------

-- DO NOT REMOVE THIS LINE !!
-- REQUIRED AT THE BEGINNING OF EVERY AUTOTEXTURER SCRIPT:
dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()


----------------------------------
-- DEFINE GLOBAL VARIABLES HERE --
----------------------------------

texGrass = 6
texGrass2 = 30
texGrass3 = 5
texBrownGrass = 13
texMudGrass = 4
texStoneGravel = 16
texGravel = 31
texGravel2 = 20
texStone = 27
texStone2 = 11

texSnowGrass = 21
texSnowStone = 22
texSnow = 28
texIce = 24

markMud1 = 224
markMud2 = 225
markMud3 = 226
markMud4 = 227
markMud5 = 228
markMud6 = 229

texMud1 = 2
texMud2 = 7
texMud3 = 8
texMud4 = 9
texMud5 = 23

------------------------------------
-- DEFINE AUTOTEXTURING FUNCTIONS --
------------------------------------


-- now we set a spot of dirt beneath every object
-- this should be more picky in object selection but for sake of demonstration
-- i included almost all objects ... the script would be better if only large trees had
-- the spots beneath them but that would make it much more complicated
function AT_MarkTreeSpots()
	BeginRuleSet()
	SetDefaults	()
	-- make sure the tree centre always gets the desired texture
	SetObjRange	(512, 2000)
	SetMarker	(markMud5)
	CreateRule	()

	-- now set the mud texture marker beneath every tree/object in the specified range
	SetRange	(3, Circle)
	SetPercent	(9000)
	SetMarker	(markMud6)
	CreateRule	()
end

function AT_TextureTreeSpots()
	BeginRuleSet()
	SetDefaults	()
	-- now set the actual mud texture on tree spot markers (#5)
	SetCondition(markMud5)
	SetTexture	(texMud4)
	CreateRule	()

	SetCondition(markMud6)
	SetTexture	(texMud3)
	CreateRule	()
end


-- to do this, we first have to find and mark tiles we would like to
-- be textured with a mud texture
function AT_MarkMudSpots()
	BeginRuleSet()
	SetDefaults	()
	-- at first set a marker with very low chance on very flat surface
	-- this will be our initial marker for the centre of the spot
	SetSteep	(0, 6)
	SetPercent	(50)
	SetMarker	(markMud1)
	CreateRule	()

	-- now start another iteration (so we will be able to "find" previous markers)
	-- look for the first marker and set other markers around it
	BeginRuleSet()
	-- look for marker in this range from current tile
	SetRange	(3, Circle)
	-- look for this marker
	SetCondition(markMud1)
	-- set marker with 90% chance, so we effectively create a circle around the spot centre
	-- by setting the marker markMud2 to every tile in range of markMud1
	SetPercent	(9000)
	SetMarker	(markMud2)
	CreateRule	()
    
	-- now start another iteration (so we will be able to "find" previous markers)
	-- look for the second marker and set another spot centre marker
	BeginRuleSet()
	-- look for marker in this range from current tile
	SetRange	(4, Circle)
	-- look for this marker
	SetCondition(markMud2)
	-- set marker with low percentage
	SetPercent	(100)
	SetMarker	(markMud3)
	CreateRule	()

	-- now start another iteration (so we will be able to "find" previous markers)
	-- look for the second marker and set other markers around it
	BeginRuleSet()
	-- look for marker in this range from current tile
	SetRange	(4, Circle)
	-- look for this marker
	SetCondition(markMud3)
	-- set marker with low percentage
	SetPercent	(6000)
	SetMarker	(markMud4)
	CreateRule	()
end

-- and then texture the marked tiles with the right textures
function AT_TextureMudSpots()
	BeginRuleSet()
	SetDefaults	()

	-- look for this marker
	SetCondition(markMud1)
	-- set this texture on the marked tile
	SetTexture	(texMud4)
	CreateRule	()

	SetCondition(markMud2)
	SetTexture	(texMud5)
	CreateRule	()

	SetCondition(markMud3)
	SetTexture	(texMud1)
	CreateRule	()

	SetCondition(markMud4)
	SetTexture	(texMud1)
	CreateRule	()
end


function AT_SnowOnMountainTops()
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 40)
	SetHeight	(16, 24)
	SetPercent	(5000)
	SetTexture	(texSnowGrass)
	CreateRule	()

	SetSteepRel	(90)
	SetPercent	(8000)
	SetTexture	(texSnowStone)
	CreateRule	()

	SetSteep	(0, 50)
	SetHeight	(18, 24)
	SetPercent	(2000)
	SetTexture	(texSnow)
	CreateRule	()

	SetSteep	(0,90)
	SetHeightRel(255)
	SetPercent	(10000)
	SetTexture	(texIce)
	CreateRule	()
end


function AT_BySteepness()
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 1)
	SetTexture	(texGrass)
	CreateRule	()

	SetSteepRel	(4)
	SetTexture	(texGrass2)
	CreateRule	()

	SetSteepRel	(8)
	SetTexture	(texGrass3)
	CreateRule	()

	SetSteepRel	(14)
	SetTexture	(texBrownGrass)
	CreateRule	()

	SetSteepRel	(20)
	SetTexture	(texMudGrass)
	CreateRule	()
	
	SetSteepRel	(28)
	SetTexture	(texStoneGravel)
	CreateRule	()
	
	SetSteepRel	(34)
	SetTexture	(texGravel)
	CreateRule	()
	
	SetSteepRel	(40)
	SetTexture	(texGravel2)
	CreateRule	()
	
	SetSteepRel	(52)
	SetTexture	(texStone)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(texStone2)
	CreateRule	()
end


---------------------------------------------------
-- CALL AUTOTEXTURING FUNCTIONS IN DESIRED ORDER --
---------------------------------------------------

-- the call order is most important!
-- begin with detailed texturing of certain areas of the map
-- and finish with globally applicable but general rules!

AT_MarkTreeSpots()
AT_TextureTreeSpots()

AT_MarkMudSpots()
AT_TextureMudSpots()

AT_SnowOnMountainTops()

AT_BySteepness()


----------------------------------
-- EXPORT SCRIPT TO .DES FORMAT --
----------------------------------

-- never omit this line or you won't get a resulting .des file
-- never write anything below this line because it will be ignored
-- (at least it wouldn't change the texturing rules).
ExportAutoTexture()
---- EOF --------- EOF --------- EOF --------- EOF --------- EOF --------- EOF --------- EOF -----