-- funktionen einbinden
dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

-- HIER GEHTS LOS:

bergeboden		= 6
bergeanstieg	= 24
bergesteil		= 7
bergesehrsteil	= 21

inselboden		= 16
inselbodenbraun	= 32
inselanstieg	= 11
inselsteil		= 10

sumpfboden		= 13
sumpfsteil		= 11

function WegBoden()
	BeginRuleSet()
	SetDefaults	()
	SetObject	(1)
	SetRange	(1, Rectangle)
	SetSteep	(0, 25)
	SetTexture	(27)
	CreateRule	()

	SetObject	(1)
	SetRange	(0, Rectangle)
	SetSteep	(0, 25)
	SetTexture	(27)
	CreateRule	()
end

function BasicExpoInseln()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(6, 255)
	SetExposMax	(2000)
	SetTexture	(bergeanstieg)
	CreateRule	()
end

function BasicSteepnessInseln()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(6, 255)
	SetSteep	(0, 5)
	SetTexture	(inselboden)
	CreateRule	()

	SetSteepRel	(16)
	SetTexture	(inselbodenbraun)
	CreateRule	()

	SetSteepRel	(30)
	SetTexture	(inselanstieg)
	CreateRule	()

	SetSteepRel	(40)
	SetTexture	(bergeanstieg)
	CreateRule	()

	SetSteepRel	(55)
	SetTexture	(bergesteil)
	CreateRule	()

	SetSteepRel	(90)
	SetTexture	(bergesehrsteil)
	CreateRule	()
end

function BasicSteepnessSumpf()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(1, 6)
	SetSteep	(0, 10)
	SetTexture	(sumpfboden)
	CreateRule	()

	SetSteepRel	(90)
	SetTexture	(sumpfsteil)
	CreateRule	()
end


-- LAST PASS - fill the holes just in case....................................
function FillTheHolesTM()
	BeginRuleSet()
	SetDefaults	()
	SetTexture	(21)
	CreateRule	()
end


-- function list
-- here the set of rules can be re-ordererd if necessary

WegBoden()
BasicSteepnessInseln()
BasicSteepnessSumpf()

FillTheHolesTM()

-- hiermit wird der export gestartet
-- das muss immer die letzte zeile sein!
-- export geht in filename.lua mit .des Endung
ExportAutoTexture()
