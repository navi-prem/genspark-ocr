#! /bin/sh

if [ ! -d "uploads" ]; then 
	mkdir uploads
fi

python3 -m flask --app main run --debug

