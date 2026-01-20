@echo off
echo ========================================
echo    CreditSim - Actualizando Frontend
echo ========================================

cd /d "%~dp0\frontend"

echo [1/4] Building React app...
call npx react-scripts build
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo [2/4] Uploading to S3...
aws s3 sync build/ s3://credit-frontendbucket-g4gcrsfiwpbm/ --delete
if %errorlevel% neq 0 (
    echo ERROR: S3 upload failed
    pause
    exit /b 1
)

echo [3/4] Invalidating CloudFront...
aws cloudfront create-invalidation --distribution-id E17O5HNDB33C7X --paths "/*"
if %errorlevel% neq 0 (
    echo ERROR: CloudFront invalidation failed
    pause
    exit /b 1
)

echo [4/4] Done!
echo ========================================
echo Frontend updated successfully!
echo URL: https://d2gd95b8kmgmq8.cloudfront.net
echo ========================================
cd /d "%~dp0"
pause