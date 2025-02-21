import os
import sys
from pathlib import Path
import streamlit as st
import asyncio
import networkx as nx
import plotly.graph_objects as go
from dotenv import load_dotenv

# # Add paths
# current_dir = Path(__file__).parent
# project_root = current_dir.parent
# sys.path.extend([str(project_root), str(current_dir)])


current_dir = Path('Masteragent/src/app.py').parent
 
project_root = Path('Masteragent')
 
sys.path.extend([

    str(project_root / 'requirements.txt'),

    str(current_dir / '__init__.py'),

    str(current_dir / 'app.py')

])
 

from agents.MapperAgent import MapperAgent
from types.suggestions import EntitySuggestion, RelationSuggestion

class StreamlitApp:
    def __init__(self):
        self.vertex_db_client = self.get_mock_vertex_client()
        self.mapper_agent = MapperAgent(self.vertex_db_client)
        
    def get_mock_vertex_client(self):
        class MockVertexDB:
            def get_data(self):
                return {
                    "datapedia": {
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
                }
        return MockVertexDB()

    def run(self):
        st.title("Data Model Mapper")
        st.sidebar.header("Controls")
        confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.7)
        if st.button("Genesrate Suggestions"):
            asyncio.run(self._generate_and_display_suggestions(confidence_threshold))

    async def _generate_and_display_suggestions(self, confidence_threshold: float):
        with st.spinner("Analyzing and generating suggestions..."):
            try:
                results = await self.mapper_agent.analyze_and_suggest()
                if results:
                    self._display_entities(results.get("entity_suggestions", []), confidence_threshold)
                    self._display_relations(results.get("relation_suggestions", []), confidence_threshold)
                    self._display_graph(results.get("entity_suggestions", []), results.get("relation_suggestions", []), confidence_threshold)
            except Exception as e:
                st.error(f"Error: {str(e)}")

    def _display_entities(self, entities, threshold: float):
        st.header("Entity Suggestions")
        filtered_entities = [e for e in entities if e.confidence >= threshold]
        for entity in filtered_entities:
            with st.expander(f"{entity.name} ({entity.confidence:.2f})"):
                st.write(f"Description: {entity.description}")
                st.write("Attributes:")
                for attr in entity.attributes:
                    st.write(f"- {attr}")
                st.write(f"Source: {entity.source}")

    def _display_relations(self, relations, threshold: float):
        st.header("Relationship Suggestions")
        filtered_relations = [r for r in relations if r.confidence >= threshold]
        for relation in filtered_relations:
            with st.expander(f"{relation.source_entity} → {relation.target_entity} ({relation.confidence:.2f})"):
                st.write(f"Type: {relation.relation_type}")
                st.write(f"Cardinality: {relation.cardinality}")
                st.write(f"Description: {relation.description}")

    def _display_graph(self, entities, relations, threshold: float):
        st.header("Data Model Visualization")
        G = nx.DiGraph()
        
        # Add nodes
        for entity in entities:
            if entity.confidence >= threshold:
                G.add_node(entity.name)
        
        # Add edges
        for relation in relations:
            if relation.confidence >= threshold:
                G.add_edge(relation.source_entity, relation.target_entity, type=relation.relation_type)
        
        if len(G.nodes) > 0:
            pos = nx.spring_layout(G)
            fig = go.Figure()
            
            # Add edges
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines'))
            
            # Add nodes
            node_x = [pos[node][0] for node in G.nodes()]
            node_y = [pos[node][1] for node in G.nodes()]
            
            fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text', 
                                   hoverinfo='text', text=[node for node in G.nodes()],
                                   textposition="top center", marker=dict(size=20, line_width=2)))
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig)
        else:
            st.info("No entities to display at current confidence threshold.")

if __name__ == "__main__":
    try:
        load_dotenv()
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("GOOGLE_API_KEY not found")
            st.stop()
        app = StreamlitApp()
        app.run()
    except Exception as e:
        st.error(f"Error: {str(e)}")