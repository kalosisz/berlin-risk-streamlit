FROM python:3.7-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ADD https://raw.githubusercontent.com/funkeinteraktiv/Berlin-Geodaten/master/berlin_bezirke.geojson berlin_bezirke.geojson
COPY *.py ./
COPY .streamlit/ .streamlit/

EXPOSE 8080
ENTRYPOINT [ "streamlit","run","berlin.py" ]
