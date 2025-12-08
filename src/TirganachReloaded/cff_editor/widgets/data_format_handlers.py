#!/usr/bin/env python3
"""
Data Format Handlers for Import/Export

Provides handlers for different data formats used in quest import/export operations.
"""

import json
import xml.etree.ElementTree as ET
import csv
import yaml
import pickle
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import asdict
from datetime import datetime
import re

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice, DialogueCondition, DialogueAction,
        DialogueConditionType, DialogueActionType
    )
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DataFormatHandler:
    """Base class for data format handlers"""

    def __init__(self):
        self.supported_extensions = []

    def can_handle(self, file_path: str) -> bool:
        """Check if this handler can handle the given file"""
        return Path(file_path).suffix.lower() in self.supported_extensions

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import data from file"""
        raise NotImplementedError("Subclasses must implement import_data")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to file"""
        raise NotImplementedError("Subclasses must implement export_data")

    def validate_data(self, data: dict) -> Tuple[bool, List[str]]:
        """Validate imported data"""
        errors = []
        # Basic validation
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
            return False, errors
        return True, errors


class JSONFormatHandler(DataFormatHandler):
    """Handler for JSON format"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.json']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import JSON data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to JSON"""
        try:
            pretty_print = kwargs.get('pretty_print', True)
            include_metadata = kwargs.get('include_metadata', True)

            # Add metadata if requested
            if include_metadata:
                data['metadata'] = data.get('metadata', {})
                data['metadata'].update({
                    'exported_at': datetime.now().isoformat(),
                    'format_version': '1.0'
                })

            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty_print:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return False


class XMLFormatHandler(DataFormatHandler):
    """Handler for XML format"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.xml']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import XML data"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise ValueError(f"Error reading XML file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to XML"""
        try:
            root = self._dict_to_xml('quest_data', data)
            tree = ET.ElementTree(root)

            # Pretty print XML
            self._indent_xml(root)

            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            logger.error(f"Error exporting XML: {e}")
            return False

    def _xml_to_dict(self, element: ET.Element) -> dict:
        """Convert XML element to dictionary"""
        result = {}

        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib

        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['#text'] = element.text.strip()

        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result

    def _dict_to_xml(self, tag: str, data: dict) -> ET.Element:
        """Convert dictionary to XML element"""
        element = ET.Element(tag)

        if isinstance(data, dict):
            # Handle attributes
            if '@attributes' in data:
                element.attrib.update(data['@attributes'])
                del data['@attributes']

            # Handle text content
            if '#text' in data:
                element.text = str(data['#text'])
                del data['#text']

            # Handle children
            for key, value in data.items():
                child = self._dict_to_xml(key, value)
                element.append(child)
        else:
            element.text = str(data)

        return element

    def _indent_xml(self, elem: ET.Element, level: int = 0):
        """Add indentation to XML for pretty printing"""
        indent = "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = "\\n" + indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = "\\n" + indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = "\\n" + indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = "\\n" + indent


class YAMLFormatHandler(DataFormatHandler):
    """Handler for YAML format"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.yaml', '.yml']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import YAML data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise ValueError(f"Error reading YAML file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to YAML"""
        try:
            include_metadata = kwargs.get('include_metadata', True)

            # Add metadata if requested
            if include_metadata:
                data['metadata'] = data.get('metadata', {})
                data['metadata'].update({
                    'exported_at': datetime.now().isoformat(),
                    'format_version': '1.0'
                })

            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exporting YAML: {e}")
            return False


class CSVFormatHandler(DataFormatHandler):
    """Handler for CSV format (主要用于 dialogue choices)"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.csv']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import CSV data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                return {'csv_data': rows}
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to CSV"""
        try:
            # Extract dialogue choices for CSV export
            choices = data.get('dialogue_choices', [])
            if not choices:
                # Try to extract choices from dialogue trees
                dialogue_trees = data.get('dialogue_trees', {})
                for tree_id, tree in dialogue_trees.items():
                    if isinstance(tree, dict) and 'nodes' in tree:
                        for node in tree['nodes']:
                            if 'choices' in node:
                                for choice in node['choices']:
                                    choice['tree_id'] = tree_id
                                    choice['node_id'] = node.get('node_id', '')
                                    choices.append(choice)

            if not choices:
                logger.warning("No dialogue choices found for CSV export")
                return False

            # Prepare CSV data
            fieldnames = ['tree_id', 'node_id', 'choice_index', 'text', 'answer_id', 'next_node', 'conditions', 'actions']
            csv_data = []

            for i, choice in enumerate(choices):
                row = {
                    'tree_id': choice.get('tree_id', ''),
                    'node_id': choice.get('node_id', ''),
                    'choice_index': i,
                    'text': choice.get('text', ''),
                    'answer_id': choice.get('answer_id', ''),
                    'next_node': choice.get('next_node', ''),
                    'conditions': json.dumps(choice.get('conditions', [])),
                    'actions': json.dumps(choice.get('actions', []))
                }
                csv_data.append(row)

            # Write CSV
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            return True
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return False


class LUAFormatHandler(DataFormatHandler):
    """Handler for LUA script format (SpellForce compatible)"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.lua']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import LUA script data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lua_content = f.read()

            # Basic LUA parsing (simplified)
            data = {
                'lua_script': lua_content,
                'format': 'lua',
                'parsed_data': self._parse_lua_content(lua_content)
            }
            return data
        except Exception as e:
            raise ValueError(f"Error reading LUA file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to LUA script"""
        try:
            include_metadata = kwargs.get('include_metadata', True)
            quest_id = data.get('quest_id', 'unknown')

            lua_script = self._generate_lua_script(data, include_metadata)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(lua_script)

            return True
        except Exception as e:
            logger.error(f"Error exporting LUA: {e}")
            return False

    def _parse_lua_content(self, content: str) -> dict:
        """Parse LUA content into structured data"""
        parsed = {
            'functions': [],
            'variables': [],
            'quest_events': []
        }

        # Extract function definitions
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(func_pattern, content):
            parsed['functions'].append(match.group(1))

        # Extract variable assignments
        var_pattern = r'(\w+)\s*=\s*([^;\n]+)'
        for match in re.finditer(var_pattern, content):
            var_name = match.group(1)
            if not var_name.startswith('function') and var_name != 'end':
                parsed['variables'].append({
                    'name': var_name,
                    'value': match.group(2).strip()
                })

        # Extract quest event calls
        event_pattern = r'(OnBeginDialog|OnAnswer|OnQuestStateChange)\s*\([^)]+\)'
        for match in re.finditer(event_pattern, content):
            parsed['quest_events'].append(match.group(0))

        return parsed

    def _generate_lua_script(self, data: dict, include_metadata: bool) -> str:
        """Generate LUA script from quest data"""
        script_lines = []

        # Add header comments
        if include_metadata:
            script_lines.extend([
                "-- Quest Script Generated by Quest Editor",
                f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"-- Quest ID: {data.get('quest_id', 'unknown')}",
                f"-- Quest Name: {data.get('quest_name', 'unknown')}",
                ""
            ])

        quest_id = data.get('quest_id', 1)

        # Generate quest functions
        dialogue_trees = data.get('dialogue_trees', {})
        for tree_id, tree in dialogue_trees.items():
            if isinstance(tree, dict) and 'nodes' in tree:
                script_lines.extend(self._generate_dialogue_functions(tree_id, tree, quest_id))

        # Generate quest state management
        script_lines.extend(self._generate_quest_state_functions(data, quest_id))

        return '\n'.join(script_lines)

    def _generate_dialogue_functions(self, tree_id: str, tree: dict, quest_id: int) -> List[str]:
        """Generate dialogue functions for a dialogue tree"""
        lines = []

        # Begin dialogue function
        lines.append(f"function OnBeginDialog_{tree_id}(entity)")
        lines.append(f"    -- Dialogue tree: {tree.get('name', tree_id)}")

        # Find start node
        start_node = None
        for node in tree.get('nodes', []):
            if node.get('node_type') == 'start':
                start_node = node
                break

        if start_node:
            lines.extend(self._generate_dialogue_options(start_node, tree, 1))

        lines.append("end")
        lines.append("")

        # Answer functions
        for node in tree.get('nodes', []):
            for i, choice in enumerate(node.get('choices', [])):
                if choice.get('answer_id'):
                    lines.extend(self._generate_answer_function(choice, tree, quest_id))

        return lines

    def _generate_dialogue_options(self, node: dict, tree: dict, indent_level: int) -> List[str]:
        """Generate dialogue options for a node"""
        lines = []
        indent = "    " * indent_level

        if node.get('text'):
            lines.append(f"{indent}entity:Say(\"{node['text']}\")")

        choices = node.get('choices', [])
        if choices:
            for i, choice in enumerate(choices):
                answer_id = choice.get('answer_id')
                if answer_id:
                    lines.append(f"{indent}entity:Choice({answer_id}, \"{choice['text']}\")")

        return lines

    def _generate_answer_function(self, choice: dict, tree: dict, quest_id: int) -> List[str]:
        """Generate answer function for a choice"""
        lines = []
        answer_id = choice.get('answer_id')
        next_node_id = choice.get('next_node')

        if not answer_id:
            return lines

        lines.append(f"function OnAnswer_{answer_id}(entity)")

        # Add actions
        for action in choice.get('actions', []):
            lines.append(f"    -- Action: {action.get('type', 'unknown')}")
            # Generate specific action code based on type

        # Navigate to next node
        if next_node_id:
            next_node = self._find_node_by_id(tree, next_node_id)
            if next_node:
                lines.extend(self._generate_dialogue_options(next_node, tree, 2))

        lines.append("end")
        lines.append("")

        return lines

    def _generate_quest_state_functions(self, data: dict, quest_id: int) -> List[str]:
        """Generate quest state management functions"""
        lines = []

        lines.extend([
            "-- Quest State Management",
            "function OnQuestStateChange(entity, questId, newState)",
            f"    if questId == {quest_id} then",
            "        case newState of",
            "            0: -- Unknown",
            "            1: -- Known",
            "            2: -- Active",
            "            3: -- Solved",
            "            4: -- Failed",
            "        end",
            "    end",
            "end",
            ""
        ])

        return lines

    def _find_node_by_id(self, tree: dict, node_id: str) -> Optional[dict]:
        """Find a node by ID in the dialogue tree"""
        for node in tree.get('nodes', []):
            if node.get('node_id') == node_id:
                return node
        return None


class PickleFormatHandler(DataFormatHandler):
    """Handler for Python pickle format"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pkl', '.pickle']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import pickled data"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                return data
        except Exception as e:
            raise ValueError(f"Error reading pickle file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to pickle"""
        try:
            include_metadata = kwargs.get('include_metadata', True)

            if include_metadata:
                data['metadata'] = data.get('metadata', {})
                data['metadata'].update({
                    'exported_at': datetime.now().isoformat(),
                    'format_version': '1.0'
                })

            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            logger.error(f"Error exporting pickle: {e}")
            return False


class ZipFormatHandler(DataFormatHandler):
    """Handler for ZIP archive format (for complete quest packages)"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.zip']

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import data from ZIP archive"""
        try:
            extracted_data = {}

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if not file_info.is_dir():
                        with zip_ref.open(file_info) as file:
                            content = file.read()
                            file_path = file_info.filename

                            # Try to parse based on file extension
                            if file_path.endswith('.json'):
                                extracted_data[file_path] = json.loads(content.decode('utf-8'))
                            elif file_path.endswith('.xml'):
                                root = ET.fromstring(content)
                                extracted_data[file_path] = self._xml_to_dict(root)
                            else:
                                extracted_data[file_path] = content.decode('utf-8')

            return extracted_data
        except Exception as e:
            raise ValueError(f"Error reading ZIP file: {e}")

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data to ZIP archive"""
        try:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                # Export main data as JSON
                json_data = json.dumps(data, indent=2, ensure_ascii=False)
                zip_ref.writestr('quest_data.json', json_data)

                # Export dialogue trees separately
                dialogue_trees = data.get('dialogue_trees', {})
                for tree_id, tree in dialogue_trees.items():
                    tree_json = json.dumps(tree, indent=2, ensure_ascii=False)
                    zip_ref.writestr(f'dialogue_trees/{tree_id}.json', tree_json)

                # Export LUA script if requested
                if kwargs.get('generate_lua', False):
                    lua_handler = LUAFormatHandler()
                    lua_script = lua_handler._generate_lua_script(data, True)
                    zip_ref.writestr('quest_script.lua', lua_script)

            return True
        except Exception as e:
            logger.error(f"Error exporting ZIP: {e}")
            return False

    def _xml_to_dict(self, element: ET.Element) -> dict:
        """Convert XML element to dictionary (same as XMLFormatHandler)"""
        result = {}
        if element.attrib:
            result['@attributes'] = element.attrib
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['#text'] = element.text.strip()
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        return result


class DataFormatManager:
    """Manager for data format handlers"""

    def __init__(self):
        self.handlers = {
            '.json': JSONFormatHandler(),
            '.xml': XMLFormatHandler(),
            '.yaml': YAMLFormatHandler(),
            '.yml': YAMLFormatHandler(),
            '.csv': CSVFormatHandler(),
            '.lua': LUAFormatHandler(),
            '.pkl': PickleFormatHandler(),
            '.pickle': PickleFormatHandler(),
            '.zip': ZipFormatHandler()
        }

    def get_handler(self, file_path: str) -> Optional[DataFormatHandler]:
        """Get appropriate handler for file"""
        extension = Path(file_path).suffix.lower()
        return self.handlers.get(extension)

    def import_data(self, file_path: str, **kwargs) -> dict:
        """Import data using appropriate handler"""
        handler = self.get_handler(file_path)
        if not handler:
            raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")

        return handler.import_data(file_path, **kwargs)

    def export_data(self, data: dict, file_path: str, **kwargs) -> bool:
        """Export data using appropriate handler"""
        handler = self.get_handler(file_path)
        if not handler:
            raise ValueError(f"Unsupported file format: {Path(file_path).suffix}")

        return handler.export_data(data, file_path, **kwargs)

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return list(self.handlers.keys())