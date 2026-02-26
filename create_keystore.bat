@echo off
cd C:\Users\harpr\examinerai
if exist examinerai.jks del examinerai.jks
keytool -genkeypair -v -keystore examinerai.jks -keyalg RSA -keysize 2048 -validity 10000 -alias examinerai -storepass examinerai -keypass examinerai -dname "CN=ExaminerAI,O=ExaminerAI,C=US"
echo.
echo Verifying keystore...
keytool -list -keystore examinerai.jks -storepass examinerai
pause
