.PHONY: test demos site clean

PYTHONPATH := src
export PYTHONPATH

test:
	python3 -m unittest discover -s tests -v

demos:
	mkdir -p reports
	python3 -m tisa_portfolio.qoe_repro --out reports/qoe-foresight-repro.json
	python3 -m tisa_portfolio.cipherqoe --out reports/cipherqoe.json
	python3 -m tisa_portfolio.fedqoe --out reports/fedqoe-bench.json
	python3 -m tisa_portfolio.trustflow --out reports/trustflow-lab.json

site:
	python3 -m http.server 8000 --directory website

clean:
	find . -type d -name __pycache__ -prune -exec rm -r {} +
	find reports -type f -name '*.json' -delete
