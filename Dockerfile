FROM python:bullseye

WORKDIR /app

COPY requirements.txt .

#install make
RUN apt-get update && apt-get install -y make && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PORT=4000
ENV MODE=production

EXPOSE 4000

CMD ["make", "deploy"]
