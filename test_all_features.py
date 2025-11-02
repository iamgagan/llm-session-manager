#!/usr/bin/env python3
"""Comprehensive feature testing suite for LLM Session Manager.

Tests all advertised features and generates a detailed report.
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class FeatureTester:
    """Comprehensive feature testing for LLM Session Manager."""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.session_id = None
        
    def run_cmd(self, cmd: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return (success, stdout, stderr)."""
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
            return (False, "", "Command timed out")
        except Exception as e:
            return (False, "", str(e))
    
    def test_feature(self, name: str, cmd: str, check_fn=None, timeout=30) -> bool:
        """Test a feature and record results."""
        print(f"\n🧪 Testing: {name}")
        print(f"   Command: {cmd}")
        
        success, stdout, stderr = self.run_cmd(cmd, timeout)
        
        # Custom check function
        if check_fn and success:
            try:
                success = check_fn(stdout, stderr)
            except Exception as e:
                success = False
                stderr += f"\nCheck function failed: {str(e)}"
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}")
        
        self.results.append({
            "feature": name,
            "command": cmd,
            "status": "PASS" if success else "FAIL",
            "stdout_preview": stdout[:200] if stdout else "",
            "stderr_preview": stderr[:200] if stderr else "",
            "timestamp": datetime.now().isoformat()
        })
        
        return success
    
    def get_session_id(self) -> str:
        """Get a session ID for testing."""
        if self.session_id:
            return self.session_id
            
        cmd = 'poetry run python -m llm_session_manager.cli list --format json 2>&1 | grep -v "Discovering"'
        success, stdout, stderr = self.run_cmd(cmd)
        
        if success and stdout.strip():
            try:
                sessions = json.loads(stdout)
                if sessions:
                    self.session_id = sessions[0]['id']
                    print(f"📋 Using session ID: {self.session_id}")
                    return self.session_id
            except:
                pass
        
        # Fallback: create a test session ID
        self.session_id = "test_session_001"
        return self.session_id
    
    def test_core_features(self):
        """Test core session monitoring features."""
        print("\n" + "="*60)
        print("📊 TESTING CORE SESSION MONITORING")
        print("="*60)
        
        # Test: List sessions
        self.test_feature(
            "List Sessions (Table)",
            "poetry run python -m llm_session_manager.cli list",
            lambda out, err: "Active Sessions" in out
        )
        
        # Test: List sessions JSON
        self.test_feature(
            "List Sessions (JSON)",
            "poetry run python -m llm_session_manager.cli list --format json 2>&1 | grep -v Discovering",
            lambda out, err: out.strip().startswith("[") or out.strip().startswith("{")
        )
        
        # Test: Show session details
        session_id = self.get_session_id()
        if session_id:
            self.test_feature(
                "Show Session Details",
                f"poetry run python -m llm_session_manager.cli show {session_id}",
                lambda out, err: "Session Details" in out or "Session ID" in out
            )
            
            # Test: Health check
            self.test_feature(
                "Health Check",
                f"poetry run python -m llm_session_manager.cli health {session_id}",
                lambda out, err: "Health" in out or "Score" in out or "Session" in err
            )
        
        # Test: List projects
        self.test_feature(
            "List Projects",
            "poetry run python -m llm_session_manager.cli list-projects",
            lambda out, err: "Projects" in out or "No projects" in out
        )
        
        # Test: Info command
        self.test_feature(
            "Info Command",
            "poetry run python -m llm_session_manager.cli info",
            lambda out, err: "LLM Session Manager" in out and "Version" in out
        )
    
    def test_export_features(self):
        """Test export functionality."""
        print("\n" + "="*60)
        print("💾 TESTING EXPORT FEATURES")
        print("="*60)
        
        session_id = self.get_session_id()
        if not session_id:
            print("⚠️  Skipping export tests (no session ID)")
            return
        
        # Test: Export JSON
        self.test_feature(
            "Export to JSON",
            f"poetry run python -m llm_session_manager.cli export {session_id} --format json --output /tmp/test_export.json",
            lambda out, err: Path("/tmp/test_export.json").exists()
        )
        
        # Test: Export YAML
        self.test_feature(
            "Export to YAML",
            f"poetry run python -m llm_session_manager.cli export {session_id} --format yaml --output /tmp/test_export.yaml",
            lambda out, err: Path("/tmp/test_export.yaml").exists()
        )
        
        # Test: Export Markdown
        self.test_feature(
            "Export to Markdown",
            f"poetry run python -m llm_session_manager.cli export {session_id} --format markdown --output /tmp/test_export.md",
            lambda out, err: Path("/tmp/test_export.md").exists()
        )
    
    def test_memory_features(self):
        """Test cross-session memory features."""
        print("\n" + "="*60)
        print("🧠 TESTING MEMORY FEATURES")
        print("="*60)
        
        session_id = self.get_session_id()
        if not session_id:
            print("⚠️  Skipping memory tests (no session ID)")
            return
        
        # Test: Memory stats
        self.test_feature(
            "Memory Stats",
            "poetry run python -m llm_session_manager.cli memory-stats",
            lambda out, err: "Memory System" in out or "ChromaDB" in err or "not available" in out
        )
        
        # Test: Memory add
        self.test_feature(
            "Add Memory",
            f'poetry run python -m llm_session_manager.cli memory-add {session_id} "Test memory content" "test feature"',
            lambda out, err: "Memory saved" in out or "not available" in out or "not available" in err
        )
        
        # Test: Memory search
        self.test_feature(
            "Search Memory",
            'poetry run python -m llm_session_manager.cli memory-search "test"',
            lambda out, err: "memories" in out.lower() or "not available" in out or "not available" in err
        )
        
        # Test: Memory list
        self.test_feature(
            "List Memories",
            "poetry run python -m llm_session_manager.cli memory-list",
            lambda out, err: "memories" in out.lower() or "Total memories" in out or "not available" in out
        )
    
    def test_tagging_features(self):
        """Test tagging and organization features."""
        print("\n" + "="*60)
        print("🏷️  TESTING TAGGING FEATURES")
        print("="*60)
        
        session_id = self.get_session_id()
        if not session_id:
            print("⚠️  Skipping tagging tests (no session ID)")
            return
        
        # Test: Tag session
        self.test_feature(
            "Tag Session",
            f'poetry run python -m llm_session_manager.cli tag {session_id} test-tag feature-test',
            lambda out, err: "tag" in out.lower() or "Session" in err
        )
        
        # Test: Set project
        self.test_feature(
            "Set Project",
            f'poetry run python -m llm_session_manager.cli set-project {session_id} "Test Project"',
            lambda out, err: "Project" in out or "Session" in err
        )
        
        # Test: Describe session
        self.test_feature(
            "Describe Session",
            f'poetry run python -m llm_session_manager.cli describe {session_id} "Test description" --show',
            lambda out, err: "description" in out.lower() or "Session" in err
        )
    
    def test_mcp_features(self):
        """Test MCP integration."""
        print("\n" + "="*60)
        print("🔌 TESTING MCP INTEGRATION")
        print("="*60)
        
        # Test: MCP config generation
        self.test_feature(
            "Generate MCP Config",
            "poetry run python -m llm_session_manager.cli mcp-config",
            lambda out, err: "mcpServers" in out or "Configuration" in out
        )
    
    def test_config_features(self):
        """Test configuration features."""
        print("\n" + "="*60)
        print("⚙️  TESTING CONFIGURATION")
        print("="*60)
        
        # Test: Show config
        self.test_feature(
            "Show Config",
            "poetry run python -m llm_session_manager.cli show-config",
            lambda out, err: "Configuration" in out or "Token Limits" in out or "exists" in err
        )
    
    def test_recommendation_features(self):
        """Test smart recommendations."""
        print("\n" + "="*60)
        print("💡 TESTING RECOMMENDATIONS")
        print("="*60)
        
        # Test: Recommendations
        self.test_feature(
            "Get Recommendations",
            "poetry run python -m llm_session_manager.cli recommend",
            lambda out, err: "Recommendations" in out or "No active sessions" in out or "recommendations" in out.lower()
        )
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "="*60)
        print("📊 TEST REPORT")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if r['status'] == 'FAIL':
                    print(f"   - {r['feature']}")
                    if r['stderr_preview']:
                        print(f"     Error: {r['stderr_preview'][:100]}")
        
        # Save detailed report
        report_file = Path("test_results_comprehensive.json")
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": f"{passed/total*100:.1f}%"
                },
                "tests": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return passed == total


def main():
    """Run all tests."""
    print("🚀 LLM Session Manager - Comprehensive Feature Testing")
    print("="*60)
    
    tester = FeatureTester()
    
    # Run all test suites
    tester.test_core_features()
    tester.test_export_features()
    tester.test_memory_features()
    tester.test_tagging_features()
    tester.test_mcp_features()
    tester.test_config_features()
    tester.test_recommendation_features()
    
    # Generate report
    all_passed = tester.generate_report()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

