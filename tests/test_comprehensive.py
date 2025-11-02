#!/usr/bin/env python3
"""
Comprehensive automated test suite for LLM Session Manager.

This test suite can be run with:
    python3 tests/test_comprehensive.py

Or with pytest:
    pytest tests/test_comprehensive.py -v
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Tuple, List
import unittest


class TestCLICommands(unittest.TestCase):
    """Test CLI command functionality."""
    
    @staticmethod
    def run_cli(args: str) -> Tuple[int, str, str]:
        """Run CLI command and return (returncode, stdout, stderr)."""
        cmd = f"poetry run python -m llm_session_manager.cli {args}"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        return result.returncode, result.stdout, result.stderr
    
    def test_info_command(self):
        """Test info command displays version."""
        returncode, stdout, stderr = self.run_cli("info")
        self.assertEqual(returncode, 0)
        self.assertIn("LLM Session Manager", stdout)
        self.assertIn("Version", stdout)
    
    def test_list_sessions_json(self):
        """Test list command with JSON output."""
        returncode, stdout, stderr = self.run_cli("list --format json")
        self.assertEqual(returncode, 0)
        # Should output valid JSON (array)
        self.assertTrue(stdout.strip().startswith("[") or stdout.strip().startswith("{"))
    
    def test_list_projects(self):
        """Test list-projects command."""
        returncode, stdout, stderr = self.run_cli("list-projects")
        self.assertEqual(returncode, 0)
        self.assertTrue("Projects" in stdout or "No projects" in stdout)
    
    def test_memory_stats(self):
        """Test memory-stats command."""
        returncode, stdout, stderr = self.run_cli("memory-stats")
        self.assertEqual(returncode, 0)
        self.assertIn("Memory", stdout)
    
    def test_mcp_config(self):
        """Test MCP config generation."""
        returncode, stdout, stderr = self.run_cli("mcp-config")
        self.assertEqual(returncode, 0)
        self.assertIn("mcpServers", stdout)
    
    def test_show_config(self):
        """Test show-config command."""
        returncode, stdout, stderr = self.run_cli("show-config")
        self.assertEqual(returncode, 0)
        self.assertIn("Token Limits", stdout)


class TestDatabaseOperations(unittest.TestCase):
    """Test database functionality."""
    
    def test_database_initialization(self):
        """Test database can be initialized."""
        try:
            from llm_session_manager.storage.database import Database
            db = Database()
            self.assertIsNotNone(db)
        except Exception as e:
            self.fail(f"Database initialization failed: {e}")
    
    def test_get_all_sessions(self):
        """Test retrieving all sessions."""
        from llm_session_manager.storage.database import Database
        db = Database()
        sessions = db.get_all_sessions()
        self.assertIsInstance(sessions, list)
    
    def test_get_all_projects(self):
        """Test retrieving all projects."""
        from llm_session_manager.storage.database import Database
        db = Database()
        projects = db.get_all_projects()
        self.assertIsInstance(projects, list)


class TestSessionDiscovery(unittest.TestCase):
    """Test session discovery functionality."""
    
    def test_session_discovery_initialization(self):
        """Test SessionDiscovery can be initialized."""
        try:
            from llm_session_manager.core.session_discovery import SessionDiscovery
            from llm_session_manager.storage.database import Database
            db = Database()
            discovery = SessionDiscovery(db)
            self.assertIsNotNone(discovery)
        except Exception as e:
            self.fail(f"SessionDiscovery initialization failed: {e}")
    
    def test_detect_sessions(self):
        """Test session detection."""
        from llm_session_manager.core.session_discovery import SessionDiscovery
        from llm_session_manager.storage.database import Database
        db = Database()
        discovery = SessionDiscovery(db)
        sessions = discovery.discover_sessions()
        self.assertIsInstance(sessions, list)


class TestMemoryManager(unittest.TestCase):
    """Test memory manager functionality."""
    
    def test_memory_manager_initialization(self):
        """Test MemoryManager can be initialized."""
        try:
            from llm_session_manager.core.memory_manager import MemoryManager
            memory_manager = MemoryManager()
            self.assertIsNotNone(memory_manager)
        except Exception as e:
            self.fail(f"MemoryManager initialization failed: {e}")
    
    def test_memory_stats(self):
        """Test getting memory statistics."""
        from llm_session_manager.core.memory_manager import MemoryManager
        memory_manager = MemoryManager()
        stats = memory_manager.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_memories", stats)


class TestHealthMonitor(unittest.TestCase):
    """Test health monitoring functionality."""
    
    def test_health_monitor_initialization(self):
        """Test HealthMonitor can be initialized."""
        try:
            from llm_session_manager.core.health_monitor import HealthMonitor
            from llm_session_manager.storage.database import Database
            db = Database()
            health_monitor = HealthMonitor(db)
            self.assertIsNotNone(health_monitor)
        except Exception as e:
            self.fail(f"HealthMonitor initialization failed: {e}")


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine."""
    
    def test_recommendation_engine_initialization(self):
        """Test RecommendationEngine can be initialized."""
        try:
            from llm_session_manager.services.recommendation_engine import RecommendationEngine
            from llm_session_manager.storage.database import Database
            from llm_session_manager.core.health_monitor import HealthMonitor
            db = Database()
            health_monitor = HealthMonitor(db)
            engine = RecommendationEngine(db, health_monitor)
            self.assertIsNotNone(engine)
        except Exception as e:
            self.fail(f"RecommendationEngine initialization failed: {e}")


class TestExportFunctionality(unittest.TestCase):
    """Test export functionality."""
    
    def test_export_json(self):
        """Test JSON export."""
        returncode, stdout, stderr = TestCLICommands.run_cli(
            "list --format json"
        )
        self.assertEqual(returncode, 0)
        
        # Try to parse as JSON
        try:
            # Filter out non-JSON lines
            lines = [l for l in stdout.split('\n') if l.strip() and not l.startswith('Discovering')]
            json_str = '\n'.join(lines)
            if json_str:
                json.loads(json_str)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON output: {e}")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCLICommands))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionDiscovery))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryManager))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestExportFunctionality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())

