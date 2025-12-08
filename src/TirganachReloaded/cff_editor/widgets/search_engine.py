#!/usr/bin/env python3
"""
Search Engine for Quest Editor

Provides powerful search capabilities across quest data, dialogue nodes,
conditions, actions, and other content with advanced filtering and ranking.
"""

import re
import fnmatch
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from difflib import SequenceMatcher

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice, DialogueCondition, DialogueAction,
        DialogueConditionType, DialogueActionType
    )
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
    from TirganachReloaded.cff_editor.widgets.enhanced_search_navigation import (
        SearchScope, SearchType, SearchResult
    )
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class SearchContext:
    """Context information for search operations"""
    quest_data: Dict[str, EnhancedQuestData] = None
    dialogue_trees: Dict[str, DialogueTree] = None
    current_quest_id: Optional[str] = None
    include_completed: bool = True
    include_archived: bool = False


class SearchEngine:
    """Main search engine for quest content"""

    def __init__(self):
        self.context = SearchContext()
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup common search patterns and keywords"""
        self.action_keywords = {
            "give": ["give", "reward", "add", "provide"],
            "remove": ["remove", "take", "subtract"],
            "set": ["set", "assign", "change"],
            "check": ["check", "verify", "validate"],
            "start": ["start", "begin", "initiate"],
            "complete": ["complete", "finish", "end"],
            "fail": ["fail", "abort", "cancel"]
        }

        self.condition_keywords = {
            "level": ["level", "xp", "experience"],
            "quest": ["quest", "mission", "task"],
            "flag": ["flag", "state", "status"],
            "item": ["item", "inventory", "equipment"],
            "faction": ["faction", "reputation", "standing"],
            "skill": ["skill", "ability", "talent"]
        }

    def set_context(self, context: SearchContext):
        """Set search context"""
        self.context = context

    def search(self, search_params: dict) -> List[SearchResult]:
        """Perform search based on parameters"""
        try:
            # Extract parameters
            query = search_params.get("query", "").strip()
            search_type = search_params.get("type", SearchType.CONTAINS)
            scopes = search_params.get("scope", [SearchScope.ALL])
            case_sensitive = search_params.get("case_sensitive", False)
            whole_words = search_params.get("whole_words", False)

            # Additional filters
            quest_id_filter = search_params.get("quest_id")
            answer_id_filter = search_params.get("answer_id")
            node_type_filter = search_params.get("node_type")

            if not query and not quest_id_filter and not answer_id_filter:
                return []

            results = []

            # Determine search scopes
            if SearchScope.ALL in scopes or len(scopes) == 0:
                active_scopes = list(SearchScope)
            else:
                active_scopes = scopes

            # Search in each scope
            for scope in active_scopes:
                try:
                    scope_results = self._search_in_scope(
                        query, search_type, scope,
                        case_sensitive, whole_words,
                        quest_id_filter, answer_id_filter, node_type_filter
                    )
                    results.extend(scope_results)
                except Exception as e:
                    logger.error(f"Error searching in scope {scope}: {e}")

            # Rank and sort results
            ranked_results = self._rank_results(results, query)

            return ranked_results

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def _search_in_scope(self, query: str, search_type: SearchType, scope: SearchScope,
                        case_sensitive: bool, whole_words: bool,
                        quest_id_filter: Optional[int],
                        answer_id_filter: Optional[int],
                        node_type_filter: Optional[str]) -> List[SearchResult]:
        """Search within a specific scope"""
        results = []

        if scope == SearchScope.QUEST_INFO:
            results.extend(self._search_quest_info(
                query, search_type, case_sensitive, whole_words, quest_id_filter
            ))
        elif scope == SearchScope.DIALOGUE_NODES:
            results.extend(self._search_dialogue_nodes(
                query, search_type, case_sensitive, whole_words, quest_id_filter, node_type_filter
            ))
        elif scope == SearchScope.CHOICE_TEXT:
            results.extend(self._search_choice_text(
                query, search_type, case_sensitive, whole_words, quest_id_filter, answer_id_filter
            ))
        elif scope == SearchScope.CONDITIONS:
            results.extend(self._search_conditions(
                query, search_type, case_sensitive, whole_words, quest_id_filter
            ))
        elif scope == SearchScope.ACTIONS:
            results.extend(self._search_actions(
                query, search_type, case_sensitive, whole_words, quest_id_filter
            ))
        elif scope == SearchScope.ANSWER_IDS:
            results.extend(self._search_answer_ids(
                answer_id_filter, quest_id_filter
            ))
        elif scope == SearchScope.FLAGS:
            results.extend(self._search_flags(
                query, search_type, case_sensitive, whole_words, quest_id_filter
            ))
        elif scope == SearchScope.VARIABLES:
            results.extend(self._search_variables(
                query, search_type, case_sensitive, whole_words, quest_id_filter
            ))
        elif scope == SearchScope.LUA_CODE:
            results.extend(self._search_lua_code(
                query, search_type, case_sensitive, whole_words, quest_id_filter
            ))

        return results

    def _search_quest_info(self, query: str, search_type: SearchType,
                          case_sensitive: bool, whole_words: bool,
                          quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search quest information"""
        results = []

        if not self.context.quest_data:
            return results

        for quest_id, quest in self.context.quest_data.items():
            # Apply quest ID filter
            if quest_id_filter and quest.quest_id != quest_id_filter:
                continue

            # Search in quest name
            if self._matches_query(query, search_type, quest.quest_name, case_sensitive, whole_words):
                results.append(SearchResult(
                    item_type="quest",
                    item_id=str(quest.quest_id),
                    context=f"Quest: {quest.quest_name}",
                    match_text=quest.quest_name,
                    quest_name=quest.quest_name,
                    relevance_score=self._calculate_relevance(query, quest.quest_name)
                ))

            # Search in quest description
            if self._matches_query(query, search_type, quest.description, case_sensitive, whole_words):
                results.append(SearchResult(
                    item_type="quest",
                    item_id=str(quest.quest_id),
                    context=f"Description: {quest.description[:100]}...",
                    match_text=quest.description,
                    quest_name=quest.quest_name,
                    relevance_score=self._calculate_relevance(query, quest.description)
                ))

        return results

    def _search_dialogue_nodes(self, query: str, search_type: SearchType,
                              case_sensitive: bool, whole_words: bool,
                              quest_id_filter: Optional[int],
                              node_type_filter: Optional[str]) -> List[SearchResult]:
        """Search dialogue nodes"""
        results = []

        if not self.context.dialogue_trees:
            return results

        for quest_id, dialogue_tree in self.context.dialogue_trees.items():
            # Apply quest ID filter
            if quest_id_filter and quest_id != str(quest_id_filter):
                continue

            for node in dialogue_tree.nodes:
                # Apply node type filter
                if node_type_filter and node.node_type != node_type_filter:
                    continue

                # Search in node text
                if self._matches_query(query, search_type, node.text, case_sensitive, whole_words):
                    results.append(SearchResult(
                        item_type="node",
                        item_id=node.node_id,
                        context=f"Dialogue: {node.text[:80]}...",
                        match_text=node.text,
                        quest_name=dialogue_tree.quest_name,
                        relevance_score=self._calculate_relevance(query, node.text)
                    ))

                # Search in node speaker
                if hasattr(node, 'speaker') and node.speaker:
                    if self._matches_query(query, search_type, node.speaker, case_sensitive, whole_words):
                        results.append(SearchResult(
                            item_type="node",
                            item_id=node.node_id,
                            context=f"Speaker: {node.speaker}",
                            match_text=node.speaker,
                            quest_name=dialogue_tree.quest_name,
                            relevance_score=self._calculate_relevance(query, node.speaker)
                        ))

        return results

    def _search_choice_text(self, query: str, search_type: SearchType,
                           case_sensitive: bool, whole_words: bool,
                           quest_id_filter: Optional[int],
                           answer_id_filter: Optional[int]) -> List[SearchResult]:
        """Search player choice text"""
        results = []

        if not self.context.dialogue_trees:
            return results

        for quest_id, dialogue_tree in self.context.dialogue_trees.items():
            # Apply quest ID filter
            if quest_id_filter and quest_id != str(quest_id_filter):
                continue

            for node in dialogue_tree.nodes:
                for i, choice in enumerate(node.choices):
                    # Apply answer ID filter
                    if answer_id_filter and choice.answer_id != answer_id_filter:
                        continue

                    # Search in choice text
                    if self._matches_query(query, search_type, choice.text, case_sensitive, whole_words):
                        results.append(SearchResult(
                            item_type="choice",
                            item_id=f"{node.node_id}_choice_{i}",
                            parent_id=node.node_id,
                            context=f"Choice: {choice.text[:60]}...",
                            match_text=choice.text,
                            quest_name=dialogue_tree.quest_name,
                            relevance_score=self._calculate_relevance(query, choice.text)
                        ))

        return results

    def _search_conditions(self, query: str, search_type: SearchType,
                          case_sensitive: bool, whole_words: bool,
                          quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search in dialogue conditions"""
        results = []

        if not self.context.dialogue_trees:
            return results

        for quest_id, dialogue_tree in self.context.dialogue_trees.items():
            # Apply quest ID filter
            if quest_id_filter and quest_id != str(quest_id_filter):
                continue

            for node in dialogue_tree.nodes:
                for condition in node.conditions:
                    # Search in condition description
                    if hasattr(condition, 'description') and condition.description:
                        if self._matches_query(query, search_type, condition.description, case_sensitive, whole_words):
                            results.append(SearchResult(
                                item_type="condition",
                                item_id=f"{node.node_id}_cond",
                                parent_id=node.node_id,
                                context=f"Condition: {condition.description[:50]}...",
                                match_text=condition.description,
                                quest_name=dialogue_tree.quest_name,
                                relevance_score=self._calculate_relevance(query, condition.description)
                            ))

                    # Search in condition target
                    if hasattr(condition, 'target') and condition.target:
                        if self._matches_query(query, search_type, condition.target, case_sensitive, whole_words):
                            results.append(SearchResult(
                                item_type="condition",
                                item_id=f"{node.node_id}_cond_target",
                                parent_id=node.node_id,
                                context=f"Condition Target: {condition.target}",
                                match_text=condition.target,
                                quest_name=dialogue_tree.quest_name,
                                relevance_score=self._calculate_relevance(query, condition.target)
                            ))

                    # Search in Lua code if present
                    if hasattr(condition, 'lua_code') and condition.lua_code:
                        if self._matches_query(query, search_type, condition.lua_code, case_sensitive, whole_words):
                            results.append(SearchResult(
                                item_type="condition",
                                item_id=f"{node.node_id}_cond_lua",
                                parent_id=node.node_id,
                                context=f"Condition Lua: {condition.lua_code[:50]}...",
                                match_text=condition.lua_code,
                                quest_name=dialogue_tree.quest_name,
                                relevance_score=self._calculate_relevance(query, condition.lua_code) * 0.8
                            ))

        return results

    def _search_actions(self, query: str, search_type: SearchType,
                       case_sensitive: bool, whole_words: bool,
                       quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search in dialogue actions"""
        results = []

        if not self.context.dialogue_trees:
            return results

        for quest_id, dialogue_tree in self.context.dialogue_trees.items():
            # Apply quest ID filter
            if quest_id_filter and quest_id != str(quest_id_filter):
                continue

            for node in dialogue_tree.nodes:
                for action in node.actions:
                    # Search in action description
                    if hasattr(action, 'description') and action.description:
                        if self._matches_query(query, search_type, action.description, case_sensitive, whole_words):
                            results.append(SearchResult(
                                item_type="action",
                                item_id=f"{node.node_id}_act",
                                parent_id=node.node_id,
                                context=f"Action: {action.description[:50]}...",
                                match_text=action.description,
                                quest_name=dialogue_tree.quest_name,
                                relevance_score=self._calculate_relevance(query, action.description)
                            ))

                    # Search in action target
                    if hasattr(action, 'target') and action.target:
                        if self._matches_query(query, search_type, action.target, case_sensitive, whole_words):
                            results.append(SearchResult(
                                item_type="action",
                                item_id=f"{node.node_id}_act_target",
                                parent_id=node.node_id,
                                context=f"Action Target: {action.target}",
                                match_text=action.target,
                                quest_name=dialogue_tree.quest_name,
                                relevance_score=self._calculate_relevance(query, action.target)
                            ))

                    # Search in Lua code if present
                    if hasattr(action, 'lua_code') and action.lua_code:
                        if self._matches_query(query, search_type, action.lua_code, case_sensitive, whole_words):
                            results.append(SearchResult(
                                item_type="action",
                                item_id=f"{node.node_id}_act_lua",
                                parent_id=node.node_id,
                                context=f"Action Lua: {action.lua_code[:50]}...",
                                match_text=action.lua_code,
                                quest_name=dialogue_tree.quest_name,
                                relevance_score=self._calculate_relevance(query, action.lua_code) * 0.8
                            ))

        return results

    def _search_answer_ids(self, answer_id_filter: Optional[int],
                          quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search for specific AnswerIds"""
        results = []

        if not answer_id_filter:
            return results

        if not self.context.dialogue_trees:
            return results

        for quest_id, dialogue_tree in self.context.dialogue_trees.items():
            # Apply quest ID filter
            if quest_id_filter and quest_id != str(quest_id_filter):
                continue

            for node in dialogue_tree.nodes:
                # Check node-level AnswerId
                if hasattr(node, 'answer_id') and node.answer_id == answer_id_filter:
                    results.append(SearchResult(
                        item_type="node",
                        item_id=node.node_id,
                        context=f"Node with AnswerId {answer_id_filter}",
                        match_text=str(answer_id_filter),
                        quest_name=dialogue_tree.quest_name,
                        relevance_score=1.0
                    ))

                # Check choice-level AnswerIds
                for i, choice in enumerate(node.choices):
                    if choice.answer_id == answer_id_filter:
                        results.append(SearchResult(
                            item_type="choice",
                            item_id=f"{node.node_id}_choice_{i}",
                            parent_id=node.node_id,
                            context=f"Choice with AnswerId {answer_id_filter}: {choice.text[:40]}...",
                            match_text=str(answer_id_filter),
                            quest_name=dialogue_tree.quest_name,
                            relevance_score=1.0
                        ))

        return results

    def _search_flags(self, query: str, search_type: SearchType,
                     case_sensitive: bool, whole_words: bool,
                     quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search in flag references"""
        results = []

        # This would search through flag manager or flag references
        # Implementation depends on how flags are stored

        return results

    def _search_variables(self, query: str, search_type: SearchType,
                         case_sensitive: bool, whole_words: bool,
                         quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search in variable references"""
        results = []

        # This would search through variable manager or variable references
        # Implementation depends on how variables are stored

        return results

    def _search_lua_code(self, query: str, search_type: SearchType,
                        case_sensitive: bool, whole_words: bool,
                        quest_id_filter: Optional[int]) -> List[SearchResult]:
        """Search in Lua code blocks"""
        results = []

        # This would search through all Lua code blocks
        # Implementation depends on how Lua code is stored

        return results

    def _matches_query(self, query: str, search_type: SearchType,
                      text: str, case_sensitive: bool, whole_words: bool) -> bool:
        """Check if text matches the search query"""
        if not query or not text:
            return False

        # Prepare text for matching
        search_text = text if case_sensitive else text.lower()
        search_query = query if case_sensitive else query.lower()

        if search_type == SearchType.CONTAINS:
            if whole_words:
                return re.search(rf'\b{re.escape(search_query)}\b', search_text) is not None
            else:
                return search_query in search_text

        elif search_type == SearchType.EXACT:
            if whole_words:
                return re.search(rf'\b{re.escape(search_query)}\b', search_text) is not None
            else:
                return search_text == search_query

        elif search_type == SearchType.REGEX:
            try:
                pattern = search_query if case_sensitive else re.compile(search_query, re.IGNORECASE)
                return pattern.search(search_text) is not None
            except re.error:
                # Invalid regex, fall back to contains
                return search_query in search_text

        elif search_type == SearchType.STARTS_WITH:
            if whole_words:
                return search_text.startswith(search_query + " ") or search_text == search_query
            else:
                return search_text.startswith(search_query)

        elif search_type == SearchType.ENDS_WITH:
            if whole_words:
                return search_text.endswith(" " + search_query) or search_text == search_query
            else:
                return search_text.endswith(search_query)

        return False

    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calculate relevance score for a match"""
        if not query or not text:
            return 0.0

        # Basic relevance based on text similarity
        similarity = SequenceMatcher(None, query.lower(), text.lower()).ratio()

        # Boost score for exact matches
        if query.lower() == text.lower():
            return 1.0

        # Boost score for word starts
        if text.lower().startswith(query.lower()):
            return min(0.9, similarity + 0.2)

        return similarity

    def _rank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Rank and sort search results"""
        # Calculate relevance scores if not already set
        for result in results:
            if result.relevance_score == 0.0 and query:
                result.relevance_score = self._calculate_relevance(query, result.match_text or result.context)

        # Sort by relevance score (descending), then by quest name, then by item type
        sorted_results = sorted(results, key=lambda r: (
            -r.relevance_score,
            r.quest_name.lower(),
            r.item_type.lower(),
            r.item_id.lower()
        ))

        # Remove duplicates (keep highest scoring version)
        seen = set()
        deduplicated_results = []
        for result in sorted_results:
            key = (result.item_type, result.item_id, result.parent_id)
            if key not in seen:
                seen.add(key)
                deduplicated_results.append(result)

        return deduplicated_results

    def get_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = set()

        if not partial_query or not self.context.dialogue_trees:
            return []

        partial_lower = partial_query.lower()

        # Extract common words and phrases from content
        for quest_id, dialogue_tree in self.context.dialogue_trees.items():
            # From dialogue nodes
            for node in dialogue_tree.nodes:
                if node.text:
                    words = node.text.lower().split()
                    for word in words:
                        if word.startswith(partial_lower) and len(word) > 2:
                            suggestions.add(word)

                # From choices
                for choice in node.choices:
                    if choice.text:
                        words = choice.text.lower().split()
                        for word in words:
                            if word.startswith(partial_lower) and len(word) > 2:
                                suggestions.add(word)

        # Sort and limit suggestions
        sorted_suggestions = sorted(suggestions, key=len)[:limit]
        return sorted_suggestions