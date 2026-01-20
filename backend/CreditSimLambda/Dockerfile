FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install with platform-specific builds
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir --platform linux_x86_64 --only-binary=:all: -r requirements.txt

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]