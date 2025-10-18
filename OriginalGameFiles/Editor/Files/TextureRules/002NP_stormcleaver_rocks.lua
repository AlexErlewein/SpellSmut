-- funktionen einbinden
dofile("AutoTexturerTools.lua")

-- initialisieren... (ja, das muss schon sein)
InitAutoTextureHelper()


comment = [[
-- Folgende Funktionen gibt es:
-- Erhöht einfach nur die Priorität um 1
-- Man sollte damit aber ganze RuleSets beginnen...
	BeginRuleSet()
-- ...und diese Funktion nehmen für Prioritätserhöhungen "für zwischendurch"
-- beide Funktionen machen übrigens dasselbe, es dient nur der Lesbarkeit
	IncreasePriority()
	
-- Setzt alle Werte (ausser Priority) zurück auf defaults
	SetDefaults	()
-- die default Werte sind:
	Height		= 1, 255
	Steep		= 0, 90
	Percent		= 10000
	Range		= 0
	Condition	= 0
	ExposureMin	= 0
	ExposureMax	= 0
	ObjectMin	= 0
	ObjectMax	= 0
	Marker		= 0
	Texture		= 1
		
-- erzeugt die Rule mit den zuvor angegebenen Werten
-- alles was danach kommt bezieht sich auf die nächste Rule
	CreateRule()

-- setzt die Werte einer Rule, selbsterklärend...
-- alle Werte werden auf Gültigkeit geprüft
	SetHeight(HeightMin, HeightMax)
	SetSteep(SteepMin, SteepMax)
	SetPercent(Percent)
	SetRange(Range, Type)	-- Type ist entweder Rectangle oder Circle
	SetCondition(Condition)
	SetMarker(Marker)
	SetTexture(Texture)

-- setzt die ExposureMin Abfrage (Vertiefung), ExposureMax wird zurückgesetzt
	SetExposMin(ExposureMin)
-- setzt die ExposureMax Abfrage (Erhöhung), ExposureMin wird zurückgesetzt
	SetExposMax(ExposureMax)
-- setzt Object ID Range der abzufragenden Objekte (z.b. ID 500-522)
	SetObjRange(ObjectIdMin, ObjectIdMax)
-- setzt abzufragendes Objekt (ObjectIdMin == ObjectIdMax)
	SetObject(ObjectId)

-- setzt einen Comment vor die aktuelle Rule (comment ist auch im .des)
-- der comment taucht nur bei der Rule auf für die er gesetzt wurde
	SetComment(Comment)
	
-- setzt nur HeightMax, HeightMin = HeightMax von voriger Rule
	SetHeightRel(HeightMax)
-- setzt nur SteepMax, SteepMin = SteepMax von voriger Rule
	SetSteepRel	(SteepMax)

-- addiert HeightAdd sowohl zu HeightMin als auch HeightMax
	AddHeight(HeightAdd)
-- addiert SteepAdd sowohl zu SteepMin als auch SteepMax
	AddSteep(SteepAdd)
	
-- mehr utility Funktionen auf Anfrage...
]]
comment = nil

-- Wenn man sich eingewöhnt hat an die neue Editierweise, kann man
-- den ganzen comment hier drüber (und diesen hier) löschen...


-- HIER GEHTS LOS:
-- variablendeklaration (muss nicht zentral an diesem punkt sein)
-- auch marker, percentages, heights, etc. können namen bekommen!
glitzerblau		= 3
braunfleckgras	= 13
blassesgras		= 15
braunerdreck	= 23
moossteine		= 19
hellerweg		= 20
waldboden		= 22
grassteine		= 24
steingras		= 25
hellrundsteine	= 30
feinerstein		= 31

-- Werte bleiben von Rule zu rule erhalten! (werden "durchgereicht")

-- test dummy objects
BeginRuleSet()
SetDefaults	()
SetHeight	(1, 7)
SetSteep	(0, 20)
SetRange	(5)
SetObject	(1)
SetTexture	(hellerweg)
CreateRule	()


-- test expos
BeginRuleSet()
SetDefaults	()
SetHeight	(1, 200)
SetSteep	(0, 20)
SetExposMax	(200)
SetTexture	(hellerweg)
CreateRule	()



-- schnee auf bergen
BeginRuleSet()
SetDefaults	()
SetComment	("schnee auf bergen")
SetHeight	(34, 255)
SetTexture	(10)
CreateRule	()

SetHeight	(29, 255)
SetTexture	(39)
CreateRule	()

-- ursprünglicher start
BeginRuleSet()
SetDefaults	()
SetComment	("Rules für 002 NP stormcleaver rocks")
SetHeight	(5, 7)
SetSteep	(18, 32)
SetPercent	(7500)
SetTexture	(braunerdreck)
CreateRule	()


BeginRuleSet()
SetDefaults	()
SetComment	("beckenböden")
SetHeight	(1, 4)
SetSteep	(0, 10)
SetTexture	(glitzerblau)
CreateRule	()

SetHeight	(1, 3)
SetSteep	(10, 50)
SetTexture	(moossteine)
CreateRule	()



BeginRuleSet()
SetDefaults	()
SetComment	("flecken ins gras")
SetHeight	(1, 18)
SetSteep	(1, 3)
SetPercent	(1500)
SetMarker	(249)
CreateRule	()

IncreasePriority()
SetSteep	(0, 5)
SetPercent	(8000)
SetRange	(1)
SetCondition(249)
SetMarker	(248)
CreateRule	()

IncreasePriority()
SetPercent	(4000)
SetRange	(1)
SetCondition(248)
SetMarker	(247)
CreateRule	()

IncreasePriority()
SetPercent	(10000)
SetRange	(0)
SetCondition(247)
SetMarker	(0)
SetTexture	(blassesgras)
CreateRule	()

SetCondition(248)
SetTexture	(blassesgras)
CreateRule	()

SetCondition(249)
SetTexture	(blassesgras)
CreateRule	()


BeginRuleSet()
SetDefaults	()
SetComment	("hochgebirge verschönern")
SetHeight	(19, 200)
SetSteep	(8, 20)
SetMarker	(250)
CreateRule	()

IncreasePriority()
SetPercent	(1000)
SetRange	(2)
SetCondition(250)
SetMarker	(251)
CreateRule	()

IncreasePriority()
SetSteep	(12, 16)
SetPercent	(5000)
SetRange	(1)
SetCondition(250)
SetMarker	(252)
CreateRule	()


SetCondition(251)
SetMarker	(252)
CreateRule	()

IncreasePriority()
SetPercent	(10000)
SetCondition(250)
SetMarker	(0)
SetTexture	(waldboden)
CreateRule	()

SetPercent	(5000)
SetCondition(251)
SetTexture	(waldboden)
CreateRule	()

SetSteep	(8, 20)
SetPercent	(2000)
SetCondition(250)
SetTexture	(waldboden)
CreateRule	()


BeginRuleSet()
SetDefaults	()
SetComment	("grünland im gebirge")
SetHeight	(19, 200)
SetSteep	(0, 12)
SetPercent	(3000)
SetTexture	(grassteine)
CreateRule	()

SetSteep	(8, 20)
SetTexture	(steingras)
CreateRule	()


BeginRuleSet()
SetDefaults	()
SetComment	("ab höhe 19 nur nach steepness texturen auf die landschaft klatschen")
SetHeight	(19, 200)
SetSteep	(0, 15)
SetTexture	(hellrundsteine)
CreateRule	()

SetSteepRel	(25)
SetTexture	(30)
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


BeginRuleSet()
SetDefaults	()
this_height = 10
h = this_height
SetComment	("ab höhe " .. this_height .. " nur nach steepness texturen auf die landschaft")
SetHeight	(h, 200)
SetSteep	(0, 6)
SetTexture	(braunfleckgras)
CreateRule	()

SetSteepRel	(24)
SetTexture	(blassesgras)
CreateRule	()

SetSteepRel	(35)
SetTexture	(feinerstein)
CreateRule	()

SetSteepRel	(50)
SetTexture	(29)
CreateRule	()

SetSteepRel	(90)
SetTexture	(27)
CreateRule	()


BeginRuleSet()
SetDefaults	()
SetComment	("nur nach steepness texturen auf die landschaft klatschen")
SetSteep	(0, 3)
SetTexture	(15)
CreateRule	()

SetSteepRel	(7)
SetTexture	(14)
CreateRule	()

SetSteepRel	(12)
SetTexture	(16)
CreateRule	()

SetSteepRel	(15)
SetTexture	(17)
CreateRule	()

SetSteepRel	(22)
SetTexture	(15)
CreateRule	()

SetSteepRel	(35)
SetTexture	(31)
CreateRule	()

SetSteepRel	(40)
SetTexture	(29)
CreateRule	()

SetSteepRel	(45)
SetTexture	(28)
CreateRule	()

SetSteepRel	(55)
SetTexture	(26)
CreateRule	()

SetSteepRel	(90)
SetTexture	(27)
CreateRule	()



BeginRuleSet()
SetDefaults	()
SetTexture	(3)
CreateRule	()

-- hiermit wird der export gestartet
-- das muss immer die letzte zeile sein!
-- export geht in filename.lua mit .des Endung
ExportAutoTexture()
