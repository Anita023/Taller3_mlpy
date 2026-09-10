FROM  python:3.10-slim

WORKDIR /app

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#Entrena y genera el artefacto en el build 
RUN python train.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]