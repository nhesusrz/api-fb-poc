FROM alpine:latest

RUN apk add --no-cache python3 py3-pip

WORKDIR /project

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080:8080

# TODO: Create default admin user.

CMD ["fabmanager", "run"]
