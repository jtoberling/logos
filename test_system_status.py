#!/usr/bin/env python3
"""
Logos System Status Test - Quick Verification Script

This script provides a fast way to verify that the Logos MCP system
is working correctly. Run this anytime to check system health.

Usage: python test_system_status.py
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_unit_tests():
    """Check if unit tests pass."""
    print("🧪 Checking Unit Tests...")
    success, stdout, stderr = run_command("cd /usr/src/logos && python -m pytest test/unit/ -q --tb=no")
    if success:
        # Extract test count from output like "239 passed in 4.76s"
        lines = stdout.split('\n')
        for line in lines:
            if 'passed' in line:
                print(f"✅ Unit Tests: {line.strip()}")
                return True
    print(f"❌ Unit Tests failed: {stderr[:100]}...")
    return False

def check_mcp_local():
    """Check MCP functionality locally."""
    print("🤖 Checking MCP Integration...")
    test_script = '''
import asyncio
import sys
sys.path.insert(0, "src")

async def quick_test():
    try:
        from fastmcp import Client
        async with Client("http://localhost:6335/") as client:
            tools = await client.list_tools()
            if len(tools) >= 11:
                result = await client.call_tool("get_constitution", {})
                return f"✅ MCP: {len(tools)} tools, constitution working"
            else:
                return f"⚠️ MCP: Only {len(tools)} tools found"
    except Exception as e:
        return f"❌ MCP: {str(e)[:50]}..."

result = asyncio.run(quick_test())
print(result)
'''
    success, stdout, stderr = run_command(f"cd /usr/src/logos && python -c '{test_script}'")
    if success:
        print(stdout)
        return "tools" in stdout.lower()
    else:
        print(f"❌ MCP check failed: {stderr[:100]}...")
        return False

def check_docker_services():
    """Check if Docker services are running."""
    print("🐳 Checking Docker Services...")
    success, stdout, stderr = run_command("docker ps --filter name=logos --format 'table {{.Names}}\\t{{.Status}}'")
    if success and "logos" in stdout.lower():
        lines = stdout.strip().split('\n')
        if len(lines) > 1:  # Header + at least one service
            print("✅ Docker Services Running:")
            for line in lines[1:]:
                print(f"   {line}")
            return True
    print("❌ Docker services not running")
    return False

def check_code_quality():
    """Check basic code quality."""
    print("🔍 Checking Code Quality...")
    # Check if main files exist and are readable
    files_to_check = [
        "src/main.py",
        "src/tools/query_tools.py",
        "requirements.txt",
        "Dockerfile"
    ]

    all_exist = True
    for file_path in files_to_check:
        if not os.path.exists(f"/usr/src/logos/{file_path}"):
            print(f"❌ Missing: {file_path}")
            all_exist = False
        else:
            print(f"✅ Found: {file_path}")

    return all_exist

def main():
    """Run all system checks."""
    print("🚀 LOGOS SYSTEM STATUS VERIFICATION")
    print("=" * 50)

    checks = [
        ("Code Quality", check_code_quality),
        ("Unit Tests", check_unit_tests),
        ("MCP Integration", check_mcp_local),
        ("Docker Services", check_docker_services),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}: Exception - {e}")
            results.append((check_name, False))
        print()

    # Summary
    print("📊 SUMMARY:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print("25")

        if success:
            passed += 1

    print("-" * 50)
    print(f"Overall Score: {passed}/{total}")

    if passed == total:
        print("🎉 SYSTEM STATUS: EXCELLENT - All checks passed!")
        print("✅ Logos MCP system is fully operational")
    elif passed >= total * 0.75:
        print("✅ SYSTEM STATUS: GOOD - Most functionality working")
    elif passed >= total * 0.5:
        print("⚠️ SYSTEM STATUS: FAIR - Some issues detected")
    else:
        print("❌ SYSTEM STATUS: POOR - Significant issues")

    print()
    print("💡 Next Steps:")
    if not any(r[1] for r in results if "MCP" in r[0]):
        print("   - Start MCP server: python -m src.main")
    if not any(r[1] for r in results if "Docker" in r[0]):
        print("   - Start Docker: docker-compose -f deploy/docker/docker-compose.portainer.yml up -d")
    print("   - Run full tests: pytest test/unit/ -v")

if __name__ == "__main__":
    main()