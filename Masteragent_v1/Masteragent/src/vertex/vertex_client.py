import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class VertexDBClient:
    def __init__(self):
        self.data_path = Path(__file__).parent / "vertex.json"
        self.data = self._load_data()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load data from vertex.json"""
        try:
            if not self.data_path.exists():
                logging.warning(f"Vertex data file not found at {self.data_path}")
                return self._get_default_data()
                
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                logging.info("Successfully loaded vertex data")
                return data
                
        except Exception as e:
            logging.error(f"Error loading vertex data: {e}")
            return self._get_default_data()

    def _get_default_data(self) -> Dict[str, Any]:
        """Return default empty data structure"""
        return {
            "datapedia": {
                "entities": {},
                "relationships": []
            },
            "conceptual_model": {
                "entities": {},
                "relationships": []
            },
            "schema": {
                "tables": {},
                "relationships": []
            }
        }

    def get_data(self) -> Dict[str, Any]:
        """Get all data"""
        return self.data

    def get_datapedia(self) -> Dict[str, Any]:
        """Get datapedia section"""
        return self.data.get("datapedia", {})

    def get_conceptual_model(self) -> Dict[str, Any]:
        """Get conceptual model section"""
        return self.data.get("conceptual_model", {})

    def get_schema(self) -> Dict[str, Any]:
        """Get schema section"""
        return self.data.get("schema", {})

    def get_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Get specific entity from any source"""
        # Check datapedia
        if entity_name in self.data.get("datapedia", {}).get("entities", {}):
            return {
                "source": "datapedia",
                "data": self.data["datapedia"]["entities"][entity_name]
            }
            
        # Check conceptual model
        if entity_name in self.data.get("conceptual_model", {}).get("entities", {}):
            return {
                "source": "conceptual_model",
                "data": self.data["conceptual_model"]["entities"][entity_name]
            }
            
        # Check schema
        if entity_name in self.data.get("schema", {}).get("tables", {}):
            return {
                "source": "schema",
                "data": self.data["schema"]["tables"][entity_name]
            }
            
        return None

    def get_relationships_for_entity(self, entity_name: str) -> List[Dict[str, Any]]:
        """Get all relationships involving an entity"""
        relationships = []
        
        # Check datapedia relationships
        for rel in self.data.get("datapedia", {}).get("relationships", []):
            if rel.get("source") == entity_name or rel.get("target") == entity_name:
                relationships.append({
                    "source": "datapedia",
                    "data": rel
                })
                
        # Check conceptual model relationships
        for rel in self.data.get("conceptual_model", {}).get("relationships", []):
            if rel.get("source") == entity_name or rel.get("target") == entity_name:
                relationships.append({
                    "source": "conceptual_model",
                    "data": rel
                })
                
        # Check schema relationships
        for table_name, table_data in self.data.get("schema", {}).get("tables", {}).items():
            for column in table_data.get("columns", []):
                if "foreign_key" in column:
                    if table_name == entity_name or column["foreign_key"]["table"] == entity_name:
                        relationships.append({
                            "source": "schema",
                            "data": {
                                "source": table_name,
                                "target": column["foreign_key"]["table"],
                                "type": "foreign_key",
                                "column": column["name"]
                            }
                        })
                        
        return relationships

    def validate_data(self) -> bool:
        """Validate data structure"""
        try:
            required_sections = ["datapedia", "conceptual_model", "schema"]
            for section in required_sections:
                if section not in self.data:
                    logging.error(f"Missing required section: {section}")
                    return False
                    
            # Validate datapedia
            datapedia = self.data["datapedia"]
            if "entities" not in datapedia or "relationships" not in datapedia:
                logging.error("Invalid datapedia structure")
                return False
                
            # Validate conceptual model
            conceptual = self.data["conceptual_model"]
            if "entities" not in conceptual or "relationships" not in conceptual:
                logging.error("Invalid conceptual model structure")
                return False
                
            # Validate schema
            schema = self.data["schema"]
            if "tables" not in schema:
                logging.error("Invalid schema structure")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Error validating data: {e}")
            return False

    def get_vertex_info(self) -> Dict[str, Any]:
        """Get summary information about the vertex data"""
        return {
            "datapedia_entities": len(self.data.get("datapedia", {}).get("entities", {})),
            "datapedia_relationships": len(self.data.get("datapedia", {}).get("relationships", [])),
            "conceptual_entities": len(self.data.get("conceptual_model", {}).get("entities", {})),
            "conceptual_relationships": len(self.data.get("conceptual_model", {}).get("relationships", [])),
            "schema_tables": len(self.data.get("schema", {}).get("tables", {})),
            "is_valid": self.validate_data()
        }