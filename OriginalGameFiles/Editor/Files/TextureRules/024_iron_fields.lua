-- funktionen einbinden
dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

-- HIER GEHTS LOS:
function KartenRand()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(1, 8)
	SetSteep	(10, 25)
	SetTexture	(31)
	CreateRule	()

	SetSteepRel	(40)
	SetTexture	(25)
	CreateRule	()

	SetSteepRel	(90)
	SetTexture	(26)
	CreateRule	()
end

function HoherBoden()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(14, 22)
	SetSteep	(0, 3)
	SetPercent	(500)
	SetTexture	(5)
	CreateRule	()

	SetHeight	(11, 13)
	SetSteep	(0, 3)
	SetPercent	(1000)
	SetTexture	(5)
	CreateRule	()

	SetDefaults	()
	SetHeight	(14, 22)
	SetSteep	(0, 10)
	SetTexture	(6)
	CreateRule	()
end


sumpfboden		= 20
sumpfsteine		= 18
sumpfsteine2	= 16
sumpfhang		= 11

function SumpfBodenSteine()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(1, 10)
	SetSteep	(0, 16)
	SetPercent	(250)
	SetMarker	(230)
	CreateRule	()
	
	IncreasePriority()
	SetCondition(230)
	SetRange	(1)
	SetPercent	(6666)
	SetMarker	(231)
	CreateRule	()
	
	IncreasePriority()
	SetCondition(230)
	SetRange	(0)
	SetPercent	(10000)
	SetTexture	(sumpfsteine2)
	CreateRule	()

	SetCondition(231)
	SetTexture	(sumpfsteine2)
	CreateRule	()


	SetCondition(sumpfsteine2)
	SetRange	(2)
	SetPercent	(8000)
	SetTexture	(sumpfsteine)
	CreateRule	()
end

function BasicSteepnessSumpfTeiche()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(1, 10)
	SetSteep	(0, 1)
	SetTexture	(sumpfboden)
	CreateRule	()

	SetSteepRel	(3)
	SetTexture	(sumpfsteine)
	CreateRule	()

	SetSteepRel	(15)
	SetTexture	(sumpfsteine2)
	CreateRule	()

	SetSteepRel	(90)
	SetTexture	(sumpfhang)
	CreateRule	()
end


grasboden		= 2
grasboden2		= 28
waldboden		= 22
steilhang		= 31

function BasicSteepnessSumpf()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(10, 255)
	SetSteep	(0, 5)
	SetTexture	(grasboden)
	CreateRule	()

	SetSteepRel	(10)
	SetTexture	(grasboden2)
	CreateRule	()

	SetSteepRel	(20)
	SetPercent	(6000)
	SetTexture	(sumpfsteine2)
	CreateRule	()

	SetPercent	(10000)
	SetTexture	(sumpfsteine)
	CreateRule	()

	SetSteepRel	(90)
	SetHeight	(12, 255)
	SetTexture	(steilhang)
	CreateRule	()
end

eisenhell	= 31
eisenmedium	= 25
eisendunkel	= 26
eisengras	= 6
eisenrot	= 23
eisenhellrot= 32

function EisenFelsen()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(25, 100)
	SetSteep	(0, 25)
	SetTexture	(eisenhellrot)
	CreateRule	()

	SetHeight	(25, 31)
	SetSteep	(0, 90)
	SetTexture	(eisenrot)
	CreateRule	()

	SetHeight	(23, 25)
	SetSteep	(0, 90)
	SetTexture	(eisenhellrot)
	CreateRule	()


	SetDefaults	()
	SetHeight	(14, 100)
	SetSteep	(0, 30)
	SetTexture	(eisenhell)
	CreateRule	()

	SetSteepRel	(50)
	SetTexture	(eisenmedium)
	CreateRule	()

	SetSteepRel	(90)
	SetTexture	(eisendunkel)
	CreateRule	()

	-- eisengras
	IncreasePriority()
	SetDefaults	()
	SetHeight	(10, 20)
	SetSteep	(0, 20)
	SetCondition(eisenhell)
	SetRange	(4, Circle)
	SetTexture	(eisengras)
	CreateRule	()

	SetCondition(eisenhell)
	SetRange	(8, Circle)
	SetPercent	(4000)
	SetTexture	(eisengras)
	CreateRule	()

	SetCondition(eisenhell)
	SetRange	(10, Circle)
	SetPercent	(800)
	SetTexture	(eisengras)
	CreateRule	()
	
	SetCondition(eisenmedium)
	SetRange	(5, Circle)
	SetPercent	(10000)
	SetTexture	(eisengras)
	CreateRule	()

	SetCondition(eisenmedium)
	SetRange	(8, Circle)
	SetTexture	(eisengras)
	SetPercent	(3000)
	CreateRule	()

	SetCondition(eisenmedium)
	SetRange	(10, Circle)
	SetTexture	(eisengras)
	SetPercent	(500)
	CreateRule	()
end


-- LAST PASS - fill the holes just in case....................................
function FillTheHolesTM()
	BeginRuleSet()
	SetDefaults	()
	SetTexture	(11)
	CreateRule	()
end


-- function list
-- here the set of rules can be re-ordererd if necessary

KartenRand()
HoherBoden()
EisenFelsen()
SumpfBodenSteine()
BasicSteepnessSumpfTeiche()
BasicSteepnessSumpf()

FillTheHolesTM()

-- hiermit wird der export gestartet
-- das muss immer die letzte zeile sein!
-- export geht in filename.lua mit .des Endung
ExportAutoTexture()
