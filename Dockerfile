FROM mrcatcis/awesome-python:1.0

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create App folder 
RUN mkdir /skedule-telegram
WORKDIR /skedule-telegram
# copy all files
COPY . /skedule-telegram/
# compile texts
RUN python3 compile_texts.py
# Run app
CMD ["python3", "main.py"]