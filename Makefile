# only random once obviously ;)
python=venv/bin/python
pip=venv/bin/pip
pycodestyle=venv/bin/pycodestyle
pyresttest=venv/bin/pyresttest
manage=$(python) $(CURDIR)/manage.py

lint:
	$(pycodestyle) $(CURDIR)/nextcloudappstore --exclude=migrations

test: lint
	$(manage) test
	# assume that the testserver is running on port 8001

resetup:
	rm -f db.sqlite3
	rm -f $(CURDIR)/nextcloudappstore/**/migrations/0*.py
	$(manage) makemigrations
	$(manage) migrate
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json

# Only for local setup, do not use in production
dev-setup:
	pyvenv venv
	@echo "DEBUG = True" > $(CURDIR)/nextcloudappstore/local_settings.py
	@echo "SECRET_KEY = 'secret'" >> $(CURDIR)/nextcloudappstore/local_settings.py
	@echo "RECAPTCHA_PUBLIC_KEY = 'PUBLIC_KEY'" >> $(CURDIR)/nextcloudappstore/local_settings.py
	@echo "RECAPTCHA_PRIVATE_KEY = 'PRIVATE_KEY'" >> $(CURDIR)/nextcloudappstore/local_settings.py
	$(pip) install -r $(CURDIR)/requirements/development.txt
	$(pip) install -r $(CURDIR)/requirements/base.txt
	$(manage) migrate
	$(manage) loaddata $(CURDIR)/nextcloudappstore/**/fixtures/*.json
	@echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | $(manage) shell

