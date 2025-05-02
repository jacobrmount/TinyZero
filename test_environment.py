#!/usr/bin/env python3
"""
Environment verification script for Remedy Project.
This script tests the basic components of the development environment.
"""

import sys
import platform
import importlib.util
from typing import Dict, Any


def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    print(f"Python version: {sys.version}")
    major, minor, *_ = sys.version_info
    return major == 3 and minor >= 9


def check_package_availability(package: str) -> bool:
    """Check if a package is available and print its version if found."""
    spec = importlib.util.find_spec(package)
    if spec is not None:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print(f"{package} version: {version}")
            return True
        except ImportError:
            print(f"{package} found but failed to import")
            return False
    else:
        print(f"{package} not found")
        return False


def check_torch() -> Dict[str, Any]:
    """Check PyTorch installation and CUDA availability."""
    results = {}
    
    if check_package_availability("torch"):
        import torch
        
        results["torch_version"] = torch.__version__
        results["cuda_available"] = torch.cuda.is_available()
        
        if results["cuda_available"]:
            results["cuda_version"] = torch.version.cuda
            results["cuda_device_count"] = torch.cuda.device_count()
            results["cuda_device_name"] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "N/A"
        
        # Test basic tensor operations
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tensor = torch.randn(3, 3).to(device)
        results["tensor_device"] = str(tensor.device)
        
        # Test matrix multiplication
        result_tensor = tensor @ tensor
        results["matrix_multiply_successful"] = (result_tensor.shape == (3, 3))
    
    return results


def main():
    """Run environment checks and print results."""
    print("\n=== Remedy Environment Check ===\n")
    
    # System information
    print("=== System Information ===")
    print(f"Operating System: {platform.platform()}")
    check_python_version()
    print("")
    
    # Core dependencies
    print("=== Core Dependencies ===")
    core_packages = ["torch", "numpy", "matplotlib", "ray", "transformers", "wandb"]
    available_packages = [pkg for pkg in core_packages if check_package_availability(pkg)]
    print(f"\n{len(available_packages)}/{len(core_packages)} core packages available.\n")
    
    # PyTorch specific checks
    print("=== PyTorch Details ===")
    torch_results = check_torch()
    for key, value in torch_results.items():
        print(f"{key}: {value}")
    print("")
    
    # Overall assessment
    print("=== Environment Assessment ===")
    
    python_ok = check_python_version()
    torch_ok = "torch_version" in torch_results and torch_results.get("matrix_multiply_successful", False)
    
    if python_ok and torch_ok and len(available_packages) >= 3:
        print("✅ Basic environment is functional for development.")
        if not torch_results.get("cuda_available", False):
            print("⚠️  Warning: CUDA is not available. GPU acceleration will not be used.")
    else:
        print("❌ Environment setup is incomplete. Please check the requirements.")
    
    print("\nRefer to docs/ENV_SETUP.md for complete installation instructions.")


if __name__ == "__main__":
    main() 