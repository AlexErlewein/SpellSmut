function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)

-- search for: FIXME, REMOVE

-- um die states durchzuzhlen, DO NOT MODIFY!
TutorialStateNum = 0

-- Dummy effekt um nicht vorh. cond. anzuzeigen
MissingConditionEffect = "BuildingFire"
MissingConditionLength = 3333

-- max. entfernung zu monument um es benutzen zu knnen
TutorialDefaultRange = 10

-- delay fr die beiden untoten tore, spielwiese geht zuerst auf, das andere nach x sekunden:
UntotenTorDelay = 3

--woker limit
UnitLimitAfterUpgrade = 20

-- wir haben hier einen (fast) rein linearen ablauf, von daher ist es am gnstigsten, einfach
-- linear zusammenhngende states zu erzeugen, anstatt globale events zu benutzen....



------------------------------------------------------------------------------------------------------------------------
-- Tutorial: The Beginning, set initial Quest States, erste Erzhlungen des Offsprechers...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "_IDLE", To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "TutorialIntroCutSceneIsOver", UpdateInterval = 5},
	},
	Actions = {
		QuestBegin{QuestId = 473},
		QuestBegin{QuestId = 474},
		--SetInfoText{Tag = "TutInfo001", String = "Selektieren Sie den Seelenfels und aktivieren Sie ihn unten in der Aktionsleiste. Falls Sie sterben, mssen Sie jetzt nicht mehr den ganzen Weg bis zu diesem Ort laufen."   , Color = ColorYellow},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo002", String = "Willkommen in der Welt von Spellforce!"   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo003", String ="In diesem Prolog wird Ihnen das Spiel erklrt. Beginnen wir mit einigen allgemeinen Informationen:"    , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo004", String = "Ihr Hauptcharakter im Prolog heit 'Tahira'. Sie ist eine Mischung aus Kmpferin und Magierin. Wir nennen den Hauptcharakter zuknftig 'Avatar'."   , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo005", String = "Wenn Sie den Prolog gelst haben, wird das Spiel mit dem von Ihnen vor dem Spielstart erstellten Avatar fortgesetzt."   , Color = ColorWhite} },
		[5] = { SetInfoText{Tag = "TutInfo006", String = "Immer, wenn Sie den Mauszeiger ber eine Schaltflche oder ein Objekt halten, erscheint ein Hilfe-Fenster unten links mit nheren Informationen."   , Color = ColorWhite} },
		[6] = { SetInfoText{Tag = "TutInfo007", String =  "Immer, wenn Sie aufgefordert werden, auf etwas zu klicken, ist ein Klick mit der linken Maustaste gemeint. Auf die rechte Maustaste wird bei Bedarf konkret hingewiesen."  , Color = ColorWhite} },
		[7] = { SetInfoText{Tag = "TutInfo267", String =  "Wenn Sie auf die Schaltflche 'Men' oben rechts klicken, knnen Sie das Spiel jederzeit speichern oder Spieleinstellungen verndern."  , Color = ColorWhite} },

		[8] = { SetInfoText{Tag = "TutInfo011", String = "Selektieren Sie Ihren Avatar indem Sie mit der linken Maustaste in der Spielwelt auf 'Tahira' klicken."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #1.a SELEKTION des Avatar
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsNpcSelected:new(Avatar)
cond:SetUpdateInterval(1)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}


TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo012", String = "Sehr gut. Sie knnen den sichtbaren Bildausschnitt mit den Cursortasten oder mit gedrckter rechter Maustaste verschieben. Sie knnen den Bildausschnitt ebenfalls verschieben, indem sie den Mauszeiger zum jeweiligen Bildschirmrand bewegen."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo013", String = "Eine selektierte Einheit wird durch einen farbigen Ring markiert. Eigene Einheiten erhalten einen grnen Ring, feindliche Einheiten einen roten Ring und neutrale oder verbndete Einheiten einen blauen Ring."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo014", String = "Unten links sehen Sie die aktuell selektierten Einheiten und einige zustzliche Informationen wie Name, Gesundheitszustand und Manamenge."   , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo015", String = "Mit einem Mausklick auf den Portrt-Button oben links knnen Sie jederzeit Ihren Avatar selektieren. Wenn Sie auf dem Portrt-Button die rechte Maustaste klicken, dann wird der Bildausschnitt zu der entsprechenden Einheit bewegt."   , Color = ColorWhite} },

		[5] = { SetInfoText{Tag = "TutInfo016", String = "Bewegen Sie 'Tahira' durch einen Klick mit der rechten Maustaste nach Osten den Weg entlang durch das offene Steintor bis zu dem 'Seelenfels', einem grossen Steinbrocken."   , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3276"},
		},
}}

------------------------------------------------------------------------------------------------------------------------
-- #2.a NAHE BEIM SEELENFELS / BINDSTONE ... ist das zufall das "Seelenfels" sich so anhrt wie "Celen Fell" ?? :)
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeBindstone", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo017", String = "Der Seelenfels bietet einem Avatar die Mglichkeit, seine Rune mit diesem Ort zu verbinden. Falls Sie sterben, erscheinen Sie an dem zuletzt verwendeten Seelenfels. Feinde knnen allerdings Ihre Verbindung zu einem Seelenfels unterbrechen, wodurch Sie einen aktivierten Seelenfels auch wieder verlieren knnen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo018", String = "Selektieren Sie den Seelenfels mit einem Klick."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #2.b SEELENFELS SELEKTIERT ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsMonumentSelected:new(183, 443, 1)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo019", String = "Am unteren Bildrand befindet sich die 'Aktionsleiste'. Hier ist nun ein neues Symbol fr 'Seelenfels aktivieren' erschienen. Klicken Sie auf das Symbol."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #2.c AN SEELENFELS GEBUNDEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsMonumentInUse{X = 183, Y = 442, Range = 1, UpdateInterval = 2},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo020", String = "Der Seelenfels leuchtet auf und ist nun aktiv. Sie sind nun mit diesem Seelenfels verbunden."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo021", String = "Unten rechts befindet sich die bersichtskarte. Schwarze Bereiche sind noch unerforscht und werden automatisch aufgedeckt, wenn Sie mit Einheiten in der Nhe sind. Ihr Avatar hat dabei einen besonders groen Sichtradius."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo022", String = "Die Punkte in der bersichtskarte haben unterschiedliche Farben. Grn steht fr Ihre eigenen, rot fr feindliche und blau fr neutrale oder verbndete Einheiten und Gebude. Einige besondere Objekte wie Monumente sind gelb markiert."   , Color = ColorWhite} },

		[4] = { SetInfoText{Tag = "TutInfo023", String = "Gehen Sie den Weg weiter nach Osten."   , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3277"},
		},
}}

------------------------------------------------------------------------------------------------------------------------
-- #3.a SPIELER IM 3RD PERSON BEREICH ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRange3rdPersonArea", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo024", String = "SpellForce bietet die Mglichkeit, das Spielgeschehen auch aus verschiedenen Ansichten und sogar der 'Verfolgerperspektive', d.h. einer Perspektive direkt hinter Ihrem Avatar, zu erleben."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo025", String = "Zur Vernderung der Perspektive drcken Sie die Tasten 'Bild hoch', um hineinzuzoomen und 'Bild runter', um herauszuzoomen. Oder sie drehen einfach das Mausrad."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo026", String = "Wenn Sie das Mausrad nach unten bewegen oder 'Bild runter' drcken, geht die Kamera in eine fast senkrechte Perspektive."   , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo027", String = "Wenn Sie nun das Mausrad nach oben drehen oder 'Bild hoch' drcken, sehen Sie die normalen isometrischen Ansichten aus unterschiedlichen Entfernungen."   , Color = ColorWhite} },

		[5] = { SetInfoText{Tag = "TutInfo028", String = "Wechseln Sie nun in die Verfolgerperspektive, indem Sie noch weiter heranzoomen. Dies ist nur mglich, wenn sich Ihr Avatar im Bildausschnitt befindet."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #3.b PERSPEKTIVE IN 3RD PERSON GEWECHSELT ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsIsoView:new())
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo029", String = "In der Verfolgerperspektive steuern Sie direkt Ihren Avatar mit den Cursortasten oder mit den Tasten 'ADSW'."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo030", String = "Wenn Sie die rechte Maustaste gedrckt halten, knnen Sie die Blickrichtung verndern. Ansonsten ist die Bedienung von SpellForce in dieser Perspektive identisch mit der isometrischen Ansicht."   , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo031", String = "Folgen Sie in der Verfolgerperspektive dem Weg nach Osten bis zum nchsten Steintor."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #3.c AM ENDE DES 3RD PERSON BEREICHS ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRange3rdPersonEndArea", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo032", String = "Sie knnen im Spiel jederzeit in die Verfolgerperspektive wechseln, die Bedienungserklrungen gehen aber davon aus, dass Sie die isometrische Ansicht verwenden."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo033", String = "Wechseln Sie mit dem Mausrad wieder in die normale isometrische Ansicht."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #3.d SPIELER WIEDER IN ISO PERSPEKTIVE ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsIsoView:new()
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo034", String = "Hinter der nchste Ecke lauert ein feindlicher 'Goblin'. Er stellt keine groe Gefahr dar. Wenn Sie den Mauszeiger ber ihn halten, zeigt Ihnen ein Balken seinen Gesundheitszustand."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo035", String = "Selektieren Sie Ihren Avatar und klicken Sie mit der rechten Maustaste auf den 'Goblin'. Ihr Avatar greift den 'Goblin' an. Sobald er besiegt ist, geht es weiter."   , Color = ColorYellow} ,
				SetGlobalFlagTrue{Name = "OpenDoor3280"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #4.a ERSTEN GEGNER (DER MIT SCHILD) GETTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureDead{NpcId = 3440},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo036", String = "Die Leiche des 'Goblins' leuchtet, wodurch gekennzeichnet wird, dass er einen Gegenstand dabei hat. Diesen Gegenstand knnen Sie an sich nehmen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo037", String = "Stellen Sie sich in die Nhe des toten Goblins und klicken Sie mit der rechten Maustaste auf die Leiche. Am linken Bildrand sehen Sie dann, welche Gegenstnde der Goblin bei sich trug. Nehmen Sie den Schild durch einen Klick mit, er wird automatisch in Ihr Inventar einsortiert."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #4.b SCHILD GELOOTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerHasHadGoblinShield", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo038", String = "Der Schild erhht die Rstungsklasse Ihres Avatars, wenn Sie ihn tragen. Mit einer hheren Rstungsklasse verlieren Sie weniger Lebenspunkte, wenn ein Gegner Sie mit einer Waffe trifft."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo039", String = "Um Ihr Inventar zu ffnen, klicken Sie den Rucksack unten in der Aktionsleiste oder die 'I'-Taste. Ein Fenster ffnet sich und links sind nun verschiedene Rubriken Ihres Inventars anwhlbar. Klicken Sie auf das 'Ring'-Symbol, er steht fr Ausrstungsgegenstnde."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #4.c IM INVENTORY ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(0)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo040", String = "Links sehen Sie nun unbenutzte Ausrstungsgegenstnde, in der Mitte die von Ihrem Avatar aktuell verwendeten Gegenstnde und rechts die aktuellen Daten Ihres Charakters, mit denen wir uns erst spter beschftigen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo041", String = "Um den Schild anziehen zu knnen, mssen Sie ihn zunchst an die Maus nehmen. Klicken Sie dazu auf den Schild und klicken Sie dann auf das noch freie Fach fr die linke Hand neben dem Oberkrper."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #4.d SPIELER HAT SCHILD ANGEZOGEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		AvatarHasItem{ItemId = 701, UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo042", String = "Schlieen Sie nun das Inventar mit einem Klick auf den Haken unten rechts im Fenster oder auf den Rucksack oder durch erneutes Drcken von 'I'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #4.e SPIELER HAT INVENTORY WIEDER VERLASSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo008", String = "In der oberen linken Ecke sehen Sie ein Portrt des Avatars. Schaltflchen dieser Art nennen wir Portrt-Buttons."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo009", String = "Der grne Balken im Portrt zeigt den Gesundheitszustand an. Wenn die Figur verwundet ist, verfrbt er sich je nach Schwere der Verletzung ber gelb nach rot. Wenn die Figur keine Lebenspunkte mehr hat, stirbt sie. Ihr Avatar regeneriert seine Lebenspunkte mit der Zeit wieder."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo010", String = "Der blaue Balken stellt Mana dar -  die magische Energie. Wenn eine Figur kein Mana mehr hat, kann sie keine Zaubersprche mehr ausfhren. Mana fllt sich ebenfalls mit der Zeit wieder auf."   , Color = ColorWhite} },

		[4] = { SetInfoText{Tag = "TutInfo043", String = "Folgen Sie dem Weg durch das nchste Steintor, bis Sie auf den verletzten 'Lev' treffen."   , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3281"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #5.a LEV ERREICHT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeLev", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo044", String = "Wenn Ihnen jemand einen Dialog anbietet, schwebt ber der Figur ein Symbol. Wenn diese Person fr die Hauptqueste relevant ist, handelt es sich um ein Ausrufezeichen. Falls die Person nur fr optionale Nebenquesten relevant ist, handelt es sich um ein Fragezeichen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo045", String = "Selektieren Sie Ihren Avatar, gehen Sie in die Nhe von 'Lev' und klicken Sie ihn mit der rechten Maustaste an, um einen Dialog zu beginnen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.b MIT LEV ERSTMALIG GEREDET, LEV BITTET UM HEILUNG ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "Q473LevBeggedForHeal", UpdateInterval = 5},
		IsGlobalFlagFalse{Name = "GDS_PlayerIsTalking", UpdateInterval = 5},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo046", String = "Sie verfgen ber einen Heilspruch. Wenn Sie einen Zauberspruch auf ein Ziel auslsen wollen, gibt es 2 Mglichkeiten:"   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo047", String = "Die einfachste Mglichkeit bietet das 'Click&Fight'-System. Selektieren Sie dazu 'Lev'. Unter dem Portrt-Button Ihres Avatars erscheinen nun alle sinnvollen Aktionen fr dieses Ziel. Die blaue Hand ist das Symbol fr den Heilspruch. Klicken Sie auf das Symbol, um 'Lev' zu heilen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.c DEN LEV GEHEILT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(FigureHasHealth{Percent = 25, NpcId = 3326, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		QuestSolve{QuestId = 474},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo048", String = "Mit dem 'Click&Fight'-System knnen Sie natrlich auch Zaubersprche auf gegnerische Einheiten auslsen oder Angriffskommandos geben. Wenn Sie eine feindliche Einheit selektieren, werden automatisch nur gegen Feinde sinnvolle Aktionen angeboten."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo049", String = "Alternativ dazu gibt es die klassische Methode. Selektieren Sie Ihren Avatar, klicken Sie danach in der Aktionsleiste den Heilspruch an und klicken Sie anschlieend in der Spielwelt auf den verwundeten 'Lev'. Wenn Sie den Zauberspruch auslsen knnen, erscheint ein grner Pfeil am Mauszeiger."   , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo050", String = "Sprechen Sie 'Lev' noch einmal an."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.d ERNEUT MIT LEV GEREDET, BELOHNUNG ABGEHOLT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		QuestState{QuestId = 475, State = StateActive, UpdateInterval = 5},
		IsGlobalFlagFalse{Name = "GDS_PlayerIsTalking", UpdateInterval = 5},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo051", String = "Sie haben als Belohnung zustzliche Erfahrungspunkte gewonnen und von dem Soldaten eine Zauberspruchrolle fr den Spruch 'Feuerball' erhalten."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo052", String =  "Wenn Sie eine bestimmte Menge an Erfahrungspunkten gesammelt haben, steigt Ihr Avatar eine Stufe auf, wird strker und kann neue Fhigkeiten erlernen. Sie erhalten Erfahrungspunkte durch das Besiegen von Gegnern und das Lsen von Questen."  , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo266", String =  "Wenn Sie sterben, verlieren Sie jedesmal eine geringe Menge Erfahrungspunkte."  , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo053", String = "Als nchstes soll Ihr Avatar den Zauberspruch, den Sie gerade erhalten haben, erlernen."   , Color = ColorWhite} },

		[5] = { SetInfoText{Tag = "TutInfo054", String = "ffnen Sie Ihr Inventar und klicken Sie links im Fenster das Symbol fr Zauberbuch an."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.e SPELLBOOK OFFEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(1)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo055", String = "Links sehen Sie nun das Inventar fr Zauberspruchrollen, rechts Ihr Zauberbuch und darber das sogenannte Zauber-Gedchtnis, momentan mit 9 freien Fchern."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo056", String = "Klicken Sie auf die Zauberspruchrolle im Inventar, um sie an den Mauszeiger zu nehmen. Klicken Sie dann auf ein beliebiges freies Feld in Ihrem Zauberbuch."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.f FEUERBALL SPRUCH IM ZAUBERBUCH ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(PlayerHasItem{ItemId = 1984, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo057", String = "Sie haben nun einen neuen Zauberspruch in Ihr Zauberbuch bertragen. Im Zauberbuch knnen Sie unzhlige davon eintragen. Sie knnen aber nur maximal 10 Zaubersprche gleichzeitig im Zauber-Gedchtnis auswendig lernen und benutzen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo058", String = "Lernen Sie den Zauberspruch 'Feuerball', indem Sie auf das Feuerball-Symbol in Ihrem Zauberbuch und danach in ein beliebiges freies Feld in Ihrem Zauber-Gedchtnis klicken."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.g FEUERBALL GELERNT (IM ZAUBERGEDCHTNIS) ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsSpellMemorized:new(1973)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo059", String = "Schlieen Sie nun Ihr Inventar."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #5.h INVENTAR GESCHLOSSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo060", String = "Folgen Sie dem Weg, bis Sie den 'Minotaurus' sehen."   , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3283"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #6.a BEIM MINOTAUREN DORT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeMinotaurus", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo061", String = "Benutzen Sie den Zauberspruch 'Feuerball', um den Minotauren zu besiegen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #6.b MINOTAURUS TOT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureDead{NpcId = 3441},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo062", String = "Manche Wesen sind teilweise oder ganz resistent gegen bestimmte Magiearten. Auch Ihr Avatar kann sich mit seltenen Gegenstnden, die er im Laufe des Spiels finden wird, besser gegen magische Angriffe schtzen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo063", String =  "Hinter dem nchsten Tor wartet ein Feuer-Elementarwesen auf Sie, welches vllig resistent gegen Feuermagie ist. Folgen Sie dem Weg."  , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #6.c SPIELER BEIM MINOTAURUS TOR ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureInRange{NpcId = Avatar, X = 300, Y = 351, Range = 8},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo064", String = "Versuchen Sie Ihren Zauberspruch Feuerball gegen das Feuer-Elementar einzusetzen. Wenn ein Wesen einem Zauberspruch widerstanden hat, sehen Sie weie abprallende Funken. Besiegen Sie danach das Feuer-Elementar im Nahkampf."   , Color = ColorYellow} ,
				SetGlobalFlagTrue{Name = "OpenDoor3292"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #7.a FEUERWESEN TOT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureDead{NpcId = 3442},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		SetGlobalFlagTrue{Name = "FireElementalDead"},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo065", String = "Das Feuer-Elementar hatte eine Helden-Rune und 4 Gegenstnde dabei. Nehmen Sie diese an sich."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #7.b ALLE ITEMS DES FEUERWESEN GELOOTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		-- counter in n0.lua der jedes einzelne item abfrgt, zur sicherheit falls spieler items einzeln lootet ...
		IsGlobalCounter{Name = "FeuerwesenItemCounter", Operator = IsEqual, Value = 5, UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo066", String = "Neben Ihrem Hauptcharakter stehen Ihnen bis zu fnf Helden gleichzeitig zur Verfgung. Die Helden sind Ihre strksten Verbndeten und knnen auch ber magische Fhigkeiten verfgen."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo067", String = "Die gerade von Ihnen gefundene Helden-Rune steht fr einen geschickten Fernkmpfer. Die Rune legt die Eigenschaften und Fhigkeiten des Helden fest. Im Spielverlauf werden Sie mit der Zeit weitere Runen finden und teilweise ltere Runen ersetzen."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo068", String = "Um einen Helden herbeizurufen, mssen Sie die Rune des Helden in Ihrer Runentafel, die Sie immer bei sich haben, einsetzen und ein Helden-Monument fr die Herbeirufung finden."   , Color = ColorWhite} },

		[4] = { SetInfoText{Tag = "TutInfo069", String = "ffnen Sie Ihr Inventar und gehen Sie in die Rubrik 'Runentafel'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #7.c RUNEBOARD OFFEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(2)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo070", String = "Links sehen Sie Ihre momentan nicht verwendeten Runen und rechts die in der 'Runentafel' eingesetzten Runen. Auf der oberen Hlfte der Runentafel befinden sich die Felder fr die Helden-Runen und unten die Felder fr die Arbeiter-Runen, unterteilt in helle und dunkle Rassen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo071", String = "Je nachdem welche Stufe Ihr Avatar hat, knnen Sie bis zu fnf Runen gleichzeitig verwenden. Klicken Sie auf die Rune des Helden und setzen Sie sie in eines der freien Felder oben in der Runentafel ein."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #7.d HERO RUNE NICHT MEHR IM INVENTAR ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(PlayerHasItem{ItemId = 3231, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo072", String = "Nun mssen Sie den Helden noch ausrsten. Sie haben einen Bogen, einen Dolch und zwei Rstungsteile erhalten. Gehen Sie in das Inventar und whlen Sie die Rubrik 'Ausrstung'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #7.e EQUIPMENT MEN OFFEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(0)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo073", String = "Auf der rechten Seite des Fensters sehen Sie nun 2 Portrts. Whlen Sie das untere Portrt fr Ihren Helden und geben Sie ihm die vier neuen Gegenstnde links in Ihrem Inventar. Der Bogen muss in die linke Hand, das ist das Fach auf der rechten Seite."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #7.f NEUE AUSRSTUNG DEM HELDEN GEGEBEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerHasItem{ItemId = 693, Equipment = EquipmentHero, UpdateInterval = 1},
		PlayerHasItem{ItemId = 2325, Equipment = EquipmentHero, UpdateInterval = 1},
		PlayerHasItem{ItemId = 3265, Equipment = EquipmentHero, UpdateInterval = 1},
		PlayerHasItem{ItemId = 3266, Equipment = EquipmentHero, UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo074", String = "Wenn Ihr Avatar oder ein Held einen Gegenstand nicht benutzen kann, so wird dieser mit einem roten Hintergrund markiert. Schlieen Sie Ihr Inventar."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #7.g INVENTAR GESCHLOSSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo075", String = "Folgen Sie dem Weg bis zu dem groen Monument. Es handelt sich dabei um ein Helden-Monument."   , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3289"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #8.a BEIM HELDENMONUMENT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeHeroMonument", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo076", String = "Gehen Sie dicht an das Helden-Monument, selektieren Sie es und klicken Sie auf das 'Runensymbol' unten in der Aktionsleiste."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #8.b HELDENMONUMENT BERNOMMEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsMonumentInUse{X = 342, Y = 315, Range = 1 , UpdateInterval = 2},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo268", String = "Unten links im Selektionsfenster erscheint auer dem Helden-Monument ein Symbol mit einer Hand. Dort knnen Sie die Runenkraft Ihres Avatars ablesen."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo269", String = "Jedesmal, wenn Sie einen Helden oder spter auch Arbeiter herbeirufen, verlieren Sie etwas Runenkraft und die Herbeirufungen dauern lnger. Die Runenkraft regeneriert sich mit der Zeit automatisch."   , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo077", String = "Nun knnen Sie die Herbeirufung des Helden auslsen. Selektieren Sie das Monument und klicken Sie unten in der Aktionsleiste auf das Symbol fr den Helden. Es dauert dann einige Sekunden, bis der Held erscheint."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #8.c HELD ERSCHEINT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerHasCalledHeroToAction", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo078", String = "Oben links ist nun ein zweiter 'Portrt-Button' fr Ihren neuen Helden erschienen. Sie knnen den Helden nun kommandieren."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo079", String = "Um mehrere Einheiten gleichzeitig zu selektieren, knnen Sie in der Spielwelt die linke Maustaste gedrckt halten und einen Rahmen um beide Figuren ziehen. Sobald Sie die linke Maustaste loslassen, wird die Selektion festgelegt."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo184", String = "Sie knnen Kampfeinheiten auch zu Gruppen zusammenschlieen. Dazu selektieren Sie zunchst die Einheiten. Klicken Sie dann auf eine der kleinen Schaltflchen in der Mitte des oberen Bildschirmrandes. Sie knnen auch die Taste STRG gedrckt halten und eine Zifferntaste von 1-6 fr die entsprechende Gruppe whlen." , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo185", String = "Wenn Sie eine Gruppe definiert haben, erscheint ein 'Portrt-Button' am oberen Bildrand mit der Anzahl der Einheiten in der Gruppe. Die Funktionalitt des 'Portrt-Buttons' ist mit der Ihres Avatars identisch." , Color = ColorWhite} },
		[5] = { SetInfoText{Tag = "TutInfo186", String = "Sie knnen dann sehr schnell eine Gruppe selektieren, indem Sie den entsprechenden Portrt-Button anklicken oder eine Zifferntaste von 1-6 drcken." , Color = ColorWhite} },

		[6] = { SetInfoText{Tag = "TutInfo080", String = "Folgen Sie dem Weg weiter nach Sden."   , Color = ColorYellow} ,
				SetGlobalFlagTrue{Name = "OpenDoor3290"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #9.a BEI DEN UNTOTEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeUndeadCity", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo081", String = "Es steht Ihnen ein Kampf mit 'Untoten' bevor. Gemeinsam mit Ihrem Helden knnen Sie diesen Kampf gewinnen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo082", String = "Setzen Sie Ihre Magie ein und besiegen Sie die 'Untoten'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #9.b ALLE UNTOTEN SIND ENDGLTIG TOT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureDead{NpcId = 3443},
		FigureDead{NpcId = 3652},
		FigureDead{NpcId = 3655},
		FigureDead{NpcId = 3651},
		FigureDead{NpcId = 3654},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo083", String = "Sehr gut! Einer der 'Untoten' hat einen wertvollen Edelstein dabei. Nehmen Sie ihn mit."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #9.c EDELSTEIN GELOOTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerHasItem{ItemId = 2472, UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo084", String = "Falls Sie noch einige weitere Testkmpfe durchfhren wollen, biegen Sie hier nach Norden ab. Ansonsten folgen Sie dem Weg weiter nach Sden."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #9.d BEI DEN BEIDEN TOREN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureInRange{NpcId = Avatar, X = 247, Y = 286, Range = 15},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		SetGlobalFlagTrue{Name = "OpenDoor3306"},
		SetNpcTimeStamp{Name = "UntotenTorTimer"},
	},
}
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsNpcTimeElapsed{Name = "UntotenTorTimer", Seconds = UntotenTorDelay, UpdateInterval = 5},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		SetGlobalFlagTrue{Name = "OpenDoor3305"},
	},
}
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeCloseToMerchant", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo085", String = "Folgen Sie dem Weg bis zu dem Hndler. Hndler sind durch eine sich drehende Mnze ber dem Kopf hervorgehoben."   , Color = ColorYellow} ,
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #10.a BEIM HNDLER ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeMerchant", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo086", String = "Bei einem Hndler knnen Sie Gegenstnde jeder Art kaufen und verkaufen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo087", String = "Gehen Sie in die Nhe des Hndlers und sprechen Sie den Hndler an, indem Sie ihn mit der rechten Maustaste anklicken. Es erscheint ein Fenster mit dem Hndlermen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #10.b HANDELSMEN OFFEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(5)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo088", String = "Im Fenster links sehen Sie Ihre Gegenstnde und rechts die Gegenstnde des Hndlers. In der Mitte ist das verfgbare Geld und der Preis der ausgewhlten Gegenstnde zu sehen."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo089", String = "100 Kupferstcke entsprechen einem Silberstck und 100 Silberstcke wiederum entsprechen einem Goldstck."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo090", String = "Alle Gegenstnde sind in SpellForce in 5 Kategorien eingeteilt. Die 5 Symbole neben Ihrem Inventar und dem Inventar des Hndlers sind abgedunkelt, falls Sie oder der Hndler in dieser Kategorie ber keinen Gegenstand verfgen."   , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo091", String = "Sie wollen nun den Edelstein verkaufen, um Geld fr den Einkauf zu erhalten."   , Color = ColorWhite} },

		[5] = { SetInfoText{Tag = "TutInfo092", String = "Whlen Sie das unterste Symbol fr die Kategorie 'Quest- und Wertgegenstnde'. Klicken Sie auf den Edelstein. Der angebotene Gegenstand wird grn markiert und in der Mitte sehen Sie den Preis, den der Hndler bezahlen will. Klicken Sie auf 'Verkaufen'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #10.c EDELSTEIN VERKAUFT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(PlayerHasItem{ItemId = 2472, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo093", String = "Mit dem Geld wollen Sie sich nun etwas anderes kaufen. Klicken Sie auf die Rubrik 'Runen' und erwerben Sie die 'Menschen-Arbeiter-Rune'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #10.d MENSCHEN ARBEITER RUNE GEKAUFT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerHasItem{ItemId = 783, UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo094", String = "Beenden Sie den Handel durch einen Klick auf den Haken unten rechts im Fenster oder die 'ESC'-Taste."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #10.e HANDELSMEN GESCHLOSSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(5))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo095", String = "ffnen Sie Ihr Inventar, whlen Sie links die Rubrik 'Runentafel' aus und legen Sie die gerade erworbene Menschen-Arbeiter-Rune in das Fach mit dem Menschen-Portrt unten links in der Runentafel."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #10.f MENSCHENRUNE INS RUNEBOARD GELEGT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(PlayerHasItem{ItemId = 783, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo096", String = "Schlieen Sie nun Ihr Inventar."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #10.g INVENTAR GESCHLOSSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo097", String = "Folgen Sie dem Weg bis zum Seelenfels."   , Color = ColorYellow} ,
				SetGlobalFlagTrue{Name = "OpenDoor3307"},
		},
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.a AM ZWEITEN SEELENFELS ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeSecondBindstone", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo098", String = "Selektieren Sie den Seelenfels und aktivieren Sie ihn unten in der Aktionsleiste. Falls Sie sterben, mssen Sie jetzt nicht mehr den ganzen Weg bis zu diesem Ort laufen."   , Color = ColorYellow} ,
				SetGlobalFlagTrue{Name = "OpenDoor3307"},
		},
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.b SPIELER GEBUNDEN AM ZWEITEN SEELENFELS ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsMonumentInUse{X = 179, Y = 217, Range = 1 , UpdateInterval = 2},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		EnableDialog{NpcId = 3325},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo099", String = "Von einem Seelenfels knnen Sie zu jedem anderen Seelenfels reisen, den Sie bereits aktiviert haben. Dazu selektieren Sie Ihren Avatar und gehen zum Seelenfels, klicken mit der rechten Maustaste auf den Seelenfels und whlen den Zielort."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo100", String = "Wenn Sie mchten, knnen Sie dies jetzt ausprobieren, ansonsten folgen Sie dem Weg weiter bis zu dem Menschen-Monument."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.c BEI JOSHUA & DEM MENSCHEN MONUMENT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerInRangeJoshua", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
--		[1] = { SetInfoText{Tag = "TutInfo101", String = "Wenn Sie sterben, erstehen Sie am zuletzt verwendeten Seelenfels wieder auf. Feinde knnen allerdings Ihre Verbindung zu einem Seelenfels unterbrechen, wodurch Sie einen aktivierten Seelenfels auch wieder verlieren knnen."   , Color = ColorWhite} },

		[1] = { SetInfoText{Tag = "TutInfo102", String = "Reden Sie mit 'Joshua', dem Mann direkt neben dem Monument."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.d MIT JOSHUA GEREDET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		QuestState{QuestId = 475, State = StateSolved, UpdateInterval = 5},
		IsGlobalFlagFalse{Name = "GDS_PlayerIsTalking", UpdateInterval = 5},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo103", String = "Sie haben nun einen neuen Auftrag erhalten. ffnen Sie Ihr Inventar und whlen sie die Seite 'Questbuch'."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.e QUESTBOOK OFFEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(4)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo104", String = "In der Mitte des Fensters sehen Sie alle Ihre aktuellen noch nicht abgeschlossenen Questen und rechts eine Detailansicht der momentan angewhlten Queste."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo105", String = "Sie haben die Queste 'Die verschollene Rune' erhalten. Wenn Sie die Queste anklicken, erscheinen rechts die einzelnen Schritte dieser Queste. Bereits gelste Schritte werden abgedunkelt angezeigt."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo106", String = "Wenn Sie den Mauszeiger ber einen dieser einzelnen Schritte halten, erscheint zustzlich unten links ein Hilfe-Fenster mit Informationen, falls Sie etwas vergessen haben sollten."   , Color = ColorWhite} },

		[4] = { SetInfoText{Tag = "TutInfo107", String = "Schlieen Sie Ihr Inventar."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.f INVENTAR & QUESTBOOK WIEDER ZU ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo108", String = "Gehen Sie in die Nhe des Monuments, selektieren Sie das Monument und klicken Sie auf das 'Runensymbol' unten in der Aktionsleiste."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.g MENSCHEN MONUMENT GECLAIMED ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsMonumentInUse{X = 206, Y = 214, Range = 1 , UpdateInterval = 2},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo109", String = "In dem Augenblick, in dem Sie ein Arbeiter-Monument belegen, wird es ernst. Wenn Feinde Ihre neu entstehenden Siedlungen entdecken, werden sie alles daransetzen, sie mglichst schnell zu zerstren. Auf dieser Karte knnen Sie sich aber Zeit lassen."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo110", String = "Nun knnen Sie die Herbeirufung von menschlichen Arbeitern auslsen. Selektieren Sie das Monument und klicken Sie unten in der Aktionsleiste auf das Symbol fr Arbeiter."   , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo111", String = "Der Arbeiter erscheint nach einigen Sekunden. Sie knnen das Symbol auch mehrfach anklicken, um weitere Arbeiter in Auftrag zu geben. Produzieren Sie wenigstens 5 Arbeiter."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.h FNF ARBEITER(INNEN) HERBEIGERUFEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerUnitExists{UnitId = 0, Amount = 5, UpdateInterval = 5, NoWorkers = FALSE},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo112", String = "Wenn Sie das Monument selektiert haben, sehen Sie unten links Zahlen fr Ihre Bevlkerungsbegrenzung. Die oberen Zahlen geben an, wie viele Arbeiter dieser Rasse Sie momentan haben und maximal haben knnen."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo113", String = "Sie knnen momentan bis zu 20 Arbeiter produzieren. Die Anzahl der maximalen Arbeiter erhht sich, wenn Sie grere Haupthuser bauen."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo114", String = "Oben rechts befindet sich nun ein Portrt-Button fr menschliche Arbeiter. Die Zahl gibt an, wie viele menschliche Arbeiter momentan keiner Arbeit nachgehen. Mit einem Klick auf den Portrt-Button knnen Sie einen freien Arbeiter selektieren."   , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo115", String = "Die Arbeiter knnen, je nach Rasse, verschiedene Rohstoffe abbauen. Menschliche Arbeiter knnen Bume fllen, im Steinbruch arbeiten oder Eisenerz abbauen."   , Color = ColorWhite} },
		[5] = { SetInfoText{Tag = "TutInfo116", String = "Links neben dem Monument befindet sich ein Steinbruch und rechts daneben ein Erzvorkommen. Der nchste Wald befindet sich westlich."   , Color = ColorWhite} },
		[6] = { SetInfoText{Tag = "TutInfo117", String = "Um Arbeiter einen Rohstoff abbauen zu lassen, selektieren Sie einen oder mehrere Arbeiter und klicken dann mit der rechten Maustaste direkt auf den Baum, Felsen oder das Erzvorkommen. Dazu drfen ausschlielich Arbeiter in der Selektion sein."   , Color = ColorWhite} },
		[7] = { SetInfoText{Tag = "TutInfo118", String = "Am oberen Bildschirmrand sehen Sie, welche Menge an Rohstoffen Sie bereits abgebaut haben. Mit Rohstoffen knnen Sie Gebude errichten lassen oder Kampf-Einheiten an einem Monument herbeirufen."   , Color = ColorWhite} },

		[8] = { SetInfoText{Tag = "TutInfo119", String = "Selektieren Sie Arbeiter und schicken Sie sie mit der rechten Maustaste zum Baumfllen. Lassen Sie sie Steine und Erz abbauen, bis Sie wenigstens 50 Einheiten von jedem der drei Rohstoffe haben."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.i MINDESTMENGE HOLZ, STEIN & EISEN ABGEBAUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerHasGood{Good = GoodBoard, Amount = 50, Side = SideLight, UpdateInterval = 10},
		PlayerHasGood{Good = GoodStone, Amount = 50, Side = SideLight, UpdateInterval = 10},
		PlayerHasGood{Good = GoodIron, Amount = 50, Side = SideLight, UpdateInterval = 10},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo120", String = "Sehr gut! Sie haben jetzt genug Rohstoffe, um erste Gebude zu errichten."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo121", String = "Selektieren Sie einen beliebigen Arbeiter und klicken Sie auf das Bau-Symbol unten in der Aktionsleiste. Es erscheint eine Auswahl von Gebuden. Klicken Sie die 'Holzfllerhtte' an und whlen Sie in der Spielwelt einen Standort in der Nhe des Waldes."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.j HOLZFLLER GEBUDE WIRD GEBAUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 4, OnlyWhenBuiltUp = FALSE, UpdateInterval = 5},		-- Holzfller
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo122", String = "Der gewhlte Arbeiter beginnt nun, das Gebude zu errichten. Sie knnen weitere Arbeiter selektieren und mit einem Rechtsklick zustzlich zu der Baustelle schicken, falls Sie das Gebude schneller errichten lassen wollen."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo123", String = "Whlen Sie nun andere Arbeiter aus und bauen Sie auerdem noch einen Steinbruch in der Nhe der Felsen und eine Mine bei dem Erzvorkommen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.k STEINBRUCH UND MINE WERDEN ERRICHTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 7, OnlyWhenBuiltUp = FALSE, UpdateInterval = 10},		-- Steinbruch
		PlayerBuildingExists{BuildingId = 14, OnlyWhenBuiltUp = FALSE, UpdateInterval = 10},	-- Mine
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo124", String = "In jedem dieser Rohstoff-Gebude knnen bis zu 5 Arbeiter zu sogenannten Handwerkern aufsteigen. Handwerker haben andere Kleidung und spezielles Werkzeug und sind doppelt so effizient wie einfache Arbeiter."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo125", String = "Wenn Sie ein fertiges Gebude selektieren, dann knnen Sie unten links im Selektionsfenster sehen, wie viele Handwerker bereits diesem Gebude zugeordnet sind. Wenn Sie ein leeres Symbol anklicken und noch ein freier Arbeiter verfgbar ist, wird er dem Gebude zugewiesen. Wenn Sie auf ein belegtes Symbol klicken, wird ein Arbeiter freigesetzt."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo126", String = "Arbeiter, die das Gebude errichtet haben, bernehmen automatisch die freien Arbeitspltze des Gebudes soweit verfgbar."  , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo127", String = "Wenn Sie einen selektierten Arbeiter mit der rechten Maustaste zu einem Gebude schicken, knnen Sie freie Arbeitspltze belegen. So suchen Arbeiter, die z.B. Bume fllen, automatisch nach freien Pltzen in Holzfllergebuden und besetzen diese nach kurzer Zeit."   , Color = ColorWhite} },

		[5] = { SetInfoText{Tag = "TutInfo128", String = "Warten Sie, bis alle drei Gebude fertiggestellt sind. Falls ein Gebude nicht mehr weitergebaut wird, haben Sie versehentlich alle Arbeiter von der Baustelle abgezogen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.l HOLZFLLER, STEINBRUCH UND MINE EXISTIEREN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 4, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Holzfller
		PlayerBuildingExists{BuildingId = 7, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Steinbruch
		PlayerBuildingExists{BuildingId = 14, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Mine
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo129", String = "Nun sollten Ihre Rohstoffe wesentlich schneller ansteigen. Behalten Sie die einzelnen Lagerbestnde im Auge und weisen Sie bei Bedarf Arbeitern eine andere Ttigkeit zu."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo130", String = "Wenn Sie eine grere Armee rekrutieren wollen, bentigen Sie Nahrungsmittel. Die Menschen sind sehr flexibel und knnen Fische fangen, Tiere jagen oder zchten und Getreide anbauen."   , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo131", String = "In der Umgebung Ihrer Basis befinden sich zahlreiche Tiere. Bauen Sie ein Jagdhaus, um sich Nahrungsmittel zu beschaffen. Lassen Sie auerdem das kleine Haupthaus errichten, damit Sie ber bis zu 30 Arbeiter verfgen."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.m JAGDHTTE UND KLEINES HAUPTHAUS EXISTIEREN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 2, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Kleines Haupthaus
		PlayerBuildingExists{BuildingId = 9, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Jgerhtte
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo132", String = "Sie knnen bis zu 5 Arbeiter in das Jagdhaus schicken, um schneller Nahrungsmittel zu erhalten. Die Menge Ihrer gelagerten Nahrungsmittel bestimmt die maximale Gre Ihrer Armee."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo265", String = "Durch die Fahnen an den Gebuden erkennt man, welchem Spieler die Gebude gehren und ob gegenwrtig Arbeiter in diesem Gebude arbeiten."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo133", String = "Wenn Sie genau hinsehen, knnen Sie in dem See hinter dem Menschen-Monument die Fischvorkommen entdecken. Am Seeufer stehen einige Beerenbsche, diese dienen allerdings nur als Nahrung fr Elfen."   , Color = ColorWhite} },

		[4] = { SetInfoText{Tag = "TutInfo134", String = "Nun sollten Sie etwas fr die Verteidigung Ihrer Siedlung tun. Errichten Sie zwei Trme in dem durch Steinplatten markierten Bereich in der Nhe des Erzvorkommens, da Feinde vermutlich aus dieser Richtung angreifen werden."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #11.n ZWEI TRME BEI DEN GOBLINS BAUEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 13, OnlyWhenBuiltUp = TRUE, Amount = 2, UpdateInterval = 10},	-- 2 Schtzentrme
		BuildingInRange{X = 224, Y = 189, Range = 15, Owner = OwnerPlayer, BuildingId = 13, UpdateInterval = 10},
		--BuildingInRange{X = 222, Y = 183, Range = 6, Owner = OwnerPlayer, BuildingId = 13, UpdateInterval = 20},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo135", String = "Einige 'Goblins' greifen Ihre Siedlung an. Sie werden gleich ein Alarmsignal hren. Zustzlich weist ein rotes Symbol in der bersichtskarte auf den Ort des Angriffs hin. Verteidigen Sie Ihre Stadt mit dem Avatar und dem Helden."   , Color = ColorYellow} ,
				SetGlobalFlagTrue{Name = "OpenDoor3334"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #12.a GOBLINS ANGRIFF KOMMANDO GEBEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "Door3334NowOpen", UpdateInterval = 10},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		Goto{X = 204, Y = 208, NpcId = 3659, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 205, Y = 208, NpcId = 3660, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 205, Y = 209, NpcId = 3661, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 203, Y = 208, NpcId = 3662, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 204, Y = 207, NpcId = 3663, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 204, Y = 208, NpcId = 3664, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 204, Y = 209, NpcId = 3665, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
		Goto{X = 205, Y = 207, NpcId = 3666, Range = 15, WalkMode = Run, GotoMode = GotoContinous},
	},
}

------------------------------------------------------------------------------------------------------------------------
-- #12.b GOBLIN ANGREIFER TOT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureDead{NpcId = 3659},
		FigureDead{NpcId = 3660},
		FigureDead{NpcId = 3661},
		FigureDead{NpcId = 3662},
		FigureDead{NpcId = 3663},
		FigureDead{NpcId = 3664},
		FigureDead{NpcId = 3665},
		FigureDead{NpcId = 3666},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo136", String = "Sehr gut, die Angreifer sind geschlagen. Sie knnen brigens immer wenn ein Alarmsignal ertnt durch Drcken der 'SPACE'-Taste (Leertaste) sofort zum Ort des Geschehens wechseln."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo137", String = "Falls Ihre Trme beschdigt sind, knnen Sie diese wieder reparieren lassen. Selektieren Sie dazu einen oder mehrere Arbeiter und klicken Sie mit der rechten Maustaste auf das beschdigte Gebude."   , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo138", String = "An einem Menschen-Monument knnen Sie nicht nur Arbeiter, sondern auch menschliche Krieger und Magier herbeirufen."   , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo139", String = "Die an den Monumenten herbeigerufenen Krieger sind zwar alleine nicht so stark wie Ihr Avatar oder Ihre Helden, Sie knnen mit ausreichend Rohstoffen dafr aber ganze Armeen produzieren."   , Color = ColorWhite} },

		[5] = { SetInfoText{Tag = "TutInfo140", String = "Es ist an der Zeit, eine Armee aufzustellen. Errichten Sie eine Schmiede."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #12.c SCHMIEDE ERRICHTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 75, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Schmiede
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo141", String = "In der Schmiede werden automatisch Waffen und Rstungen fr Kampfeinheiten hergestellt. Wenn Sie ber mehrere Schmieden verfgen, knnen Sie schneller Kampfeinheiten produzieren."   , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo142", String = "Auch Kampfeinheiten werden am Menschen-Monument herbeigerufen. Wenn Sie einen Sammelpunkt fr neue Einheiten festlegen mchten, selektieren Sie das Menschen-Monument und klicken Sie mit der rechten Maustaste auf den Zielort. Das Erscheinen einer kleinen Fahne zeigt an, dass produzierte Kampfeinheiten sich an diesem Punkt sammeln werden."   , Color = ColorWhite} },
--		[3] = { SetInfoText{Tag = "TutInfo143", String = "ALTENATIVE"   , Color = ColorWhite} },
--		[4] = { SetInfoText{Tag = "TutInfo144", String = "Auch Kampfeinheiten werden am Menschen-Monument herbeigerufen. Wenn Sie einen Sammelpunkt fr neue Einheiten festlegen mchten, selektieren Sie das Menschen-Monument, klicken Sie unten links im Selektionsfenster auf das Symbol fr 'Sammelpunkt' und klicken Sie in der Spielwelt auf den Zielort."   , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo145", String = "Selektieren Sie nun das Menschen-Monument und produzieren Sie wenigstens 3 Rekruten und 3 Spher. Falls Sie eine Einheit nicht produzieren knnen, finden Sie im Hilfe-Fenster einen rot markierten Text als Hinweis auf die Ursache, z.B. ein fehlendes oder nicht besetztes Gebude oder zu wenig Rohstoffe."   , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #12.d JE DREI SCOUTS & REKRUTEN ERSCHAFFEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerUnitExists{UnitId = 543, Amount = 3 , UpdateInterval = 10},	-- Rekruten
		PlayerUnitExists{UnitId = 544, Amount = 3 , UpdateInterval = 10},	-- Scouts
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo146", String = "Die Orks verfgen ber eigene Patrouillen, die nach Feinden suchen. Wenn eine solche Patrouille Ihre Siedlung oder Krieger von Ihnen entdeckt, geht sie nach kurzer Zeit zurck in das feindliche Hauptlager und schlgt Alarm."   , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo147", String = "Gleich wird eine Patrouille Ihre Siedlung entdecken. Ein gelbes Symbol erscheint in diesem Moment auf der bersichtskarte. Vernichten Sie die Gegner, bevor sie entkommen."   , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3331"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #13.a SCOUTGRUPPE TOT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		FigureDead{NpcId = 3613},
		FigureDead{NpcId = 3614},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo148", String = "Jetzt werden Sie zwar nicht direkt angegriffen, nach einiger Zeit wird das Hauptlager aber die Patrouille vermissen und nach ihr suchen lassen. Sie haben aber Zeit gewonnen und sollten nun schnell weitere Spher und Rekruten produzieren." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo149", String = "Es ist wichtig, dass Sie die Gebude in feindlichen Lagern mglichst schnell zerstren, denn dort werden immer wieder neue Gegner rekrutiert." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo150", String = "Um eine grere Armee zu produzieren, bentigen Sie mehr Nahrungsmittel. Selektieren Sie Ihr Menschen-Monument." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.b MENSCHEN MONUMENT SELEKTIERT ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsMonumentSelected:new(206, 214, 1)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo151", String = "Die unteren Zahlen in dem Selektionsfenster unten links geben an, wie viele Kampfeinheiten Sie haben und maximal haben knnen. Der Maximalwert ist momentan 10." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo152", String = "In Haupthusern knnen Sie die maximale Armeegre erhhen. Dies kostet Nahrungsmittel. Selektieren Sie Ihr kleines Haupthaus." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.c KLEINES HAUPTHAUS SELEKTIERT ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsBuildingSelected:new(2, 0, 0, 1)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 2, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Kleines Haupthaus
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo153", String = "Unten in der Aktionsleiste sehen Sie nun ein Symbol fr Nahrungsmittel. Wenn Sie den Mauszeiger darber halten, werden die Kosten fr diese Aufwertung im Hilfe-Fenster angezeigt." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo154", String = "Wenn Sie das Symbol einmal anklicken erhht sich fr 100 Nahrungsmitteleinheiten die maximale Anzahl der Kampfeinheiten von 10 auf 15. Die Erhhung von 15 auf 20 Einheiten kostet bereits 200 Nahrungsmitteleinheiten." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo155", String = "Erhhen Sie nun die maximale Anzahl Ihrer Kampfeinheiten auf wenigstens 20 Einheiten, indem Sie das Symbol zweimal anklicken. Falls das Symbol abgedunkelt ist, haben Ihre Jger noch nicht ausreichend Nahrungsmittel beschafft und Sie mssen etwas warten." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.d EINHEITENLIMIT AUF 20 ERHHT ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsUnitLimit:new(1, UnitLimitAfterUpgrade, 0)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo156", String = "Mit dem kleinen Haupthaus knnen Sie den Maximalwert auf bis zu 30 Kampfeinheiten erhhen. Mit dem mittleren und groen Haupthaus erhalten Sie spter weitere Mglichkeiten, den Maximalwert zu erhhen." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo157", String = "Wenn Sie spter einmal zwei verbndete Rassen gleichzeitig spielen, so gilt der Maximalwert der Kampfeinheiten fr die gemeinsame Armee, dafr teilen die Rassen aber auch ihre Nahrungsmittel." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo158", String = "Produzieren Sie weitere Spher und Rekruten und zerstren Sie das Ork-Lager im Osten. Bauen Sie weitere Rohstoffe ab und sorgen Sie fr ausreichend Nahrung." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.e ORK LAGER ZERSTRT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "OrcCamp1Destroyed", UpdateInterval = 2},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		QuestSolve{QuestId = 476},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo264", String = "Sie knnen Leichen und Truhen nicht durchsuchen, wenn in der Nhe noch ein Feind ist." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo159", String = "In dem Ork-Lager steht eine Kiste. Wenn Sie mit einer eigenen Figur in der Nhe stehen, knnen Sie die Kiste durch einen Klick mit der rechten Maustaste ffnen. Nehmen Sie die beiden Plne darin an sich." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.f TEMPEL UND KLERIKER PLNE GELOOTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalCounter{Name = "OrkCampItemCounter", Operator = IsEqual, Value = 2, UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo160", String = "Sie haben gerade den Konstruktionsplan fr ein neues Gebude und den Einheitenplan fr die menschliche Einheit 'Kleriker' gefunden." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo161", String = "ffnen Sie Ihr Inventar und gehen Sie auf die Seite 'Plne'." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.g IM INVENTAR BEI DEN PLNEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(3)
cond:SetUpdateInterval(1)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo162", String = "Hier haben Sie die bersicht, ber welche Gebude- und Einheitenplne Sie von allen sechs Aufbaurassen verfgen. Auf der rechten Seite im Fenster knnen Sie die Rasse whlen. Whlen Sie, falls nicht bereits aktiv, die Menschen." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo163", String = "Legen Sie den Einheitenplan in ein freies Fach bei den Einheiten in der unteren Zeile." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.h KLERIKER PLAN WEG ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(PlayerHasItem{ItemId = 1261, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo164", String = "Diese Einheit knnen Sie ab jetzt an Ihren Menschen-Monumenten produzieren, vorausgesetzt Sie verfgen ber die erforderlichen Gebude und Rohstoffe." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo165", String = "Legen Sie den Gebudeplan in ein freies Fach bei den Gebuden in der oberen Zeile. Da die erste Zeile komplett belegt ist, mssen Sie zunchst den Pfeil nach rechts klicken." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.i TPEMEL PALN BZNTEUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		Negated(PlayerHasItem{ItemId = 255, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo166", String = "Ab jetzt knnen Ihre menschlichen Arbeiter auch den 'Tempel' errichten. Schlieen Sie Ihr Inventar." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.j INVENTAR GESCHLOSSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo167", String = "Wenn Sie menschliche Einheiten mit magischen Fhigkeiten herbeirufen wollen, bentigen Sie 'Aria' eine magische Flssigkeit. In der Nhe des Ork-Lagers finden Sie eine Aria-Quelle." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo168", String = "Einfache Arbeiter sind nicht in der Lage, Aria zu frdern. Sie bentigen dafr ein spezielles Gebude." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo169", String = "Errichten Sie in der Nhe der Aria-Quelle einen 'Ariaschrein' und in Ihrer Hauptsiedlung den Tempel des Lichts. Um diese Gebude auswhlen zu knnen, mssen Sie bei der Gebudeauswahl den Pfeil nach rechts anklicken." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.k SCHREIN UND TEMPEL AUFGEBAUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 16, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Aria Schrein
		PlayerBuildingExists{BuildingId = 17, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Tempel
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo170", String = "Bis zu 5 Handwerker knnen in dem 'Ariaschrein' arbeiten und Aria frdern." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo171", String = "Der 'Tempel des Lichts' dient der Beschwrung von Einheiten mit magischen Fhigkeiten, vergleichbar mit der Schmiede fr die Waffenproduktion. Mehrere Tempel erlauben eine schnellere Herbeirufung magischer Einheiten." , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo172", String = "Auerdem knnen Sie im Tempel des Lichts eine Aufwertung durchfhren. Aufwertungen sind in zahlreichen Gebuden mglich und sie verbessern meist Ihre Einheiten, knnen aber auch andere Vorteile bieten." , Color = ColorWhite} },
		[4] = { SetInfoText{Tag = "TutInfo173", String = "Wenn Sie den Tempel selektieren und ausreichend Rohstoffe haben, knnen Sie unten das Symbol 'Weg des Lichts' aktivieren. Alle Kleriker, welche Sie danach herbeirufen, verfgen ber ein Schild und grere Mana-Reserven." , Color = ColorWhite} },
		[5] = { SetInfoText{Tag = "TutInfo174", String = "Neben der Aria-Quelle sehen Sie brigens einige Lenya-Pflanzen und Mondsilber. Beide Rohstoffe sind fr Menschen unbedeutend, spielen aber fr die anderen Aufbaurassen eine wichtige Rolle." , Color = ColorWhite} },

		[6] = { SetInfoText{Tag = "TutInfo175", String = "Produzieren Sie wenigstens 3 Kleriker. Falls Sie die Einheit nicht produzieren knnen, ist die Schaltflche abgedunkelt. Bewegen Sie in diesem Fall die Maus ber die Schaltflche und achten Sie auf Hinweise im Hilfe-Fenster. Falls die Anzahl Ihrer Kampfeinheiten bereits das Einheitenlimit erreicht hat, knnen Sie vorhandene Einheiten selektieren und mit 'K' zerstren." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.l DREI KLERIKER GEBAUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = 
	{  	-- Kleriker oder Kleriker Upgrade
		ODER(			UND(				PlayerUnitExists{UnitId = 538, Amount = 2, UpdateInterval = 5},
		     	PlayerUnitExists{UnitId = 1227, Amount = 1, UpdateInterval = 5}
		    ),
			ODER(				UND(					PlayerUnitExists{UnitId = 538, Amount = 1, UpdateInterval = 5},
		     		PlayerUnitExists{UnitId = 1227, Amount = 2, UpdateInterval = 5}
		     	),     
				ODER(					PlayerUnitExists{UnitId = 538, Amount = 3, UpdateInterval = 5},
		     		PlayerUnitExists{UnitId = 1227, Amount = 3, UpdateInterval = 5}
		     	)
		   	)
		 ),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo176", String = "Als nchstes wollen wir der Eisenproduktion etwas nachhelfen. Errichten Sie eine Schmelze im nheren Umkreis Ihrer 'Mine'." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.m SCHMELZE AUFGEBAUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 15, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Schmelze
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo177", String = "Die 'Minen'-Handwerker werden nun das von Ihnen gefrderte Erz bei der Schmelze abliefern. In der Schmelze wird es weiterverarbeitet. Dadurch erhalten Sie insgesamt die doppelte Rohstoffmenge pro Lieferung." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo178", String = "Einfache Arbeiter knnen ihre Rohstoffe nur in Hauptgebuden und an Monumenten abliefern." , Color = ColorWhite} },
		[3] = { SetInfoText{Tag = "TutInfo179", String = "Alle Handwerker knnen ihr Eisenerz an eine Schmelze, ihr Holz an ein Sgwerk, ihre Steine an einen Steinmetz oder ihre Nahrungsmittel an das Nahrungslager liefern, wodurch jede Lieferung doppelt zhlt." , Color = ColorWhite} },

		[4] = { SetInfoText{Tag = "TutInfo180", String = "Errichten Sie ein Nahrungslager." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.n NAHRUNGSMITTELLAGER AUFGEBAUT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerBuildingExists{BuildingId = 8, OnlyWhenBuiltUp = TRUE, UpdateInterval = 10},	-- Nahrungslager
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo181", String = "Wenn das Nahrungslager fertig ist, knnen Ihre herbeigerufenen Einheiten durch Nahrungsmittel ihre Lebenspunkte und Manareserven regenerieren. Dies ist insbesondere wichtig, wenn Sie viele magische Einheiten herbeirufen." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo182", String = "Ihr Avatar und Ihre Helden regenerieren sich brigens auch ohne Nahrungsmittel." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo183", String = "Rufen Sie wenigstens 15 Kampfeinheiten herbei." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #13.o FNFZEHN KAMPFEINHEITEN PRODUZIERT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		PlayerUnitExists{UnitId = 0, Amount = 15, UpdateInterval = 10},	-- 15 Einheiten
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo187", String = "Wenn Sie nun am Ork-Lager vorbei dem Weg weiter nach Osten folgen, werden Sie auf einen feindlichen Sphposten treffen. Dieser wird bei Sichtkontakt sofort sein Hauptlager alarmieren." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo188", String = "Dringen Sie mit Ihrem Avatar, dem Helden und wenigstens 15 Kampfeinheiten weiter nach Osten vor. Sobald der Sphposten Sie entdeckt hat, erscheint ein gelbes Warnsignal auf der bersichtskarte." , Color = ColorYellow},
				SetGlobalFlagTrue{Name = "OpenDoor3335"},
		},
}}


------------------------------------------------------------------------------------------------------------------------
-- #14.a LOOKOUT ALARMIERT CAMP ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		ODER(
			FigureHasAggro{NpcId = 3615},
			FigureDead{NpcId = 3615}
			),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo189", String = "Die Orks sind alarmiert und schicken Ihnen eine Angriffswelle entgegen. Vernichten Sie die Orks und ihr Hauptlager." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.b ZWEITES CAMP ZERSTRT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "OrcCamp2Destroyed", UpdateInterval = 2},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		QuestSolve{QuestId = 477},
		QuestBegin{QuestId = 478},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo190", String = "Gratuliere! Wenn Sie in Ihr Questbuch schauen, werden Sie feststellen, dass Sie die beiden vorher offenen Schritte jetzt gelst haben." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo191", String = "Der Anfhrer der Orks hatte die gesuchte Rune bei sich. Durchsuchen Sie die Leiche und nehmen Sie die Rune an sich, falls noch nicht geschehen." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.bII ORK ANFHRER GELOOTET ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerHasHadAvatarRune", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo192", String = "Gehen Sie nun zurck zu 'Joshua' am Menschen-Monument und reden Sie mit ihm." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.c DEM JOSHUA DIE RUNE GEBRACHT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagFalse{Name = "GDS_PlayerIsTalking", UpdateInterval = 1},
		Negated(PlayerHasItem{ItemId = 3240, UpdateInterval = 1}),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo193", String = "Fr das Lsen der Queste haben Sie zustzliche Erfahrungspunkte erhalten und Ihr Avatar ist eine Stufe aufgestiegen." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo194", String = "Mit jeder neuen Stufe verfgt Ihr Avatar ber mehr Lebenspunkte und Manareserven. Auerdem erhalten Sie Fhigkeitspunkte und Attributspunkte, mit denen Sie Ihren Avatar weiter verbessern knnen." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo195", String = "ffnen Sie das Inventar und gehen Sie in die Rubrik 'Charakter-Information'" , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.d IM CHARAKTER STATS MEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsInventoryOpen:new(6)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo196", String = "Whlen Sie rechts im Fenster Ihren Avatar aus, falls nicht bereits aktiv. Links im Fenster sehen Sie die Fhigkeiten Ihres Avatars und in der Mitte die Attribute." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo197", String = "Verteilen Sie die neuen Attributspunkte, z.B. auf Strke oder Weisheit. Klicken Sie dazu im Fenster auf die kleinen Pfeile direkt neben den Zahlenwerten der Attribute." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.e STATPUNKTE VERTEILT ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsAdvancementLookUp:new(0, 0, 0))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo198", String = "Die einzelnen Attribute stehen fr die Eigenschaften einer Figur. Wenn Sie mit dem Mauszeiger ber einem Attribut schweben, erklrt das Hilfe-Fenster die Bedeutung der einzelnen Werte." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo199", String = "Verteilen Sie nun die neuen Fhigkeitspunkte. Klicken Sie auf 'Neue Fhigkeit' und whlen Sie rechts im Fenster die 'leichte Kriegskunst' aus. Verteilen Sie den zweiten Punkt beliebig durch einen Klick auf einen der kleinen Pfeile neben den Fhigkeiten." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.f SKILLPUNKTE VERTEILT ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsAdvancementLookUp:new(0, 0, 1))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo200", String = "Sie haben durch Ihre besseren Fhigkeiten in der 'leichten Kriegskunst' nun eine zustzliche Kampf-Fhigkeit erhalten, und zwar 'Berserk'." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo201", String = "Sie finden diese Nahkampf-Fhigkeit in Ihrem Zauberbuch. bertragen Sie 'Berserk' in das 'Zauber-Gedchtnis'." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.g BERSERK IM GEDCHTNIS ...
------------------------------------------------------------------------------------------------------------------------
local cond = CGdsIsSpellMemorized:new(3211)
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo202", String = "Schlieen Sie nun Ihr Inventar.", Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.h INVENTORY GESCHLOSSEN ...
------------------------------------------------------------------------------------------------------------------------
local cond = Negated(CGdsIsInventoryOpen:new(8))
cond:SetUpdateInterval(2)
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		cond,
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo203", String = "Kampf-Fhigkeiten und einige Zaubersprche werden nicht auf ein Ziel ausgelst, sondern wirken nur  auf den auslsenden Charakter selbst." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo204", String = "Lsen Sie 'Berserk' testweise aus, indem Sie Ihre Figur selektieren und das Symbol unten in der Aktionsleiste oder oben links unter dem Portrt anklicken." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.i DIE BERSERK ABILITY BENUTZT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "PlayerHasHadBerserkActive", UpdateInterval = 1},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		SetGlobalFlagTrue{Name = "JoshTurorialOver"},
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo205", String = "Wenn Sie 'Berserk' auslsen, verursacht Ihr Avatar fr kurze Zeit sehr hohen Kampfschaden. Dies kann in einer Notsituation sehr hilfreich sein, allerdings knnen Sie ihn erst nach einigen Minuten erneut einsetzen." , Color = ColorWhite} },

		[2] = { SetInfoText{Tag = "TutInfo206", String = "Sprechen Sie Joshua nochmals an." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.j JOSHUA ZUM LETZTEN MAL ANGESPROCHEN ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "JoshTutorialGotoPortal", UpdateInterval = 10},
		IsGlobalFlagFalse{Name = "GDS_PlayerIsTalking", UpdateInterval = 10},
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
		SetGlobalFlagTrue{Name = "OpenDoor3333"},
		SetGlobalFlagTrue{Name = "BeginJoshuaRohenCutscene"},
		-- lsche letzten info text
		SetInfoText{Tag = "", String = "" , Color = ColorWhite},
	},
}

------------------------------------------------------------------------------------------------------------------------
-- #14.k NACH ENDE DER FINALEN CUTSCENE ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		IsGlobalFlagTrue{Name = "TutExtroEnd", UpdateInterval = 10},
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo207", String = "Mit einem magischen Portal knnen Sie diese Karte nun verlassen. Oder folgen Sie dem Weg nach Sden. Dort warten weitere Gegner zum Experimentieren auf sie, sowie einige ntzliche Hinweise, die Sie fr die ersten Karten aber nicht unbedingt bentigen." , Color = ColorWhite} },
		[2] = { SetInfoText{Tag = "TutInfo208", String = "Wenn Sie oben rechts 'Men' anklicken, dann knnen Sie jederzeit den aktuellen Spielstand speichern." , Color = ColorWhite} },

		[3] = { SetInfoText{Tag = "TutInfo209", String = "Gehen Sie nach Westen zum Portal, um die Karte zu verlassen oder folgen Sie dem Weg nach Sden, um weitere ntzliche Hinweise zu erhalten." , Color = ColorYellow} },
}}

------------------------------------------------------------------------------------------------------------------------
-- #14.l SPIELER AM FINALEN MONUMENT ...
------------------------------------------------------------------------------------------------------------------------
TutorialStateNum = TutorialStateNum + 1
NewState{ Name = "Tutorial#" .. TutorialStateNum }
AddTransition{ From = "Tutorial#" .. TutorialStateNum - 1, To = "Tutorial#" .. TutorialStateNum, RemoveTransitionAfterUse = TRUE,
	Conditions = {
		ODER(
			FigureInRange{NpcId = Avatar, X = 145, Y = 196, Range = TutorialDefaultRange},
			FigureInRange{NpcId = Avatar, X = 297, Y = 108, Range = TutorialDefaultRange}
			),
		CGdsIsInfoTextActive:new(),
	},
	Actions = {
	},
}
TutorialTextFlow{ From = "Tutorial#" .. TutorialStateNum, To = "Tutorial#" .. TutorialStateNum,	Actions = {
		[1] = { SetInfoText{Tag = "TutInfo210", String = "Portale erlauben einem die Reise zu neuen Plattformen, auch wenn man dort noch ber keinen aktiven Seelenfels verfgt. Wenn Sie dieses Portal benutzen, betreten Sie die nchste Karte." , Color = ColorYellow} },
}}


EndDefinition()
end
