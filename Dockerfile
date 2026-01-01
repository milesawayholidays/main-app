FROM python:bullseye

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip \
	&& python -m pip install --no-cache-dir -r requirements.txt

#install make
RUN apt-get update && apt-get install -y make && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PORT=4000
ENV MODE=production

EXPOSE 4000

CMD ["sh", "-c", "python -m uvicorn src.app:APP --host 0.0.0.0 --port ${PORT:-4000}"]
