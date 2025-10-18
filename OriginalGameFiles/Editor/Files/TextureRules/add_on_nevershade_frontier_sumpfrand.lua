dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

function AufstiegeTexturieren()
	-- aufstiege texturieren...
	BeginRuleSet()
	SetDefaults	()
	SetRange	(2, Circle)
	SetObjRange	(1, 4)
	SetTexture	(3)
	CreateRule	()
		
end

function SandTexturieren()
	-- sand 10 texturieren (größerer Range)
	BeginRuleSet()
	SetDefaults	()
	SetRange	(2, Circle)
	SetObjRange	(10, 10)
	SetTexture	(21)
	CreateRule	()
	
	-- sand 11 texturieren (kleinerer Range)
	SetDefaults	()
	SetRange	(1, Circle)
	SetObjRange	(11, 11)
	SetTexture	(21)
	CreateRule	()
		
end

function SandRandTexturieren()
	-- Nach dem Sand den Sandrand texturieren...
	BeginRuleSet()
	SetDefaults	()
	SetRange	(3, Circle)
	SetObjRange	(10, 11)
	SetTexture	(20)
	CreateRule	()

	SetDefaults	()
	SetRange	(4, Circle)
	SetObjRange	(10, 11)
	SetTexture	(5)
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
	SetTexture	(4)
	CreateRule	()
	
	SetComment	("last Dreck unter Bäumen...")
	SetRange	(1, Circle)
	SetCondition(235)
	SetTexture	(5)
	CreateRule	()
end




function BergSpitzen ()
	-- kein gras auf bergen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 10)
	SetHeight	(40, 255)
	SetTexture	(7)
	CreateRule	()

	SetSteep	(10, 15)
	SetHeight	(40, 255)
	SetTexture	(27)
	CreateRule	()
	
	SetSteep	(15, 20)
	SetHeight	(40, 255)
	SetTexture	(7)
	CreateRule	()
end

function GebirgeSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(22, 28)
	SetTexture	(15)
	CreateRule	()
	
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(28, 32)
	SetTexture	(10)
	CreateRule	()
	
	SetSteepRel	(40)
	SetTexture	(12)
	CreateRule	()
	
	SetSteepRel	(50)
	SetTexture	(10)
	CreateRule	()
	
	SetSteepRel	(55)
	SetTexture	(15)
	CreateRule	()
	
	SetSteepRel	(75)
	SetTexture	(7)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(12)
	CreateRule	()
end

function SteinFurchen()
	-- ...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 40)
	SetTexture	(11)
	SetExposMin (19)
	CreateRule	()

	BeginRuleSet()
	SetSteepRel	(60)
	SetTexture	(11)
	SetExposMin (44)
	CreateRule	()
end

function GrasFlecken()
	-- ...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 1)
	SetPercent	(500)
	SetMarker	(224)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 6)
	SetCondition(224)
	SetRange	(1)
	SetMarker	(225)
	SetPercent	(6000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 4)
	SetCondition(225)
	SetRange	(1)
	SetMarker	(226)
	SetPercent	(3000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 3)
	SetCondition(226)
	SetRange	(1)
	SetMarker	(227)
	SetPercent	(2000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 2)
	SetCondition(227)
	SetRange	(1)
	SetMarker	(228)
	SetPercent	(1000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 1)
	SetCondition(228)
	SetRange	(1)
	SetMarker	(229)
	SetPercent	(2000)
	CreateRule	()

	-- texturieren:
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 6)
	SetCondition(224)
	SetRange	(1)
	SetTexture	(2)
	CreateRule	()

	SetCondition(225)
	SetTexture	(3)
	CreateRule	()

	SetCondition(226)
	SetTexture	(2)
	CreateRule	()

	SetCondition(227)
	SetTexture	(6)
	CreateRule	()

	SetCondition(228)
	SetTexture	(3)
	CreateRule	()

	SetCondition(229)
	SetTexture	(6)
	CreateRule	()
end


function FlachLandSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 2)
	SetTexture	(2)
	CreateRule	()
	
	SetSteepRel	(5)
	SetTexture	(4)
	CreateRule	()
	
	SetSteepRel	(10)
	SetTexture	(6)
	CreateRule	()
	
	SetSteepRel	(13)
	SetTexture	(3)
	CreateRule	()
	
	SetSteepRel	(17)
	SetTexture	(2)
	CreateRule	()
	
	SetSteepRel	(22)
	SetTexture	(6)
	CreateRule	()
	
	SetSteepRel	(30)
	SetTexture	(4)
	CreateRule	()
	
	SetSteepRel	(40)
	SetTexture	(6)
	CreateRule	()
	
	SetSteepRel	(60)
	SetTexture	(3)
	CreateRule	()
	
	SetSteepRel	(75)
	SetTexture	(2)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(5)
	CreateRule	()
	
	
end

-- erst die Aufstiege, dann die Gebirge!!!
--AufstiegeTexturieren()

--GebirgeSteepness()
SteinFurchen()
BergSpitzen ()


--SandRandTexturieren()
--DreckUnterBaeumen()
GrasFlecken()
FlachLandSteepness()
ExportAutoTexture()
