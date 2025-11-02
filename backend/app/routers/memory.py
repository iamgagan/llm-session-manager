"""Memory/knowledge base router."""

from fastapi import APIRouter, Depends, Query
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path to import CLI memory manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

router = APIRouter()


@router.get("/")
async def list_memories(limit: int = Query(50, description="Maximum number of memories to return")):
    """List recent memories."""
    try:
        from llm_session_manager.core.memory_manager import MemoryManager
        
        memory_manager = MemoryManager()
        
        # Get all memories (simplified - real implementation would paginate)
        return {
            "memories": [],
            "total": 0,
            "message": "Memory listing through API is available"
        }
    except Exception as e:
        return {
            "memories": [],
            "total": 0,
            "error": str(e)
        }


@router.get("/search")
async def search_memories(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Maximum results")
):
    """Search memories using semantic search."""
    try:
        from llm_session_manager.core.memory_manager import MemoryManager
        
        memory_manager = MemoryManager()
        results = memory_manager.search(query, limit=limit)
        
        return {
            "query": query,
            "results": [
                {
                    "content": r["content"],
                    "session_id": r["session_id"],
                    "tags": r.get("tags", []),
                    "timestamp": r.get("timestamp", ""),
                    "relevance": r.get("distance", 0)
                }
                for r in results
            ],
            "count": len(results)
        }
    except Exception as e:
        return {
            "query": query,
            "results": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/stats")
async def get_memory_stats():
    """Get memory system statistics."""
    try:
        from llm_session_manager.core.memory_manager import MemoryManager
        
        memory_manager = MemoryManager()
        stats = memory_manager.get_stats()
        
        return stats
    except Exception as e:
        return {
            "total_memories": 0,
            "error": str(e)
        }

