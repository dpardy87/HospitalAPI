FROM python:3.11-slim

# set container working dir
WORKDIR /app

# copy and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy the current directory container's /app
COPY . /app

# run the app
CMD ["python3", "lib/main.py"]
