ODK = docker run -m 12g  -v $PWD/:/work -w /work --rm -ti obolibrary/odkfull

start-robot:
	$(ODK) robot python

