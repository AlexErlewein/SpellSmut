dofile("AutoTexturerTools.lua")
InitAutoTextureHelper()

function GlobalSteepness()
	-- nur nach steepness texturen auf die landschaft klatschen
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 1)
	SetTexture	(2)
	CreateRule	()
	
	SetSteepRel	(3)
	SetTexture	(4)
	CreateRule	()

	SetSteepRel	(6)
	SetTexture	(4)
	CreateRule	()

	SetSteepRel	(8)
	SetTexture	(8)
	CreateRule	()

	SetSteepRel	(12)
	SetTexture	(2)
	CreateRule	()

	SetSteepRel	(20)
	SetTexture	(7)
	SetPercent	(3000)
	CreateRule	()

	SetSteepRel	(22)
	SetTexture	(8)
	SetPercent	(5000)
	CreateRule	()

	SetSteepRel	(30)
	SetTexture	(7)
	SetPercent	(8000)
	CreateRule	()

	SetSteep	(0, 25)
	SetTexture	(7)
	SetPercent	(5000)
	CreateRule	()

	SetSteepRel	(35, 40)
	SetTexture	(12)
	CreateRule	()
	
	SetSteepRel	(45)
	SetTexture	(21)
	CreateRule	()	

	SetSteepRel	(50)
	SetTexture	(15)
	CreateRule	()
	
	SetSteepRel	(55)
	SetTexture	(11)
	CreateRule	()


	SetSteepRel	(60)
	SetTexture	(15)
	CreateRule	()

	SetSteepRel	(75)
	SetTexture	(15)
	SetPercent	(5000)	
	CreateRule	()
	
	SetSteepRel	(76)
	SetTexture	(15)
	SetPercent	(10000)	
	CreateRule	()
	
	SetSteepRel	(90)
	SetTexture	(10)
	CreateRule	()
		
end

function SteinFurchen()
	-- ...
	BeginRuleSet()
	SetDefaults	()
	SetSteep	(0, 40)
	SetTexture	(7)
	SetExposMin (20)
	CreateRule	()

	BeginRuleSet()
	SetSteepRel	(60)
	SetTexture	(7)
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
	SetTexture	(2)
	CreateRule	()

	SetCondition(226)
	SetTexture	(4)
	CreateRule	()

	SetCondition(227)
	SetTexture	(8)
	CreateRule	()

	SetCondition(228)
	SetTexture	(26)
	CreateRule	()

	SetCondition(229)
	SetTexture	(8)
	CreateRule	()
end

SteinFurchen()
GrasFlecken()
GlobalSteepness()

-- finally: export it...
ExportAutoTexture()
