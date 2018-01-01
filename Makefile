include Makefile.config
-include Makefile.custom.config
.SILENT:

make-p:
	# Launch all P targets in parallel and exit as soon as one exits.
	set -m; (for p in $(P); do ($(MAKE) $$p || kill 0)& done; wait)

serve-python:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

serve-react:
	$(NPM) start

serve:
	$(MAKE) P="serve-react serve-python" make-p

test-python:
	$(FLASK) test
