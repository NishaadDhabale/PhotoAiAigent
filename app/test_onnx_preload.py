import onnxruntime as ort


print("ONNX Runtime:", ort.__version__)

print("\nPreloading CUDA/cuDNN DLLs...")
ort.preload_dlls()

print("\nLoaded CUDA/cuDNN DLL information:")
ort.print_debug_info()

print("\nExecution providers:")
print(ort.get_available_providers())