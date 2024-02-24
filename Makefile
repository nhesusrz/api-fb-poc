#### Define these ####
SOURCE_DIR = _boilerplate
DOCS_TARGET= _boilerplate

COVERAGE_THRESHOLD = 80
FLAKE8_THRESHOLD = 0

# This one goes with export
export MAKE_BASE_TAG = 1.0
#### BOILERPLATE ####
MAKE_BASE_CHECKOUT_MSG := $(shell ./update_make_base.sh $(MAKE_BASE_TAG) )

ifdef MAKE_BASE_CHECKOUT_MSG
$(info $(MAKE_BASE_CHECKOUT_MSG))
endif

include ./make_base/Makefile.base
#### BOILERPLATE ####
