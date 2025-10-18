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

------------------------------------
-- DEFINE AUTOTEXTURING FUNCTIONS --
------------------------------------


-- now what else can we do? how about snow on the mountain tops?
-- note that by using Percentages lower than 10000 you will see that
-- every time you apply the autotexture script the snow textures on
-- the mountains will change slightly
function AT_SnowOnMountainTops()
	BeginRuleSet()
	SetDefaults	()
	-- only if steepness is between:
	SetSteep	(0, 40)
	-- only if height is between:
	SetHeight	(16, 24)
	-- only 50% of all tiles
	SetPercent	(5000)
	SetTexture	(texSnowGrass)
	CreateRule	()

	-- only if steepness is between 40 and 90 degrees:
	SetSteepRel	(90)
	-- only 80% of all tiles
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
	-- set initial steepness
	SetSteep	(0, 1)
	SetTexture	(texGrass)
	CreateRule	()

	-- set steepness relative to last (from last' max degree to this degree)
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

-- we need to call this function before the Steepness rules, otherwise it won't have any effect!
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