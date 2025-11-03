"""Python adaptation of C# SFEngine core patterns"""

import logging
from typing import Any, Dict

from .services.data_service import DataService
from .services.validation_service import ValidationService


class EngineCore:
    """
    Core engine following C# SFEngine patterns but adapted for Python.

    Manages services, configuration, and core functionality similar to C# implementation.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.services: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._initialized = False

    def initialize(self):
        """Initialize engine services following C# startup patterns"""
        self._setup_services()
        self._initialized = True
        self.logger.info("EngineCore initialized successfully")

    def _setup_services(self):
        """Setup core services following C# patterns"""
        self.services["data"] = DataService()
        self.services["validation"] = ValidationService()

    def get_service(self, service_name: str):
        """Get service following C# service locator pattern"""
        return self.services.get(service_name)

    @property
    def is_initialized(self) -> bool:
        return self._initialized
