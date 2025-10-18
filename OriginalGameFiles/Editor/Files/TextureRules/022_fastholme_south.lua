dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

function GlobalSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 1)
	SetTexture	(6)
	CreateRule	()
	
	SetSteepRel	(3)
	SetTexture	(14)
	CreateRule	()

	SetSteepRel	(6)
	SetTexture	(6)
	CreateRule	()

	SetSteepRel	(8)
	SetTexture	(14)
	CreateRule	()
	
	SetSteepRel	(10)
	SetTexture	(6)
	CreateRule	()

	SetSteepRel	(12)
	SetTexture	(14)
	CreateRule	()

	SetSteepRel	(20)
	SetTexture	(13)
	SetPercent	(3000)
	CreateRule	()

	SetSteepRel	(22)
	SetTexture	(27)
	SetPercent	(5000)
	CreateRule	()

	SetSteepRel	(30)
	SetTexture	(10)
	SetPercent	(8000)
	CreateRule	()

	SetSteep	(0, 25)
	SetTexture	(6)
	SetPercent	(10000)
	CreateRule	()

	SetSteepRel	(45)
	SetTexture	(1)
	CreateRule	()

	SetSteepRel	(60)
	SetTexture	(10)
	CreateRule	()

	SetSteepRel	(90)
	SetTexture	(1)
	CreateRule	()
end

function SteinFurchen()
	-- ...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 40)
	SetTexture	(26)
	SetExposMin (20)
	CreateRule	()

	BeginRuleSet()
	SetSteepRel	(60)
	SetTexture	(19)
	SetExposMin (44)
	CreateRule	()
end

function GrasFlecken()
	-- ...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 9)
	SetPercent	(500)
	SetMarker	(224)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 9)
	SetCondition(224)
	SetRange	(1)
	SetMarker	(225)
	SetPercent	(6000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 9)
	SetCondition(225)
	SetRange	(1)
	SetMarker	(226)
	SetPercent	(3000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 9)
	SetCondition(226)
	SetRange	(1)
	SetMarker	(227)
	SetPercent	(2000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 5)
	SetCondition(227)
	SetRange	(1)
	SetMarker	(228)
	SetPercent	(1000)
	CreateRule	()

	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 9)
	SetCondition(228)
	SetRange	(1)
	SetMarker	(229)
	SetPercent	(2000)
	CreateRule	()

	-- texturieren:
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 9)
	SetCondition(224)
	SetRange	(1)
	SetTexture	(4)
	CreateRule	()

	SetCondition(225)
	SetTexture	(24)
	CreateRule	()

	SetCondition(226)
	SetTexture	(22)
	CreateRule	()
	
	SetCondition(226)
	SetTexture	(18)
	CreateRule	()

	SetCondition(227)
	SetTexture	(14)
	CreateRule	()

	SetCondition(228)
	SetTexture	(6)
	CreateRule	()

	SetCondition(229)
	SetTexture	(14)
	CreateRule	()
end

SteinFurchen()
GrasFlecken()
GlobalSteepness()

-- finally: export it...
ExportAutoTexture()
