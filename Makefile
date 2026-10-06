# La guía de Semana 1 instala ANTLR aquí. También se acepta el JAR local.
ANTLR_JAR ?= $(firstword $(wildcard /usr/local/lib/antlr-4.13.1-complete.jar tools/antlr-4.13.1-complete.jar))
JAVA ?= java
PYTHON ?= python3

.PHONY: all generate test derivations package clean

all: generate

generate:
	@test -f "$(ANTLR_JAR)" || (echo 'Falta ANTLR 4.13.1: indique ANTLR_JAR o descargue el JAR en tools/.' >&2; exit 2)
	mkdir -p gen
	cd grammar && $(JAVA) -jar "$(abspath $(ANTLR_JAR))" -Dlanguage=Python3 -visitor -no-listener -Werror -o ../gen AlgaLexer.g4
	cd grammar && $(JAVA) -jar "$(abspath $(ANTLR_JAR))" -Dlanguage=Python3 -visitor -no-listener -Werror -lib ../gen -o ../gen AlgaParser.g4

test: generate
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) scripts/derivations.py --check

derivations: generate
	$(PYTHON) scripts/derivations.py

package:
	$(PYTHON) scripts/package.py

clean:
	rm -f gen/Alga*.py gen/Alga*.tokens gen/Alga*.interp
