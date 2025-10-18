dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

function AufstiegeTexturieren()
	-- aufstiege texturieren...
	BeginRuleSet()
	SetDefaults	()
	SetRange	(2, Circle)
	SetObjRange	(1, 4)
	SetTexture	(18)
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
	SetTexture	(19)
	CreateRule	()

	SetCondition(225)
	SetTexture	(9)
	CreateRule	()

	SetCondition(226)
	SetTexture	(26)
	CreateRule	()

	SetCondition(227)
	SetTexture	(18)
	CreateRule	()

	SetCondition(228)
	SetTexture	(24)
	CreateRule	()

	SetCondition(229)
	SetTexture	(9)
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
	SetTexture	(12)
	CreateRule	()
	
	SetSteepRel	(75)
	SetTexture	(7)
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(15)
	CreateRule	()
end

function SteinFurchen()
	-- ...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 40)
	SetTexture	(11)
	SetExposMin (20)
	CreateRule	()

	BeginRuleSet()
	SetSteepRel	(60)
	SetTexture	(11)
	SetExposMin (44)
	CreateRule	()
end

function FlachLandSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 2)
	SetTexture	(19)
	CreateRule	()
	
	SetSteepRel	(5)
	SetTexture	(9)
	CreateRule	()
	
	SetSteepRel	(10)
	SetTexture	(26)
	CreateRule	()
	
	SetSteepRel	(13)
	SetTexture	(18)
	CreateRule	()
	
	SetSteepRel	(17)
	SetTexture	(20)
	CreateRule	()
	
	SetSteepRel	(21)
	SetTexture	(24)
	CreateRule	()
	
	
end

-- erst die Aufstiege, dann die Gebirge!!!
AufstiegeTexturieren()
GebirgeSteepness()

GrasFlecken()
FlachLandSteepness()
SteinFurchen()
ExportAutoTexture()
