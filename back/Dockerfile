FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

ENV API_KEY_FIREBASE=AIzaSyAaucGQDneM0f-AKbNTKgpcRNzW05wjbyM

ENV PORT=$PORT

EXPOSE $PORT

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
