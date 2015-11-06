include includes.mk

build:
	$(MAKE) -C client/ build
	$(MAKE) -C controller/ build

clean:
	$(MAKE) -C client/ clean
	$(MAKE) -C controller/ clean

commit-hook:
	cp contrib/util/commit-msg .git/hooks/commit-msg

test: test-style test-unit

test-unit:
	$(MAKE) -C client/ test-unit
	$(MAKE) -C controller/ test-unit

test-style:
	$(MAKE) -C client/ test-style
	$(MAKE) -C controller/ test-style

.PHONY: build clean commit-hook test test-unit test-style
