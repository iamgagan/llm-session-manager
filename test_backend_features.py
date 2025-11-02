#!/usr/bin/env python3
"""Backend API and WebSocket testing suite."""

import requests
import json
import sys
import time
from typing import Dict, List, Tuple
from datetime import datetime

class BackendTester:
    """Test backend API and WebSocket features."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
        
    def test_api(self, name: str, endpoint: str, method="GET", data=None) -> bool:
        """Test an API endpoint."""
        print(f"\n🧪 Testing: {name}")
        print(f"   Endpoint: {method} {endpoint}")
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=5)
            elif method == "DELETE":
                response = requests.delete(url, timeout=5)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code < 400
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} ({response.status_code})")
            
            self.results.append({
                "feature": name,
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "status": "PASS" if success else "FAIL",
                "response_preview": str(response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text)[:200],
                "timestamp": datetime.now().isoformat()
            })
            
            return success
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ FAIL - Server not running")
            self.results.append({
                "feature": name,
                "endpoint": endpoint,
                "status": "FAIL",
                "error": "Connection refused - server not running",
                "timestamp": datetime.now().isoformat()
            })
            return False
        except Exception as e:
            print(f"   ❌ FAIL - {str(e)}")
            self.results.append({
                "feature": name,
                "endpoint": endpoint,
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def check_server(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def test_rest_api(self):
        """Test REST API endpoints."""
        print("\n" + "="*60)
        print("🌐 TESTING REST API")
        print("="*60)
        
        if not self.check_server():
            print("⚠️  Backend server not running. Start with: cd backend && poetry run uvicorn app.main:app")
            print("   Skipping API tests...")
            return
        
        # Test: Health check
        self.test_api("Health Check", "/health")
        
        # Test: List sessions
        self.test_api("List Sessions", "/api/sessions/")
        
        # Test: Get session stats
        self.test_api("Session Stats", "/api/sessions/stats")
        
        # Test: Get projects
        self.test_api("List Projects", "/api/projects/")
        
        # Test: Get memories
        self.test_api("List Memories", "/api/memory/")
        
        # Test: Search memories
        self.test_api("Search Memories", "/api/memory/search?query=test")
        
        # Test: Get recommendations
        self.test_api("Get Recommendations", "/api/insights/recommendations")
    
    def test_websocket_availability(self):
        """Test WebSocket endpoint availability."""
        print("\n" + "="*60)
        print("🔌 TESTING WEBSOCKET")
        print("="*60)
        
        if not self.check_server():
            print("⚠️  Backend server not running. Skipping WebSocket tests...")
            return
        
        try:
            import websocket
            print("✅ websocket-client library available")
            
            # Test WebSocket connection
            print("\n🧪 Testing: WebSocket Connection")
            ws_url = self.base_url.replace('http', 'ws') + '/ws/test-session'
            print(f"   URL: {ws_url}")
            
            ws = websocket.create_connection(ws_url, timeout=5)
            print("   ✅ PASS - Connected")
            
            # Send a test message
            test_msg = json.dumps({"type": "ping", "data": "test"})
            ws.send(test_msg)
            print("   ✅ PASS - Message sent")
            
            # Try to receive (with timeout)
            ws.settimeout(2)
            try:
                response = ws.recv()
                print(f"   ✅ PASS - Received: {response[:50]}")
            except:
                print("   ⚠️  No response (expected for test)")
            
            ws.close()
            
            self.results.append({
                "feature": "WebSocket Connection",
                "endpoint": "/ws/{session_id}",
                "status": "PASS",
                "timestamp": datetime.now().isoformat()
            })
            
        except ImportError:
            print("⚠️  websocket-client not installed. Install with: pip install websocket-client")
            self.results.append({
                "feature": "WebSocket Test",
                "status": "SKIP",
                "reason": "websocket-client not installed",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"   ❌ FAIL - {str(e)}")
            self.results.append({
                "feature": "WebSocket Connection",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "="*60)
        print("📊 BACKEND TEST REPORT")
        print("="*60)
        
        if not self.results:
            print("No tests run")
            return False
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('status') == 'PASS')
        failed = sum(1 for r in self.results if r.get('status') == 'FAIL')
        skipped = sum(1 for r in self.results if r.get('status') == 'SKIP')
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped: {skipped}")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if r.get('status') == 'FAIL':
                    print(f"   - {r['feature']}")
                    if 'error' in r:
                        print(f"     Error: {r['error'][:100]}")
        
        # Save report
        with open("test_results_backend.json", 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped
                },
                "tests": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: test_results_backend.json")
        
        return failed == 0


def main():
    """Run backend tests."""
    print("🚀 LLM Session Manager - Backend Testing")
    print("="*60)
    
    tester = BackendTester()
    tester.test_rest_api()
    tester.test_websocket_availability()
    tester.generate_report()


if __name__ == "__main__":
    main()

