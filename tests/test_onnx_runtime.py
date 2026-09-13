import torch
import onnxruntime as ort


print("PyTorch:", torch.__version__)
print("PyTorch CUDA:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

print("\nONNX Runtime:", ort.__version__)
print("Providers:")
print(ort.get_available_providers())

print("\nONNX Runtime debug information:")
ort.print_debug_info()