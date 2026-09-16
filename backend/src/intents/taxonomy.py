"""
Taxonomy Specification Module
Loads, validates, and surfaces the 8 empirical intents for @AppleSupport.
"""

import os
import yaml
import json
from typing import Dict, Any, List

TAXONOMY_YAML = "data/intent_taxonomy.yaml"
TAXONOMY_JSON = "taxonomy/taxonomy_spec.json"

class IntentTaxonomy:
    def __init__(self, spec_path: str = TAXONOMY_YAML):
        self.spec_path = spec_path
        self.intents: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.spec_path) and self.spec_path.endswith((".yaml", ".yml")):
            with open(self.spec_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        elif os.path.exists(TAXONOMY_JSON):
            with open(TAXONOMY_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_intent_names(self) -> List[str]:
        return list(self.intents.keys())

    def get_intent_details(self, intent_name: str) -> Dict[str, Any]:
        return self.intents.get(intent_name, {})

def load_taxonomy() -> IntentTaxonomy:
    return IntentTaxonomy()
