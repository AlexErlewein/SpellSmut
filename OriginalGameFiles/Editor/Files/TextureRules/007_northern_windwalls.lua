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
	SetTexture	(20)
	CreateRule	()
	
	-- sand 11 texturieren (kleinerer Range)
	SetDefaults	()
	SetRange	(2, Circle)
	SetObjRange	(11, 11)
	SetTexture	(20)
	CreateRule	()
		
end

function SandRandTexturieren()
	-- Nach dem Sand den Sandrand texturieren...
	BeginRuleSet()
	SetDefaults	()
	SetRange	(3, Circle)
	SetObjRange	(10, 11)
	SetTexture	(21)
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


function GebirgeSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(22, 30)
	SetTexture	(10)
	CreateRule	()
	
	SetSteepRel	(40)
	SetTexture	(12)
	CreateRule	()
	
	SetSteepRel	(55)
	SetTexture	(13)
	CreateRule	()
	
	SetSteepRel	(75)
	SetTexture	(7)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(27)
	CreateRule	()
end

function FlachLandSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 2)
	SetTexture	(3)
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
	
	SetSteepRel	(21)
	SetTexture	(4)
	CreateRule	()
	
	
end

-- erst die Aufstiege, dann die Gebirge!!!
AufstiegeTexturieren()
GebirgeSteepness()

SandTexturieren()
SandRandTexturieren()
DreckUnterBaeumen()
FlachLandSteepness()
ExportAutoTexture()
