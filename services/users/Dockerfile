FROM python:3.7-alpine

EXPOSE 6001

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY python-libs.txt /usr/src/app/
RUN pip install --no-cache-dir -r python-libs.txt

COPY user_service.py .
COPY users.db .

CMD ["python3", "user_service.py"]