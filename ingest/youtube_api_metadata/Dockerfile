FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY . "${LAMBDA_TASK_ROOT}"

CMD ["ingestor.lambda_handler"]