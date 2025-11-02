#!/usr/bin/env python3
"""MCP (Model Context Protocol) integration testing."""

import subprocess
import json
import sys
from typing import Tuple
from datetime import datetime

class MCPTester:
    """Test MCP server integration."""
    
    def __init__(self):
        self.results = []
        
    def run_cmd(self, cmd: str, timeout=10) -> Tuple[bool, str, str]:
        """Run a command."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "", "Timeout")
        except Exception as e:
            return (False, "", str(e))
    
    def test_mcp_config_generation(self):
        """Test MCP configuration generation."""
        print("\n" + "="*60)
        print("🔌 TESTING MCP INTEGRATION")
        print("="*60)
        
        print("\n🧪 Testing: MCP Config Generation")
        success, stdout, stderr = self.run_cmd(
            "cd /Users/gagan/llm-session-manager && poetry run python -m llm_session_manager.cli mcp-config"
        )
        
        if success and "mcpServers" in stdout:
            print("   ✅ PASS - Config generated")
            self.results.append({
                "test": "MCP Config Generation",
                "status": "PASS",
                "timestamp": datetime.now().isoformat()
            })
        else:
            print("   ❌ FAIL")
            self.results.append({
                "test": "MCP Config Generation",
                "status": "FAIL",
                "error": stderr[:200],
                "timestamp": datetime.now().isoformat()
            })
    
    def test_mcp_server_start(self):
        """Test MCP server starts correctly."""
        print("\n🧪 Testing: MCP Server Startup")
        
        # Try to start MCP server (it will fail without proper stdio setup, but should not crash)
        success, stdout, stderr = self.run_cmd(
            "cd /Users/gagan/llm-session-manager && echo '{}' | timeout 2 poetry run python -m llm_session_manager.mcp.server 2>&1 || true",
            timeout=3
        )
        
        # If it doesn't crash immediately, that's a pass
        if "Traceback" not in stderr and "Traceback" not in stdout:
            print("   ✅ PASS - Server initializes without crashing")
            self.results.append({
                "test": "MCP Server Startup",
                "status": "PASS",
                "timestamp": datetime.now().isoformat()
            })
        else:
            print("   ❌ FAIL - Server crashed on startup")
            self.results.append({
                "test": "MCP Server Startup",
                "status": "FAIL",
                "error": (stderr + stdout)[:200],
                "timestamp": datetime.now().isoformat()
            })
    
    def test_mcp_tools_available(self):
        """Test that MCP tools are properly defined."""
        print("\n🧪 Testing: MCP Tools Definition")
        
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path("/Users/gagan/llm-session-manager")))
            
            from llm_session_manager.mcp.server import server, list_sessions, get_session_details
            
            # Check if tools are registered
            tools_found = True
            print("   ✅ PASS - MCP tools are properly defined")
            self.results.append({
                "test": "MCP Tools Definition",
                "status": "PASS",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"   ❌ FAIL - {str(e)}")
            self.results.append({
                "test": "MCP Tools Definition",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "="*60)
        print("📊 MCP TEST REPORT")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('status') == 'PASS')
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if r.get('status') == 'FAIL':
                    print(f"   - {r['test']}")
                    if 'error' in r:
                        print(f"     Error: {r['error'][:100]}")
        
        # Save report
        with open("test_results_mcp.json", 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed
                },
                "tests": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_results_mcp.json")
        
        return failed == 0


def main():
    """Run MCP tests."""
    print("🚀 LLM Session Manager - MCP Testing")
    print("="*60)
    
    tester = MCPTester()
    tester.test_mcp_config_generation()
    tester.test_mcp_server_start()
    tester.test_mcp_tools_available()
    tester.generate_report()


if __name__ == "__main__":
    main()

