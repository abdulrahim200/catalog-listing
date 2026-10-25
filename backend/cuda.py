import paddle

print("PaddlePaddle version:", paddle.__version__)
print("Current device:", paddle.device.get_device())
print("CUDA available:", paddle.device.is_compiled_with_cuda())