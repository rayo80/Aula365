FROM python:3.10

RUN python3 -m venv /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
ADD . /app

WORKDIR /app
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "300", "backend_almacen.wsgi"]
