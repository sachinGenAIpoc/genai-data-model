from typing import Dict, Any, List
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class BIANAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3
        )
        
        self.bian_prompt = """
        Map this data model to BIAN service domains:
        
        Data Model: {data}
        
        Provide detailed mapping for:
        1. Service Domains:
           - Identify relevant BIAN service domains
           - Map entities to domains
           - Specify service operations
        
        2. Business Capabilities:
           - Core banking capabilities
           - Supporting capabilities
           - Integration points
        
        3. Business Areas:
           - Functional areas
           - Process areas
           - Cross-cutting concerns
        
        4. Implementation Guidelines:
           - Service domain integration
           - Data consistency rules
           - Operation patterns
        
        Format each section clearly and provide confidence levels for mappings.
        """

    async def process(self, datapedia_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract relevant data for BIAN analysis
            entities = datapedia_result.get("entities", {})
            relationships = datapedia_result.get("relationships", [])
            
            # Prepare data for analysis
            analysis_data = {
                "entities": entities,
                "relationships": relationships,
                "raw_analysis": datapedia_result.get("analysis", "")
            }

            # Generate BIAN analysis
            messages = [
                HumanMessage(
                    content=self.bian_prompt.format(data=analysis_data)
                )
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Process and structure the response
            bian_analysis = {
                "service_domains": self._extract_service_domains(response.content),
                "business_capabilities": self._extract_capabilities(response.content),
                "business_areas": self._extract_business_areas(response.content),
                "implementation": self._extract_implementation_guidelines(response.content),
                "raw_analysis": response.content
            }

            return bian_analysis

        except Exception as e:
            logging.error(f"Error in BIANAgent: {e}")
            raise

    def _extract_service_domains(self, analysis: str) -> Dict[str, Any]:
        domains = {}
        try:
            # Parse service domains section
            if "Service Domains:" in analysis:
                domains_section = analysis.split("Service Domains:")[1].split("2.")[0]
                lines = domains_section.strip().split("\n")
                
                current_domain = None
                for line in lines:
                    if line.strip():
                        if not line.startswith(" "):
                            current_domain = line.strip()
                            domains[current_domain] = {
                                "entities": [],
                                "operations": [],
                                "confidence": 0.0
                            }
                        elif current_domain and "- " in line:
                            item = line.strip("- ").strip()
                            if "Entity:" in item:
                                domains[current_domain]["entities"].append(
                                    item.split("Entity:")[1].strip()
                                )
                            elif "Operation:" in item:
                                domains[current_domain]["operations"].append(
                                    item.split("Operation:")[1].strip()
                                )
                            elif "Confidence:" in item:
                                domains[current_domain]["confidence"] = float(
                                    item.split("Confidence:")[1].strip()
                                )
                                
        except Exception as e:
            logging.error(f"Error extracting service domains: {e}")
            
        return domains

    def _extract_capabilities(self, analysis: str) -> Dict[str, Any]:
        capabilities = {
            "core": [],
            "supporting": [],
            "integration": []
        }
        # Implementation of capability extraction
        return capabilities

    def _extract_business_areas(self, analysis: str) -> Dict[str, Any]:
        areas = {
            "functional": [],
            "process": [],
            "cross_cutting": []
        }
        # Implementation of business area extraction
        return areas

    def _extract_implementation_guidelines(self, analysis: str) -> Dict[str, Any]:
        guidelines = {
            "integration": [],
            "consistency": [],
            "patterns": []
        }
        # Implementation of guideline extraction
        return guidelines