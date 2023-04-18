FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py unfaithful.avsc unfaithful.csv ./

CMD [ "python", "./main.py" ]
