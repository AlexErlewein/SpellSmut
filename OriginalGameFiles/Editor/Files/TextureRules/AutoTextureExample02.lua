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

------------------------------------
-- DEFINE AUTOTEXTURING FUNCTIONS --
------------------------------------


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
	
	-- this will texture the whole world with several textures, simply by applying them
	-- to different ranges of steepness. Naturally in flat areas we have more grass, the
	-- steeper it gets the more stone we'll see.
	
	-- Now go check it out! With this little effort we already have an awesome result!
	-- Try to achieve the same by texturing everything manually, and you would be working
	-- on that 2-3 days alone!
	
	-- Plus, if you don't like how certain areas are textured, you don't change the textures there!
	-- No, it's much easier to simply change the geometry, often only by a little, and then apply
	-- the autotexturing script again. Repeat this step a couple times and your map is going to look
	-- better not only in terms of textures but also geometry!
end


---------------------------------------------------
-- CALL AUTOTEXTURING FUNCTIONS IN DESIRED ORDER --
---------------------------------------------------

-- the call order is most important!
-- begin with detailed texturing of certain areas of the map
-- and finish with globally applicable but general rules!


AT_BySteepness()


----------------------------------
-- EXPORT SCRIPT TO .DES FORMAT --
----------------------------------

-- never omit this line or you won't get a resulting .des file
-- never write anything below this line because it will be ignored
-- (at least it wouldn't change the texturing rules).
ExportAutoTexture()
---- EOF --------- EOF --------- EOF --------- EOF --------- EOF --------- EOF --------- EOF -----