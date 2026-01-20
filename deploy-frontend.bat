@echo off
echo ========================================
echo Deploy Frontend a S3
echo ========================================

REM Obtener nombre del bucket
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name credit --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" --output text') do set CLOUDFRONT=%%i
for /f "tokens=*" %%i in ('aws s3 ls ^| findstr credit-frontendbucket') do set BUCKET_LINE=%%i
for %%a in (%BUCKET_LINE%) do set BUCKET=%%a

echo Bucket: %BUCKET%

echo.
echo [1/3] Instalando dependencias...
cd frontend
call npm install

echo.
echo [2/3] Compilando React...
call npm run build

echo.
echo [3/3] Subiendo a S3...
aws s3 sync build/ s3://%BUCKET%/ --delete

echo.
echo Frontend desplegado!
echo URL: https://%CLOUDFRONT%
pause
