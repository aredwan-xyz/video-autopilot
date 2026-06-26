.PHONY: install serve dry run all report clean

install:        ## Install ffmpeg + venv + deps (macOS)
	bash scripts/install_mac.sh

serve:          ## Launch the web dashboard (http://127.0.0.1:8000)
	bash scripts/serve.sh

dry:            ## Build 1 video locally for $(CH), no posting (default motivation)
	python -m src.orchestrator --channel $(or $(CH),motivation) --count 1 --dry-run

run:            ## Build + publish 1 video for $(CH)
	python -m src.orchestrator --channel $(or $(CH),motivation) --count 1

all:            ## Run every channel (posts_per_day each) — the daily job
	python -m src.orchestrator --all

report:         ## Print the analytics / feedback report
	python -m src.orchestrator --report

clean:          ## Remove generated output (keeps history.json)
	find output -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +

help:
	@grep -E '^[a-z]+:.*##' Makefile | sed 's/:.*##/ —/'
