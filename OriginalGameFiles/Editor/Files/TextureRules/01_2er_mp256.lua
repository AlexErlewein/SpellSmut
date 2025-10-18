-- funktionen einbinden
dofile("AutoTexturerTools.lua")
-- initialisieren... (ja, das muss schon sein)
InitAutoTextureHelper()

-- Werte bleiben von Rule zu rule erhalten! (werden "durchgereicht")

function Heights()
	BeginRuleSet()
	SetDefaults	()
	
	SetHeight	(1, 7)
	SetTexture	(2)
	CreateRule()

	SetHeightRel(9)
	SetTexture	(28)
	CreateRule()

	SetHeightRel(11)
	SetTexture	(1)
	CreateRule()

	SetHeightRel(15)
	SetTexture	(20)
	CreateRule()

	SetHeightRel(17)
	SetTexture	(26)
	CreateRule()

	SetHeightRel(19)
	SetTexture	(16)
	CreateRule()

	SetHeightRel(21)
	SetTexture	(13)
	CreateRule()

	SetHeightRel(50)
	SetTexture	(30)
	CreateRule()
end


function Blocking()
	BeginRuleSet()
	SetDefaults	()
	
	SetSteep	(35, 90)
	SetTexture	(22)
	CreateRule()
end



TextureBySteepness
{
	MinHeight = 10, MaxHeight = 20,				-- zwischen 10.0 und 19.9 Metern höhe ...
	DefaultPercent = 5000,
	
	[1] = { MaxAngle = 3, Texture = 23 },		-- von 0-2°
	[2] = { MaxAngle = 6, Texture = 20, Percent = 2000 },		-- von 3-9°, 50%
	[3] = { MaxAngle = 10, Texture = 4 },		-- von 10-19°, Percent wieder 100%
	[4] = { MaxAngle = 20, Texture = 17 },		-- von 20-29° usw.
	[5] = { MaxAngle = 30, Texture = 24, Percent = 3000 },
	[6] = { MaxAngle = 50, Texture = 11 },
	[7] = { MaxAngle = 90, Texture = 9 },
}

TextureBySteepness
{
	MinHeight = 8, MaxHeight = 22,				-- zwischen 10.0 und 19.9 Metern höhe ...
	DefaultPercent = 10000,
	
	[1] = { MaxAngle = 3, Texture = 23 },		-- von 0-2°
	[2] = { MaxAngle = 6, Texture = 20 },		-- von 3-9°, 50%
	[3] = { MaxAngle = 10, Texture = 4 },		-- von 10-19°, Percent wieder 100%
	[4] = { MaxAngle = 20, Texture = 17 },		-- von 20-29° usw.
	[5] = { MaxAngle = 30, Texture = 24 },
	[6] = { MaxAngle = 50, Texture = 11 },
	[7] = { MaxAngle = 90, Texture = 9 },
}

--Blocking()
--Heights()

-- hiermit wird der export gestartet
-- das muss immer die letzte zeile sein!
-- export geht in filename.lua mit .des Endung
ExportAutoTexture()
