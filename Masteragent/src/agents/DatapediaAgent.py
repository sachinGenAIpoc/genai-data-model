from typing import Dict, Any, List
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class DatapediaAgent:
    def __init__(self, vertex_db_client):
        self.vertex_db = vertex_db_client
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3
        )
        
        self.analysis_prompt = """
        Analyze the following data sources and provide a comprehensive analysis:
        
        Datapedia: {datapedia}
        Conceptual Model: {conceptual}
        Schema: {schema}
        
        Provide analysis of:
        1. Entity relationships
        2. Data consistency
        3. Business rules
        4. Technical constraints
        
        Format your response with clear sections for each aspect.
        """

    async def process(self) -> Dict[str, Any]:
        try:
            # Get data from VertexDB
            vertex_data = self.vertex_db.get_data()
            datapedia = vertex_data.get("datapedia", {})
            conceptual_model = vertex_data.get("conceptual_model", {})
            schema = vertex_data.get("schema", {})

            # Generate analysis using LLM
            messages = [
                HumanMessage(
                    content=self.analysis_prompt.format(
                        datapedia=datapedia,
                        conceptual=conceptual_model,
                        schema=schema
                    )
                )
            ]
            
            response = await self.llm.ainvoke(messages)
            
            analysis_result = {
                "raw_data": {
                    "datapedia": datapedia,
                    "conceptual_model": conceptual_model,
                    "schema": schema
                },
                "analysis": response.content,
                "entities": self._extract_entities(datapedia, conceptual_model, schema),
                "relationships": self._extract_relationships(datapedia, conceptual_model, schema)
            }

            return analysis_result

        except Exception as e:
            logging.error(f"Error in DatapediaAgent: {e}")
            raise

    def _extract_entities(self, datapedia: Dict, conceptual: Dict, schema: Dict) -> Dict[str, Any]:
        entities = {}
        
        # Extract from datapedia
        if "entities" in datapedia:
            for entity_name, entity_data in datapedia["entities"].items():
                entities[entity_name] = {
                    "source": "datapedia",
                    "attributes": entity_data.get("attributes", []),
                    "description": entity_data.get("definition", "")
                }
                
        # Extract from conceptual model
        if "entities" in conceptual:
            for entity_name, entity_data in conceptual["entities"].items():
                if entity_name not in entities:
                    entities[entity_name] = {
                        "source": "conceptual",
                        "attributes": entity_data.get("attributes", []),
                        "description": entity_data.get("description", "")
                    }
                    
        # Extract from schema
        if "tables" in schema:
            for table_name, table_data in schema["tables"].items():
                if table_name not in entities:
                    entities[table_name] = {
                        "source": "schema",
                        "attributes": [col["name"] for col in table_data.get("columns", [])],
                        "description": table_data.get("description", "")
                    }
                    
        return entities

    def _extract_relationships(self, datapedia: Dict, conceptual: Dict, schema: Dict) -> List[Dict]:
        relationships = []
        
        # Extract from datapedia
        if "relationships" in datapedia:
            for rel in datapedia["relationships"]:
                relationships.append({
                    "source": "datapedia",
                    **rel
                })
                
        # Extract from conceptual model
        if "relationships" in conceptual:
            for rel in conceptual["relationships"]:
                relationships.append({
                    "source": "conceptual",
                    **rel
                })
                
        # Extract from schema (foreign keys)
        if "tables" in schema:
            for table_name, table_data in schema["tables"].items():
                for column in table_data.get("columns", []):
                    if "foreign_key" in column:
                        relationships.append({
                            "source": "schema",
                            "source_entity": table_name,
                            "target_entity": column["foreign_key"]["table"],
                            "type": "foreign_key",
                            "cardinality": "N:1"
                        })
                        
        return relationships