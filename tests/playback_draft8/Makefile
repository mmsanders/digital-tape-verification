.PHONY: check synthetic clean
check:
	python3 generate_fixture.py
	python3 selftest.py
synthetic:
	python3 runner.py --adapter-cmd "python3 _synthetic_adapter.py" --adapter-kind synthetic --adapter-id verifier-synthetic-public-api-model-v1 --adapter-source _synthetic_adapter.py --source-commit LOCAL --source-tree LOCAL --evidence-dir evidence/local-synthetic
clean:
	rm -rf evidence/local-synthetic __pycache__
