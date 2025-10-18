-- funktionen einbinden
dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

Rem = [[
-- HIER GEHTS LOS:
glitzerblau		= 3
blassesgras		= 13
braunerdreck	= 18
seegruenstein	= 19
waldboden		= 22
wegrandmisch	= 36


function WegeTexturieren()
	-- wege texturieren...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 6)
	SetRange	(2, Circle)
	SetPercent	(5000)
	SetObjRange	(1, 1)
	SetTexture	(21)
	CreateRule	()
	
	SetPercent	(10000)
	SetSteep	(0, 12)
	SetRange	(2, Rectangle)
	SetObjRange	(1, 1)
	SetTexture	(20)
	CreateRule	()
	
	SetRange	(0, Rectangle)
	SetObjRange	(1, 1)
	SetTexture	(20)
	CreateRule	()
end

function WegZuGrasUebergang()
	-- übergang weg zum gras
	IncreasePriority()
	SetDefaults	()
	SetSteep	(0, 24)
	SetRange	(1, Circle)
	SetCondition(20)
	SetTexture	(36)
	CreateRule	()
	
	SetRange	(1, Circle)
	SetCondition(21)
	SetTexture	(36)
	CreateRule	()
end

function DreckUnterBaeumen()
	-- dreck unter bäumen und so
	BeginRuleSet()
	SetDefaults	()
	SetComment	("Dreck unter Bäumen!")
	SetSteep	(0, 10)
	SetRange	(1, Circle)
	SetObjRange	(512, 520)
	SetMarker	(235)
	CreateRule	()
	
	IncreasePriority()
	SetRange	(0, Circle)
	SetCondition(235)
	SetTexture	(12)
	CreateRule	()
	
	SetComment	("last Dreck unter Bäumen...")
	SetRange	(1, Circle)
	SetCondition(235)
	SetTexture	(36)
	CreateRule	()
end

function WegRandMischTextur()
	-- mischtextur wegrand
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(5, 7)
	SetSteep	(16, 24)
	SetTexture	(wegrandmisch)
	CreateRule	()
end

function BeckenBoden()
	-- beckenböden
	SetHeight	(1, 4)
	SetSteep	(0, 10)
	SetTexture	(glitzerblau)
	CreateRule	()
	
	SetHeight	(1, 3)
	SetSteep	(10, 50)
	SetTexture	(seegruenstein)
	CreateRule	()
end

function GrasFlecken()
	-- flecken ins gras
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(1, 18)
	SetSteep	(0.0, 3.0)
	SetPercent	(2000)
	SetMarker	(249)
	CreateRule	()
	
	IncreasePriority()
	SetSteep	(0, 5)
	SetPercent	(4000)
	SetRange	(1)
	SetCondition(249)
	SetMarker	(248)
	CreateRule	()
	
	IncreasePriority()
	SetPercent	(8000)
	SetRange	(1)
	SetCondition(248)
	SetMarker	(247)
	CreateRule	()
	
	IncreasePriority()
	SetPercent	(10000)
	SetRange	(0)
	SetCondition(247)
	SetMarker	(0)
	SetTexture	(8)
	CreateRule	()
	
	SetCondition(248)
	SetTexture	(8)
	CreateRule	()
	
	SetCondition(249)
	SetTexture	(9)
	CreateRule	()
end

function ExponierteStellen()
	-- exponierte stellen
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(1, 12)
	SetExposMax	(30)
	SetTexture	(22)
	CreateRule	()
end

function SchneeAufBergen()
	-- schnee auf bergen
	BeginRuleSet()
	SetDefaults	()
	SetComment	("schnee auf bergen")
	SetSteep	(60, 90)
	SetHeight	(20, 255)
	SetTexture	(5)
	CreateRule	()
	
	SetHeight	(25, 255)
	SetSteep	(30, 60)
	SetTexture	(2)
	CreateRule	()
	
	SetDefaults	()
	SetSteep	(0, 60)
	SetHeight	(25, 255)
	SetTexture	(10)
	CreateRule	()
end


function HochGebirgeVerschoenern()
	-- hochgebirge verschönern
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(18, 200)
	SetSteep	(8, 20)
	SetMarker	(250)
	CreateRule	()
	
	IncreasePriority()
	SetPercent	(1600)
	SetRange	(1)
	SetCondition(250)
	SetMarker	(251)
	CreateRule	()
	
	IncreasePriority()
	SetSteep	(12, 16)
	SetPercent	(3000)
	SetRange	(1)
	SetCondition(250)
	SetMarker	(252)
	CreateRule	()
	
	IncreasePriority()
	SetRange	(1)
	SetCondition(251)
	SetMarker	(252)
	CreateRule	()
	
	IncreasePriority()
	SetPercent	(10000)
	SetRange	(1)
	SetCondition(250)
	SetTexture	(waldboden)
	CreateRule	()
	
	SetPercent	(5000)
	SetRange	(1)
	SetCondition(251)
	SetTexture	(waldboden)
	CreateRule	()
	
	SetSteep	(8, 20)
	SetPercent	(2000)
	SetRange	(1)
	SetCondition(250)
	SetTexture	(waldboden)
	CreateRule	()
end

function GruenLandImGebirge()
	-- grünland verzierung im gebirge
	BeginRuleSet()
	SetHeight	(18, 200)
	SetSteep	(0, 12)
	SetPercent	(4500)
	SetTexture	(5)
	CreateRule	()
	
	SetSteep	(8, 20)
	SetPercent	(3000)
	SetTexture	(5)
	CreateRule	()
end

function GebirgeSteepness()
	-- ab höhe 18 nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(18, 200)
	SetSteep	(0, 15)
	SetTexture	(5)
	CreateRule	()
	
	SetSteepRel	(30)
	SetTexture	(31)
	CreateRule	()
	
	SetSteepRel	(40)
	SetTexture	(28)
	CreateRule	()
	
	SetSteepRel	(55)
	SetTexture	(26)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(27)
	CreateRule	()
end

function HuegelSteepness()
	-- ab höhe 10 nur nach steepness texturen auf die landschaft
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(10, 200)
	SetSteep	(0, 2)
	SetTexture	(9)
	CreateRule	()
	
	SetSteepRel	(6)
	SetTexture	(9)
	CreateRule	()
	
	SetSteepRel	(9)
	SetTexture	(9)
	CreateRule	()
	
	SetSteepRel	(12)
	SetTexture	(12)
	CreateRule	()
	
	SetSteepRel	(16)
	SetTexture	(wegrandmisch)
	CreateRule	()
	
	SetSteepRel	(19)
	SetTexture	(22)
	CreateRule	()
	
	SetSteepRel	(22)
	SetTexture	(23)
	CreateRule	()
	
	SetSteepRel	(35)
	SetTexture	(31)
	CreateRule	()
	
	SetSteepRel	(45)
	SetTexture	(29)
	CreateRule	()
	
	SetSteepRel	(55)
	SetTexture	(26)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(27)
	CreateRule	()
end
]]
function FlachLandSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 1)
	SetTexture	(10)
	CreateRule	()
	
	SetSteepRel	(3)
	SetTexture	(10)
	CreateRule	()
	
	SetSteepRel	(7)
	SetTexture	(9)
	CreateRule	()
	
	SetSteepRel	(12)
	SetTexture	(9)
	CreateRule	()
	
	SetSteepRel	(17)
	SetTexture	(8)
	CreateRule	()
	
	SetSteepRel	(20)
	SetTexture	(4)
	CreateRule	()
	
	SetSteepRel	(28)
	SetTexture	(4)
	CreateRule	()
	
	SetSteepRel	(35)
	SetTexture	(4) --8
	CreateRule	()
	
	SetSteepRel	(40)
	SetTexture	(5)  --6
	CreateRule	()
	
	SetSteepRel	(45)
	SetTexture	(5) --6
	CreateRule	()
	
	SetSteepRel	(50)
	SetTexture	(3)--6
	CreateRule	()
	
	SetSteepRel	(60)
	SetTexture	(4)--6
	CreateRule	()
	
	SetSteepRel	(75)
	SetTexture	(6)--6
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(3)--3
	CreateRule	()
end

function HeightMountainFill()
	BeginRuleSet()
	SetDefaults	()
	SetHeight	(15, 200)
	SetSteep	(0, 30)
	SetTexture	(10)
	CreateRule	()
	
	
end

function Flecken()
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 3)
	SetTexture	(6)
	SetPercent (4000)
	CreateRule	()
	
	SetSteep	(0, 3)
	SetTexture	(10)
	SetPercent (3000)
	CreateRule	()
	
	SetSteep	(20, 50)
	SetTexture	(8)
	SetPercent (2000)
	CreateRule	()
	
	SetSteep	(40, 90)
	SetTexture	(5)
	SetPercent (1500)
	CreateRule	()
	
	SetSteep	(40, 90)
	SetTexture	(32)
	SetPercent (2500)
	CreateRule	()

end

-- LAST PASS - fill the holes just in case....................................

function FillTheHolesTM()
	BeginRuleSet()
	SetDefaults	()
	SetTexture	(9)
	CreateRule	()
	
	
end


-- function list
-- here the set of rules can be re-ordererd if necessary
Rem = [[
WegeTexturieren()
WegZuGrasUebergang()
DreckUnterBaeumen()
WegRandMischTextur()
BeckenBoden()
GrasFlecken()
ExponierteStellen()
SchneeAufBergen()
HochGebirgeVerschoenern()
GruenLandImGebirge()
]]

--GebirgeSteepness()
--HuegelSteepness()
Flecken()
HeightMountainFill()
FlachLandSteepness()

FillTheHolesTM()

-- hiermit wird der export gestartet
-- das muss immer die letzte zeile sein!
-- export geht in filename.lua mit .des Endung
ExportAutoTexture()
