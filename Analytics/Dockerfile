FROM python
COPY  . /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["app.py"]

