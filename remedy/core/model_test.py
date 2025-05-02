"""
Smoke test utilities for Remedy model inference.
"""

import torch
from typing import Dict, Any


class ModelTest:
    """
    Utility class for testing model inference in the Remedy environment.
    """

    @staticmethod
    def run_smoke_test() -> Dict[str, Any]:
        """
        Run a basic smoke test to verify the environment is working properly.
        
        Returns:
            Dict[str, Any]: Results of the smoke test
        """
        results = {}
        
        # Check CUDA availability
        results["cuda_available"] = torch.cuda.is_available()
        if results["cuda_available"]:
            results["cuda_device_count"] = torch.cuda.device_count()
            results["cuda_device_name"] = torch.cuda.get_device_name(0)
        
        # Create a small tensor and move to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tensor = torch.randn(3, 3).to(device)
        results["tensor_device"] = str(tensor.device)
        
        # Test basic operation
        result_tensor = tensor @ tensor
        results["matrix_multiply_successful"] = (result_tensor.shape == (3, 3))
        
        # Check PyTorch version
        results["torch_version"] = torch.__version__
        
        print("Smoke test results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
        
        if all([
            results.get("matrix_multiply_successful", False),
            torch.__version__.startswith("2.4.0")
        ]):
            print("\nSuccess: Environment is properly configured!")
        else:
            print("\nWarning: Environment may not be properly configured.")
        
        return results

if __name__ == "__main__":
    ModelTest.run_smoke_test() 