FROM python:3.7-alpine
EXPOSE 8501
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ADD https://raw.githubusercontent.com/funkeinteraktiv/Berlin-Geodaten/master/berlin_bezirke.geojson berlin_bezirke.geojson
COPY *.py .
ENTRYPOINT [ "streamlit","run","berlin.py" ]
