FROM pythonnet/pythonnet:python3.5-mono4.8.0-pythonnet2.3.0
LABEL maintainer="Klaus.Konarkowski@Ansys.com"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org

COPY . .

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]