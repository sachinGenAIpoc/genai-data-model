# src/logical_model/generator.py
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class RelationType(Enum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "M:N"

@dataclass
class Attribute:
    name: str
    data_type: str
    is_primary: bool = False
    is_foreign: bool = False
    is_nullable: bool = True
    description: str = ""

@dataclass
class Entity:
    name: str
    attributes: List[Attribute]
    description: str = ""

@dataclass
class Relationship:
    source_entity: str
    target_entity: str
    relation_type: RelationType
    description: str = ""

class LogicalModelGenerator:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []

    def analyze_datapedia(self, datapedia_data: Dict) -> None:
        """Extract entities and relationships from datapedia"""
        for entity_name, entity_data in datapedia_data.get("entities", {}).items():
            attributes = []
            
            # Process attributes
            for attr_name, attr_data in entity_data.get("attributes", {}).items():
                attributes.append(
                    Attribute(
                        name=attr_name,
                        data_type=attr_data.get("type", "string"),
                        is_primary=attr_name.endswith("_id"),
                        description=attr_data.get("description", "")
                    )
                )
            
            # Create entity
            self.entities[entity_name] = Entity(
                name=entity_name,
                attributes=attributes,
                description=entity_data.get("definition", "")
            )
            
            # Process relationships
            for rel in entity_data.get("relationships", []):
                self.relationships.append(
                    Relationship(
                        source_entity=entity_name,
                        target_entity=rel["target"],
                        relation_type=RelationType.ONE_TO_MANY if rel["type"] == "has_many" else RelationType.ONE_TO_ONE,
                        description=rel.get("description", "")
                    )
                )

    def analyze_conceptual_model(self, conceptual_model: Dict) -> None:
        """Enhance logical model with conceptual model information"""
        for concept_name, concept_data in conceptual_model.get("business_concepts", {}).items():
            # Update existing entities or create new ones
            if concept_name in self.entities:
                entity = self.entities[concept_name]
                entity.description = f"{entity.description}\nBusiness Concept: {concept_data['description']}"
            else:
                attributes = [
                    Attribute(
                        name=attr,
                        data_type="string",
                        description="From conceptual model"
                    )
                    for attr in concept_data.get("attributes", [])
                ]
                self.entities[concept_name] = Entity(
                    name=concept_name,
                    attributes=attributes,
                    description=concept_data.get("description", "")
                )

    def analyze_existing_schema(self, schema: Dict) -> None:
        """Incorporate existing schema details"""
        for table_name, table_data in schema.get("tables", {}).items():
            attributes = []
            
            # Process columns
            for column in table_data.get("columns", []):
                attributes.append(
                    Attribute(
                        name=column["name"],
                        data_type=column["type"],
                        is_primary=column.get("primary_key", False),
                        is_foreign="foreign_key" in column,
                        is_nullable=column.get("nullable", True)
                    )
                )
            
            # Update existing entities or create new ones
            if table_name in self.entities:
                entity = self.entities[table_name]
                self._merge_attributes(entity, attributes)
            else:
                self.entities[table_name] = Entity(
                    name=table_name,
                    attributes=attributes
                )

    def _merge_attributes(self, entity: Entity, new_attributes: List[Attribute]) -> None:
        """Merge attributes while preserving existing information"""
        existing_names = {attr.name for attr in entity.attributes}
        
        for new_attr in new_attributes:
            if new_attr.name not in existing_names:
                entity.attributes.append(new_attr)
            else:
                # Update existing attribute with additional information
                for existing_attr in entity.attributes:
                    if existing_attr.name == new_attr.name:
                        existing_attr.data_type = new_attr.data_type
                        existing_attr.is_primary = existing_attr.is_primary or new_attr.is_primary
                        existing_attr.is_foreign = existing_attr.is_foreign or new_attr.is_foreign
                        existing_attr.is_nullable = existing_attr.is_nullable and new_attr.is_nullable

    def generate_logical_model(self) -> Dict[str, Any]:
        """Generate the final logical model"""
        return {
            "entities": {
                name: {
                    "description": entity.description,
                    "attributes": [
                        {
                            "name": attr.name,
                            "type": attr.data_type,
                            "is_primary": attr.is_primary,
                            "is_foreign": attr.is_foreign,
                            "is_nullable": attr.is_nullable,
                            "description": attr.description
                        }
                        for attr in entity.attributes
                    ]
                }
                for name, entity in self.entities.items()
            },
            "relationships": [
                {
                    "source": rel.source_entity,
                    "target": rel.target_entity,
                    "type": rel.relation_type.value,
                    "description": rel.description
                }
                for rel in self.relationships
            ]
        }

# Example usage
def create_logical_model(
    datapedia_data: Dict,
    conceptual_model: Dict,
    existing_schema: Dict
) -> Dict[str, Any]:
    generator = LogicalModelGenerator()
    
    # Process each input source
    generator.analyze_datapedia(datapedia_data)
    generator.analyze_conceptual_model(conceptual_model)
    generator.analyze_existing_schema(existing_schema)
    
    # Generate final model
    return generator.generate_logical_model()