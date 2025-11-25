❯ uv run quest_creator.py
🎯 Starting Quest Creator...
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.logging_config:configure_logging:95 | Logging system initialized
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.widgets.visual_dialogue_widget:__init__:170 | Visual Dialogue Widget initialized
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_load_data:1467 | Loading quest data...
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:556 | Starting icon data loading
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:562 | Loading icon mapping from: /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/data/ui_icon_mapping.json
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:606 | Loaded icon mapping: 6237 items in 0.10s
2025-11-21 07:01:28 | INFO     | TirganachReloaded.cff_editor.data_model:_build_handle_to_path_mapping:693 | Building handle-to-path mapping for 6237 items...
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_build_handle_to_path_mapping:754 | Built handle-to-path mapping with 873 handles in 0.62s
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:620 | Built handle-to-path mapping in 0.62s
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:624 | Initialized handle cache
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:628 | Loading icon index from: /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/ExtractedAssets/UI/icons_extracted/icon_index_manifest.json
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:634 | Loaded split icon index: 4258 icons
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:651 | Loading verified mappings from: /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/data/verified_icon_mappings.json
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:659 | No verified mappings found (run interactive_icon_mapper.py to create)
2025-11-21 07:01:29 | INFO     | TirganachReloaded.cff_editor.data_model:_load_icon_data:674 | Icon data loading completed in 0.63s
2025-11-21 07:01:29 | WARNING  | TirganachReloaded.cff_editor.data_model:__init__:127 | ITM Integration: cff_editor_itm_integration module not available
2025-11-21 07:01:30 | INFO     | TirganachReloaded.cff_editor.data_model:_load_weapon_names:497 | Loaded 719 weapon names
2025-11-21 07:01:30 | INFO     | TirganachReloaded.cff_editor.data_model:_load_armor_names:539 | Loaded 635 armor names
2025-11-21 07:01:30 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_load_data:1486 | CFF file loaded successfully
2025-11-21 07:01:30 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_load_data:1543 | Loaded 1041 quests
2025-11-21 07:01:39 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 487 to /Users/alex/.spellmut/quests/quest_487.json
2025-11-21 07:02:22 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:02:38 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:03:40 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:04:16 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
Traceback (most recent call last):
  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 808, in _browse_quest_giver
    self.logger.info(f"Selected quest giver: {npc.name} (ID: {npc.npc_id})")
    ^^^^^^^^^^^
AttributeError: 'QuestLocationWidget' object has no attribute 'logger'. Did you mean: 'lower'?
2025-11-21 07:05:01 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
DEBUG: populate_tree called with 11074 filtered items
DEBUG: Items grouped by type: {'weapon': 721, 'armor': 635, 'item': 6629, 'quest': 472, 'creature': 2617}
DEBUG: populate_tree called with 11074 filtered items
DEBUG: Items grouped by type: {'weapon': 721, 'armor': 635, 'item': 6629, 'quest': 472, 'creature': 2617}
DEBUG: populate_tree called with 11074 filtered items
DEBUG: Items grouped by type: {'weapon': 721, 'armor': 635, 'item': 6629, 'quest': 472, 'creature': 2617}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 5733 filtered items
DEBUG: Items grouped by type: {'item': 5733}
DEBUG: populate_tree called with 4740 filtered items
DEBUG: Items grouped by type: {'item': 4740}
DEBUG: populate_tree called with 14 filtered items
DEBUG: Items grouped by type: {'item': 14}
DEBUG: populate_tree called with 11 filtered items
DEBUG: Items grouped by type: {'item': 11}
DEBUG: populate_tree called with 0 filtered items
DEBUG: Items grouped by type: {}
DEBUG: populate_tree called with 11 filtered items
DEBUG: Items grouped by type: {'item': 11}
DEBUG: populate_tree called with 10 filtered items
DEBUG: Items grouped by type: {'item': 10}
DEBUG: populate_tree called with 11 filtered items
DEBUG: Items grouped by type: {'item': 11}
DEBUG: populate_tree called with 14 filtered items
DEBUG: Items grouped by type: {'item': 14}
DEBUG: populate_tree called with 4740 filtered items
DEBUG: Items grouped by type: {'item': 4740}
DEBUG: populate_tree called with 5733 filtered items
DEBUG: Items grouped by type: {'item': 5733}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 1994 filtered items
DEBUG: Items grouped by type: {'item': 1994}
DEBUG: populate_tree called with 651 filtered items
DEBUG: Items grouped by type: {'item': 651}
DEBUG: populate_tree called with 4 filtered items
DEBUG: Items grouped by type: {'item': 4}
DEBUG: populate_tree called with 651 filtered items
DEBUG: Items grouped by type: {'item': 651}
DEBUG: populate_tree called with 1994 filtered items
DEBUG: Items grouped by type: {'item': 1994}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 5733 filtered items
DEBUG: Items grouped by type: {'item': 5733}
DEBUG: populate_tree called with 4740 filtered items
DEBUG: Items grouped by type: {'item': 4740}
DEBUG: populate_tree called with 305 filtered items
DEBUG: Items grouped by type: {'item': 305}
DEBUG: populate_tree called with 91 filtered items
DEBUG: Items grouped by type: {'item': 91}
DEBUG: populate_tree called with 91 filtered items
DEBUG: Items grouped by type: {'item': 91}
DEBUG: populate_tree called with 11074 filtered items
DEBUG: Items grouped by type: {'weapon': 721, 'armor': 635, 'item': 6629, 'quest': 472, 'creature': 2617}
DEBUG: populate_tree called with 11074 filtered items
DEBUG: Items grouped by type: {'weapon': 721, 'armor': 635, 'item': 6629, 'quest': 472, 'creature': 2617}
DEBUG: populate_tree called with 11074 filtered items
DEBUG: Items grouped by type: {'weapon': 721, 'armor': 635, 'item': 6629, 'quest': 472, 'creature': 2617}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 6629 filtered items
DEBUG: Items grouped by type: {'item': 6629}
DEBUG: populate_tree called with 109 filtered items
DEBUG: Items grouped by type: {'item': 109}
DEBUG: populate_tree called with 36 filtered items
DEBUG: Items grouped by type: {'item': 36}
DEBUG: populate_tree called with 18 filtered items
DEBUG: Items grouped by type: {'item': 18}
2025-11-21 07:07:32 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:07:44 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:07:50 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 277, in <lambda>
    self.start_btn.clicked.connect(lambda: self.add_node(NodeType.START))
    │    │         │       │               │    │        │        └ <NodeType.START: 'start'>
    │    │         │       │               │    │        └ <enum 'NodeType'>
    │    │         │       │               │    └ <function VisualDialogueWidget.add_node at 0x13320e7a0>
    │    │         │       │               └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>
    │    │         │       └ <method 'connect' of 'PySide6.QtCore.SignalInstance' objects>
    │    │         └ <PySide6.QtCore.SignalInstance clicked() at 0x1331a5150>
    │    └ <PySide6.QtWidgets.QPushButton(0x7adde9880) at 0x133208700>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 466, in add_node
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'start', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions':...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:07:52 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:08:22.471 python3[21947:5776140] error messaging the mach port for IMKCFRunLoopWakeUpReliable
2025-11-21 07:08:28 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/text_mode_dialogue_overview.py", line 993, in on_add_node
    self.node_added.emit(node_id, node.to_dict())
    │    │          │    │        │    └ <function DialogueNodeData.to_dict at 0x10b12d300>
    │    │          │    │        └ DialogueNodeData(id='02', node_type='npc', speaker='Zwerg', text='Hallo! Ich  brauche diesen schönen Stein!', choices=[], con...
    │    │          │    └ '02'
    │    │          └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_added(QString,QVariantMap) at 0x10b0ddff0>
    └ <TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview.TextModeDialogueOverview(0x7adc016c0) at 0x10b16c340>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2635, in _on_text_mode_node_added
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:08:30 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:08:55 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/text_mode_dialogue_overview.py", line 993, in on_add_node
    self.node_added.emit(node_id, node.to_dict())
    │    │          │    │        │    └ <function DialogueNodeData.to_dict at 0x10b12d300>
    │    │          │    │        └ DialogueNodeData(id='03', node_type='player', speaker='Player', text='Ok hol ich dir!', choices=[], conditions=[], actions=[]...
    │    │          │    └ '03'
    │    │          └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_added(QString,QVariantMap) at 0x10b0ddff0>
    └ <TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview.TextModeDialogueOverview(0x7adc016c0) at 0x10b16c340>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2635, in _on_text_mode_node_added
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:08:57 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:09:12 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/text_mode_dialogue_overview.py", line 993, in on_add_node
    self.node_added.emit(node_id, node.to_dict())
    │    │          │    │        │    └ <function DialogueNodeData.to_dict at 0x10b12d300>
    │    │          │    │        └ DialogueNodeData(id='04', node_type='end', speaker='', text='', choices=[], conditions=[], actions=[], next_nodes=[], answer_...
    │    │          │    └ '04'
    │    │          └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_added(QString,QVariantMap) at 0x10b0ddff0>
    └ <TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview.TextModeDialogueOverview(0x7adc016c0) at 0x10b16c340>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2635, in _on_text_mode_node_added
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:14 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:09:42 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 617, in select_node
    node_item.setSelected(True)
    │         └ <method 'setSelected' of 'PySide6.QtWidgets.QGraphicsItem' objects>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 456, in on_selection_changed
    self.on_node_selected(item.node)
    │    │                │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...
    │    └ <function DialogueGraphicsView.on_node_selected at 0x13320ca40>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 443, in on_node_selected
    self.node_selected.emit(node)
    │    │             │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(PyObject) at 0x1331a6b50>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 633, in on_node_selected
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:42 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 620, in select_node
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:44 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:09:46 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 617, in select_node
    node_item.setSelected(True)
    │         └ <method 'setSelected' of 'PySide6.QtWidgets.QGraphicsItem' objects>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 456, in on_selection_changed
    self.on_node_selected(item.node)
    │    │                │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...
    │    └ <function DialogueGraphicsView.on_node_selected at 0x13320ca40>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 443, in on_node_selected
    self.node_selected.emit(node)
    │    │             │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(PyObject) at 0x1331a6b50>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 633, in on_node_selected
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:47 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 620, in select_node
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:47 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 617, in select_node
    node_item.setSelected(True)
    │         └ <method 'setSelected' of 'PySide6.QtWidgets.QGraphicsItem' objects>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 456, in on_selection_changed
    self.on_node_selected(item.node)
    │    │                │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...
    │    └ <function DialogueGraphicsView.on_node_selected at 0x13320ca40>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 443, in on_node_selected
    self.node_selected.emit(node)
    │    │             │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(PyObject) at 0x1331a6b50>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 633, in on_node_selected
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:48 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 620, in select_node
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:48 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 617, in select_node
    node_item.setSelected(True)
    │         └ <method 'setSelected' of 'PySide6.QtWidgets.QGraphicsItem' objects>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 456, in on_selection_changed
    self.on_node_selected(item.node)
    │    │                │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...
    │    └ <function DialogueGraphicsView.on_node_selected at 0x13320ca40>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 443, in on_node_selected
    self.node_selected.emit(node)
    │    │             │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(PyObject) at 0x1331a6b50>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 633, in on_node_selected
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:49 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 620, in select_node
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:49 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 617, in select_node
    node_item.setSelected(True)
    │         └ <method 'setSelected' of 'PySide6.QtWidgets.QGraphicsItem' objects>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 456, in on_selection_changed
    self.on_node_selected(item.node)
    │    │                │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...
    │    └ <function DialogueGraphicsView.on_node_selected at 0x13320ca40>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 443, in on_node_selected
    self.node_selected.emit(node)
    │    │             │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(PyObject) at 0x1331a6b50>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 633, in on_node_selected
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:50 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 620, in select_node
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:50 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 617, in select_node
    node_item.setSelected(True)
    │         └ <method 'setSelected' of 'PySide6.QtWidgets.QGraphicsItem' objects>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 456, in on_selection_changed
    self.on_node_selected(item.node)
    │    │                │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueNodeItem(0x7b1ae2440, pos=0,0, flags=(ItemIsMovable|Item...
    │    └ <function DialogueGraphicsView.on_node_selected at 0x13320ca40>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 443, in on_node_selected
    self.node_selected.emit(node)
    │    │             │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(PyObject) at 0x1331a6b50>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueGraphicsView(0x7afd70c00) at 0x13320b9c0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 633, in on_node_selected
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:51 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 929, in on_item_clicked
    self.node_selected.emit(node_id)
    │    │             │    └ 'NodeType.START_1'
    │    │             └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance node_selected(QString) at 0x1331a6150>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialogueTreeWidget(0x7addc2140) at 0x133208040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 620, in select_node
    self.properties_widget.set_node(node)
    │    │                 │        └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                 └ <function DialoguePropertiesWidget.set_node at 0x13320cf40>
    │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 652, in set_node
    self.text_edit.setText(node.text)
    │    │         │       │    └ ''
    │    │         │       └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │         └ <method 'setText' of 'PySide6.QtWidgets.QTextEdit' objects>
    │    └ <PySide6.QtWidgets.QTextEdit(0x7af74d600) at 0x133224540>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_editor.py", line 816, in on_properties_changed
    self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())
    │    │                  │    │    │            │   │    │            └ <function DialogueNode.to_dict at 0x101bce200>
    │    │                  │    │    │            │   │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    │    │            │   └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  │    │    │            └ 'NodeType.START_1'
    │    │                  │    │    └ DialogueNode(id='NodeType.START_1', node_type=<NodeType.NPC: 'npc'>, speaker='', text='', choices=[], conditions=[], actions=...
    │    │                  │    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>
    │    │                  └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance properties_changed(QString,QVariantMap) at 0x1331a6c90>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_editor.DialoguePropertiesWidget(0x7addc2680) at 0x13320bd80>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 655, in on_properties_changed
    self.emit_dialogue_changed()
    │    └ <function VisualDialogueWidget.emit_dialogue_changed at 0x13320f420>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/visual_dialogue_widget.py", line 1231, in emit_dialogue_changed
    self.dialogue_changed.emit(dialogue_data)
    │    │                │    └ {'nodes': [{'id': 'NodeType.START_1', 'type': 'npc', 'speaker': '', 'text': '', 'choices': [], 'conditions': [], 'actions': [...
    │    │                └ <method 'emit' of 'PySide6.QtCore.SignalInstance' objects>
    │    └ <PySide6.QtCore.SignalInstance dialogue_changed(QVariantMap) at 0x10b1ef6d0>
    └ <TirganachReloaded.cff_editor.widgets.visual_dialogue_widget.VisualDialogueWidget(0x7addc1880) at 0x10b1f2800>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2669, in _on_visual_dialogue_changed
    self._on_data_changed()
    │    └ <function UnifiedQuestEditor._on_data_changed at 0x10b11afc0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:09:53 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:10:16 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:17 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:17 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:18 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:18 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:19 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:19 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:20 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1873, in _on_data_changed
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
2025-11-21 07:10:22 | INFO     | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_auto_save:1673 | Auto-saved quest 10000 to /Users/alex/.spellmut/quests/quest_10000.json
2025-11-21 07:10:39 | ERROR    | TirganachReloaded.cff_editor.widgets.unified_quest_editor:_convert_to_enhanced_data:2138 | Error converting quest data: Dialogue.__init__() got an unexpected keyword argument 'speaker'
Traceback (most recent call last):

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 61, in <module>
    sys.exit(main())
    │   │    └ <function main at 0x1016ee020>
    │   └ <built-in function exit>
    └ <module 'sys' (built-in)>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/quest_creator.py", line 40, in main
    return editor_main()
           └ <function main at 0x10b046660>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2794, in main
    return app.exec()
           │   └ <staticmethod(<built-in method exec of Shiboken.ObjectType object at 0x7af54e310>)>
           └ <PySide6.QtWidgets.QApplication(0x7ae4328f0) at 0x1016fa040>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2157, in _save_quest
    self._validate_current_quest()
    │    └ <function UnifiedQuestEditor._validate_current_quest at 0x10b11b1a0>
    └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

  File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 1983, in _validate_current_quest
    enhanced_quest = self._convert_to_enhanced_data(quest_data)
                     │    │                         └ {'quest_id': 9000, 'name': 'Suche Baerenquarz', 'description': 'In den Windwallbergen gibt es einen besonderen Edelstein. Fin...
                     │    └ <function UnifiedQuestEditor._convert_to_enhanced_data at 0x10b11b240>
                     └ <TirganachReloaded.cff_editor.widgets.unified_quest_editor.UnifiedQuestEditor(0x7adc00000) at 0x1016f9fc0>

> File "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py", line 2105, in _convert_to_enhanced_data
    Dialogue(
    └ <class 'TirganachReloaded.cff_editor.models.quest_models.Dialogue'>

TypeError: Dialogue.__init__() got an unexpected keyword argument 'speaker'
