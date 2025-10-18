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


------------------------------------
-- DEFINE AUTOTEXTURING FUNCTIONS --
------------------------------------


function AT_BySteepness()
	-- begin new iteration of rules
	BeginRuleSet()
	-- reset all values to defaults
	SetDefaults	()
	-- the least we should do: assign texGrass (texture id 6)
	SetTexture	(texGrass)
	CreateRule	()
	
	-- this will texture the whole world with just one texture!
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