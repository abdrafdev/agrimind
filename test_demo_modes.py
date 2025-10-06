#!/usr/bin/env python3
"""
AgriMind Demo Mode Verification Script
Tests all demo modes and verifies data source handling
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_demo_mode(mode):
    """Run demo in specified mode and capture output"""
    print(f"\n🧪 Testing {mode.upper()} mode...")
    print("=" * 50)
    
    try:
        # Run the demo with timeout
        import os
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding
        
        result = subprocess.run(
            [sys.executable, "agrimind_demo.py", mode],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout for full demo
            cwd=os.getcwd(),
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace problematic characters
        )
        
        print(f"Exit code: {result.returncode}")
        
        # Check for key indicators in output
        output = result.stdout + result.stderr
        
        # Debug output for failure analysis
        if result.returncode != 0:
            print(f"\n❌ Demo failed with exit code {result.returncode}")
            error_lines = [line for line in output.split('\n')[-10:] if line.strip()]
            print(f"Last few lines of output:")
            for line in error_lines:
                print(f"  {line}")
        
        # Only test patterns if the demo completed successfully
        success_indicators = ["Demo completed!", "✅ Demo completed!"]
        demo_completed = any(indicator in output for indicator in success_indicators)
        
        if not demo_completed and result.returncode == 0:
            print(f"\n⚠️  Demo may not have completed fully")
        
        # Mode-specific checks
        if mode == "hybrid":
            checks = [
                ("Dataset loading", "📊 Dataset Status:" in output),
                ("API keys", "🔑 API keys loaded:" in output),
                ("Data source metadata", "DATA_SOURCE_METADATA:" in output),
                ("Agent initialization", "✅ Initialized" in output and "agents" in output),
                ("Demo cycle", "Starting AgriMind Collaboration Demo Cycle" in output)
            ]
        elif mode == "offline":
            checks = [
                ("Offline mode", "OFFLINE MODE: API connectivity disabled" in output or "🔒 Offline mode:" in output),
                ("Dataset only", "datasets only" in output or "using datasets only" in output),
                ("No API calls", "API connectivity disabled" in output),
                ("Data source metadata", "DATA_SOURCE_METADATA:" in output),
                ("Demo cycle", "Starting AgriMind Collaboration Demo Cycle" in output)
            ]
        elif mode == "mock":
            checks = [
                ("Mock mode", "🎭 MOCK MODE:" in output),
                ("Synthetic data", "Using synthetic data only" in output),
                ("Data source metadata", "DATA_SOURCE_METADATA:" in output or "mock" in output.lower()),
                ("Demo cycle", "Starting AgriMind Collaboration Demo Cycle" in output)
            ]
        
        # Print results
        passed = 0
        total = len(checks)
        
        for check_name, passed_check in checks:
            status = "✅ PASS" if passed_check else "❌ FAIL"
            print(f"  {check_name}: {status}")
            if passed_check:
                passed += 1
        
        print(f"\n📊 {mode.upper()} Mode: {passed}/{total} checks passed")
        
        # Show sample output lines with DATA_SOURCE_METADATA
        metadata_lines = [line for line in output.split('\n') if 'DATA_SOURCE_METADATA' in line]
        if metadata_lines:
            print(f"\n📋 Sample data source metadata from {mode} mode:")
            for line in metadata_lines[:3]:  # Show first 3 lines
                print(f"  {line.strip()}")
        
        return passed == total
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {mode.upper()} mode test timed out")
        return False
    except Exception as e:
        print(f"❌ {mode.upper()} mode test failed: {e}")
        return False

def verify_datasets():
    """Verify all required datasets exist"""
    print("\n🗂️  Verifying datasets...")
    print("=" * 50)
    
    required_datasets = [
        "datasets/farm_sensor_data_tehsil_with_date.json",
        "datasets/weather_data_tehsil.csv",
        "datasets/farm_resources.json",
        "datasets/market_prices.csv"
    ]
    
    all_exist = True
    for dataset in required_datasets:
        if Path(dataset).exists():
            size = Path(dataset).stat().st_size
            print(f"  ✅ {dataset} ({size:,} bytes)")
        else:
            print(f"  ❌ {dataset} (missing)")
            all_exist = False
    
    return all_exist

def verify_env_file():
    """Verify .env file configuration"""
    print("\n🔧 Verifying environment configuration...")
    print("=" * 50)
    
    if Path(".env").exists():
        print("  ✅ .env file exists")
        
        with open(".env", "r") as f:
            env_content = f.read()
        
        # Check for key configurations
        configs = [
            ("AGRIMIND_ENV", "AGRIMIND_ENV=" in env_content),
            ("LOG_LEVEL", "LOG_LEVEL=" in env_content)
        ]
        
        for config_name, found in configs:
            status = "✅" if found else "❌"
            print(f"  {status} {config_name} configuration")
    else:
        print("  ❌ .env file missing")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 AgriMind Demo Mode Verification")
    print("=" * 60)
    print("Testing all demo modes and data source handling...")
    
    # Verify prerequisites
    datasets_ok = verify_datasets()
    env_ok = verify_env_file()
    
    if not datasets_ok:
        print("\n⚠️  Some datasets are missing. Demo may use fallback data.")
    
    # Test all modes
    modes = ["hybrid", "offline", "mock"]
    results = {}
    
    for mode in modes:
        results[mode] = run_demo_mode(mode)
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n📊 FINAL RESULTS")
    print("=" * 60)
    
    passed_modes = sum(1 for passed in results.values() if passed)
    total_modes = len(modes)
    
    for mode, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {mode.upper()} mode: {status}")
    
    print(f"\n🎯 Overall: {passed_modes}/{total_modes} modes working correctly")
    
    if passed_modes == total_modes and datasets_ok:
        print("\n🎉 All tests passed! AgriMind is ready for demo.")
    else:
        print("\n⚠️  Some issues found. Check the output above.")
        
    print("\n💡 Usage commands:")
    print("  python agrimind_demo.py hybrid   # Dataset + API mode")
    print("  python agrimind_demo.py offline  # Dataset only mode")  
    print("  python agrimind_demo.py mock     # Mock data only mode")

if __name__ == "__main__":
    main()