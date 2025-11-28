@echo off
echo ========================================
echo Fixing TensorFlow and Protobuf Issues
echo ========================================
echo.

echo Step 1: Uninstalling old protobuf...
python -m pip uninstall protobuf -y

echo.
echo Step 2: Installing compatible protobuf version...
python -m pip install protobuf==4.23.4

echo.
echo Step 3: Upgrading TensorFlow...
python -m pip install --upgrade tensorflow==2.15.0

echo.
echo Step 4: Installing other dependencies...
python -m pip install flask-cors pillow opencv-python pandas joblib google-generativeai requests

echo.
echo ========================================
echo Fix completed! Now starting the app...
echo ========================================
echo.

python app.py

pause
