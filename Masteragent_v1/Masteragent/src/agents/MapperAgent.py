from typing import Dict, Any, List
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .DatapediaAgent import DatapediaAgent
from .BIANAgent import BIANAgent
from .AccordAgent import AccordAgent
from src.types.suggestions import EntitySuggestion, RelationSuggestion

class MapperAgent:
    def __init__(self, vertex_db_client):
        self.datapedia_agent = DatapediaAgent(vertex_db_client)
        self.bian_agent = BIANAgent()
        self.accord_agent = AccordAgent()
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3
        )
        
        # Define prompts for entity and relationship analysis
        self.entity_prompt = """
        Analyze these integrated data sources and suggest comprehensive entities:
        
        Datapedia Analysis: {datapedia}
        BIAN Analysis: {bian}
        ACCORD Analysis: {accord}
        
        For each entity, provide in this exact format:
        Entity: [entity name]
        Description: [detailed description integrating all sources]
        Attributes: [comma-separated list of all attributes]
        Source: [primary source framework]
        Confidence: [score between 0 and 1]
        
        Consider:
        - Merge similar entities from different sources
        - Include all relevant attributes
        - Maintain data consistency
        - Follow industry standards
        - Consider both banking and insurance domains
        """
        
        self.relation_prompt = """
        Analyze and suggest relationships between the entities:
        
        Available Entities: {entities}
        
        Source Data:
        Datapedia: {datapedia}
        BIAN Framework: {bian}
        ACCORD Standards: {accord}
        
        For each relationship, provide in this exact format:
        Relation: [relationship name]
        Source: [source entity]
        Target: [target entity]
        Type: [relationship type]
        Cardinality: [cardinality]
        Confidence: [score between 0 and 1]
        Description: [detailed description]
        
        Consider:
        - Business rules from all sources
        - Industry standard patterns
        - Data integrity requirements
        - Cross-domain relationships
        """

    async def analyze_and_suggest(self) -> Dict[str, Any]:
        try:
            logging.info("Starting MapperAgent analysis")
            
            # Get results from all agents
            datapedia_result = await self.datapedia_agent.process()
            logging.info("Datapedia analysis complete")
            
            bian_result = await self.bian_agent.process(datapedia_result)
            logging.info("BIAN analysis complete")
            
            accord_result = await self.accord_agent.process(datapedia_result)
            logging.info("ACCORD analysis complete")
            
            # Generate entity suggestions
            entity_response = await self._get_llm_response(
                self.entity_prompt,
                datapedia=datapedia_result,
                bian=bian_result,
                accord=accord_result
            )
            entity_suggestions = self._parse_entity_suggestions(entity_response)
            logging.info(f"Generated {len(entity_suggestions)} entity suggestions")
            
            # Generate relation suggestions
            relation_response = await self._get_llm_response(
                self.relation_prompt,
                entities=entity_suggestions,
                datapedia=datapedia_result,
                bian=bian_result,
                accord=accord_result
            )
            relation_suggestions = self._parse_relation_suggestions(relation_response)
            logging.info(f"Generated {len(relation_suggestions)} relation suggestions")
            
            return {
                "entity_suggestions": entity_suggestions,
                "relation_suggestions": relation_suggestions,
                "source_analyses": {
                    "datapedia": datapedia_result,
                    "bian": bian_result,
                    "accord": accord_result
                }
            }
            
        except Exception as e:
            logging.error(f"Error in MapperAgent analyze_and_suggest: {str(e)}")
            raise

    async def _get_llm_response(self, prompt: str, **kwargs) -> str:
        try:
            messages = [HumanMessage(content=prompt.format(**kwargs))]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logging.error(f"Error in LLM response: {str(e)}")
            return ""

    def _parse_entity_suggestions(self, text: str) -> List[EntitySuggestion]:
        try:
            entities = []
            lines = text.split('\n')
            current_entity = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Entity:'):
                    if current_entity:
                        entities.append(current_entity)
                    name = line.split('Entity:')[1].strip()
                    current_entity = {
                        'name': name,
                        'attributes': [],
                        'description': '',
                        'source': '',
                        'confidence': 0.0
                    }
                elif current_entity:
                    if line.startswith('Attributes:'):
                        attrs = line.split('Attributes:')[1].strip()
                        current_entity['attributes'] = [
                            attr.strip() 
                            for attr in attrs.split(',')
                            if attr.strip()
                        ]
                    elif line.startswith('Description:'):
                        current_entity['description'] = line.split('Description:')[1].strip()
                    elif line.startswith('Source:'):
                        current_entity['source'] = line.split('Source:')[1].strip()
                    elif line.startswith('Confidence:'):
                        try:
                            confidence = float(line.split('Confidence:')[1].strip())
                            current_entity['confidence'] = min(max(confidence, 0.0), 1.0)
                        except ValueError:
                            current_entity['confidence'] = 0.0
            
            if current_entity:
                entities.append(current_entity)
                
            return [
                EntitySuggestion(
                    name=e['name'],
                    attributes=e['attributes'],
                    source=e['source'],
                    confidence=e['confidence'],
                    description=e['description']
                )
                for e in entities
            ]
            
        except Exception as e:
            logging.error(f"Error parsing entity suggestions: {str(e)}")
            return []

    def _parse_relation_suggestions(self, text: str) -> List[RelationSuggestion]:
        try:
            relations = []
            lines = text.split('\n')
            current_relation = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Relation:'):
                    if current_relation:
                        relations.append(current_relation)
                    current_relation = {
                        'source_entity': '',
                        'target_entity': '',
                        'relation_type': '',
                        'cardinality': '',
                        'confidence': 0.0,
                        'description': ''
                    }
                elif current_relation:
                    if line.startswith('Source:'):
                        current_relation['source_entity'] = line.split('Source:')[1].strip()
                    elif line.startswith('Target:'):
                        current_relation['target_entity'] = line.split('Target:')[1].strip()
                    elif line.startswith('Type:'):
                        current_relation['relation_type'] = line.split('Type:')[1].strip()
                    elif line.startswith('Cardinality:'):
                        current_relation['cardinality'] = line.split('Cardinality:')[1].strip()
                    elif line.startswith('Confidence:'):
                        try:
                            confidence = float(line.split('Confidence:')[1].strip())
                            current_relation['confidence'] = min(max(confidence, 0.0), 1.0)
                        except ValueError:
                            current_relation['confidence'] = 0.0
                    elif line.startswith('Description:'):
                        current_relation['description'] = line.split('Description:')[1].strip()
            
            if current_relation:
                relations.append(current_relation)
                
            return [
                RelationSuggestion(
                    source_entity=r['source_entity'],
                    target_entity=r['target_entity'],
                    relation_type=r['relation_type'],
                    cardinality=r['cardinality'],
                    confidence=r['confidence'],
                    description=r['description']
                )
                for r in relations
                if r['source_entity'] and r['target_entity']  # Ensure required fields exist
            ]
            
        except Exception as e:
            logging.error(f"Error parsing relation suggestions: {str(e)}")
            return []