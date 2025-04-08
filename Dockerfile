FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --no-cache.dir -r requiriments.txt 

EXPOSE 5000

CMD [ "python" , "app/app.py"]