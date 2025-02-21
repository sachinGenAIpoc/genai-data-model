# src/types/suggestions.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class EntitySuggestion:
    """Represents a suggested entity from the mapping process"""
    name: str
    attributes: List[str]
    source: str
    confidence: float
    description: str

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "attributes": self.attributes,
            "source": self.source,
            "confidence": self.confidence,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EntitySuggestion':
        """Create from dictionary representation"""
        return cls(
            name=data["name"],
            attributes=data["attributes"],
            source=data["source"],
            confidence=data["confidence"],
            description=data["description"]
        )

    def validate(self) -> bool:
        """Validate the entity suggestion"""
        if not self.name or not isinstance(self.name, str):
            return False
        if not isinstance(self.attributes, list):
            return False
        if not self.source or not isinstance(self.source, str):
            return False
        if not isinstance(self.confidence, (int, float)):
            return False
        if self.confidence < 0 or self.confidence > 1:
            return False
        if not self.description or not isinstance(self.description, str):
            return False
        return True

@dataclass
class RelationSuggestion:
    """Represents a suggested relationship between entities"""
    source_entity: str
    target_entity: str
    relation_type: str
    cardinality: str
    confidence: float
    description: str

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "source_entity": self.source_entity,
            "target_entity": self.target_entity,
            "relation_type": self.relation_type,
            "cardinality": self.cardinality,
            "confidence": self.confidence,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RelationSuggestion':
        """Create from dictionary representation"""
        return cls(
            source_entity=data["source_entity"],
            target_entity=data["target_entity"],
            relation_type=data["relation_type"],
            cardinality=data["cardinality"],
            confidence=data["confidence"],
            description=data["description"]
        )

    def validate(self) -> bool:
        """Validate the relation suggestion"""
        if not self.source_entity or not isinstance(self.source_entity, str):
            return False
        if not self.target_entity or not isinstance(self.target_entity, str):
            return False
        if not self.relation_type or not isinstance(self.relation_type, str):
            return False
        if not self.cardinality or not isinstance(self.cardinality, str):
            return False
        if not isinstance(self.confidence, (int, float)):
            return False
        if self.confidence < 0 or self.confidence > 1:
            return False
        if not self.description or not isinstance(self.description, str):
            return False
        return True

    def get_inverse(self) -> 'RelationSuggestion':
        """Get the inverse relationship"""
        # Map cardinalities
        cardinality_map = {
            "1:1": "1:1",
            "1:N": "N:1",
            "N:1": "1:N",
            "M:N": "M:N"
        }
        
        return RelationSuggestion(
            source_entity=self.target_entity,
            target_entity=self.source_entity,
            relation_type=f"inverse_{self.relation_type}",
            cardinality=cardinality_map.get(self.cardinality, self.cardinality),
            confidence=self.confidence,
            description=f"Inverse of: {self.description}"
        )

# Helper functions
def validate_suggestions(
    entities: List[EntitySuggestion],
    relations: List[RelationSuggestion]
) -> bool:
    """Validate both entity and relation suggestions"""
    # Validate all entities
    if not all(entity.validate() for entity in entities):
        return False
        
    # Get all entity names
    entity_names = {entity.name for entity in entities}
    
    # Validate all relations
    for relation in relations:
        if not relation.validate():
            return False
        # Check that relation entities exist
        if relation.source_entity not in entity_names or relation.target_entity not in entity_names:
            return False
            
    return True

def merge_suggestions(
    suggestions1: List[EntitySuggestion],
    suggestions2: List[EntitySuggestion]
) -> List[EntitySuggestion]:
    """Merge two lists of entity suggestions"""
    merged = {}
    
    # Process first list
    for suggestion in suggestions1:
        merged[suggestion.name] = suggestion
        
    # Process second list, merging if entity exists
    for suggestion in suggestions2:
        if suggestion.name in merged:
            existing = merged[suggestion.name]
            merged[suggestion.name] = EntitySuggestion(
                name=suggestion.name,
                attributes=list(set(existing.attributes + suggestion.attributes)),
                source=f"{existing.source}, {suggestion.source}",
                confidence=max(existing.confidence, suggestion.confidence),
                description=f"{existing.description}\n{suggestion.description}"
            )
        else:
            merged[suggestion.name] = suggestion
            
    return list(merged.values())