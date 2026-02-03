@echo off
REM setup_cuda.bat - CUDA Environment Setup for Project Luna

echo =====================================
echo   Project Luna - CUDA Setup
echo =====================================
echo.

REM Set CUDA paths
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1"
set "CUDA_PATH_V13_1=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1"
set "CUDACXX=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\nvcc.exe"

REM Add to PATH
set "PATH=%CUDA_PATH%\bin;%CUDA_PATH%\libnvvp;%PATH%"

REM Set CMAKE args
set "CMAKE_ARGS=-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=89"

echo ✓ CUDA environment configured
echo ✓ CMAKE_ARGS set for RTX 5060 Ti
echo.

REM Verify
echo Verifying CUDA...
nvcc --version
echo.

echo ✓ Ready to build with CUDA support!
echo.
echo Next: pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir
echo.