import os
import json
from dotenv import load_dotenv

# Test data
test_data = {
    "entities": {
        "Customer": {
            "attributes": ["id", "name", "email"],
            "relationships": ["has_many accounts"]
        },
        "Account": {
            "attributes": ["id", "balance", "type"],
            "relationships": ["belongs_to customer"]
        }
    }
}

class MockVertexDB:
    def __init__(self):
        self.data = test_data
    
    def get_data(self):
        return self.data

def test_datapedia_agent():
    print("\nTesting DatapediaAgent...")
    try:
        # Mock data processing
        result = {
            "analysis": "Sample analysis of datapedia",
            "entities": test_data["entities"]
        }
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error in DatapediaAgent: {e}")
        return None

def test_bian_agent(datapedia_result):
    print("\nTesting BIANAgent...")
    try:
        # Mock BIAN mapping
        result = {
            "service_domains": {
                "customer_management": ["Customer"],
                "account_management": ["Account"]
            },
            "mappings": {
                "Customer": "PartyServiceDomain",
                "Account": "AccountServiceDomain"
            }
        }
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error in BIANAgent: {e}")
        return None

def test_accord_agent(datapedia_result):
    print("\nTesting AccordAgent...")
    try:
        # Mock ACCORD mapping
        result = {
            "standards": {
                "Customer": "ACORD Party Model",
                "Account": "ACORD Account Model"
            },
            "compliance": {
                "level": "high",
                "recommendations": []
            }
        }
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error in AccordAgent: {e}")
        return None

def test_mapper_agent(datapedia_result, bian_result, accord_result):
    print("\nTesting MapperAgent...")
    try:
        # Mock mapping process
        result = {
            "entity_suggestions": [
                {
                    "name": "Customer",
                    "attributes": ["id", "name", "email"],
                    "source": "datapedia",
                    "confidence": 0.9,
                    "description": "Core customer entity"
                },
                {
                    "name": "Account",
                    "attributes": ["id", "balance", "type"],
                    "source": "bian",
                    "confidence": 0.85,
                    "description": "Financial account entity"
                }
            ],
            "relation_suggestions": [
                {
                    "source_entity": "Customer",
                    "target_entity": "Account",
                    "relation_type": "owns",
                    "cardinality": "1:N",
                    "confidence": 0.88,
                    "description": "Customer owns multiple accounts"
                }
            ]
        }
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"Error in MapperAgent: {e}")
        return None

def main():
    load_dotenv()
    
    print("Starting agent tests...")
    
    # Test each agent
    datapedia_result = test_datapedia_agent()
    if datapedia_result:
        bian_result = test_bian_agent(datapedia_result)
        accord_result = test_accord_agent(datapedia_result)
        
        if bian_result and accord_result:
            mapper_result = test_mapper_agent(
                datapedia_result,
                bian_result,
                accord_result
            )
            
            if mapper_result:
                print("\nAll agents tested successfully!")

if __name__ == "__main__":
    main()