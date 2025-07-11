from .graphiti import Graphiti, AddEpisodeResults
from .nodes import EntityNode, EpisodicNode
from .edges import EntityEdge, EpisodicEdge

# Import legal extensions
from .legal_entities import LEGAL_ENTITY_TYPES, get_legal_entity_type_descriptions
from .graphiti_web_extension import extend_graphiti_with_web_capabilities
from .synthetic_legal_graph import extend_graphiti_with_synthesis

__all__ = [
    'Graphiti',
    'AddEpisodeResults',
    'EntityNode',
    'EpisodicNode', 
    'EntityEdge',
    'EpisodicEdge',
    'LEGAL_ENTITY_TYPES',
    'get_legal_entity_type_descriptions',
    'extend_graphiti_with_web_capabilities',
    'extend_graphiti_with_synthesis'
]
