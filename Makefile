# ===================
# =		VARIABLES	=
# ===================

PYTHON			=	python3
PDB 			=	python3 -m pdb
UV_PYTHON		=	uv run python
FLAKE8			=	uv run flake8
MYPY 			=	uv run mypy
MYPY_FLAGS		=	--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
INSTALL_UV		=	curl -LsSf https://astral.sh/uv/install.sh | sh
CHECK_UV		=	command -v uv
UV_WARN			=	--link-mode copy
UV_SKIP_WHEEL	=	UV_SKIP_WHEEL_FILENAME_CHECK=1
LINT_TESTER		=	src \
					main.py \

# ===================
# =		RULES		=
# ===================

.PHONY:		all install run debug clean fclean lint lint-strict

all:		install run

install:
			@if	! $(CHECK_UV) > /dev/null 2>&1; then \
					echo "$(BRED)UV not installed. Installing...$(RESET)"; \
					$(INSTALL_UV); \
			fi
			@echo "$(BGREEN)Installing project dependencies using uv...$(RESET)"
			$(UV_SKIP_WHEEL) uv sync $(UV_WARN)

run:		install
			$(UV_PYTHON) main.py

debug:		install
			@echo "$(BGREEN)Running the main script in debug mode...$(RESET)"
			$(PDB) main.py

clean:
			@clear
			@echo "$(YELLOW)Cleaning temporary files, and caches...$(RESET)"
			find . -type d -name "__pycache__" -exec rm -rf {} +
			rm -rf .mypy_cache
			rm -rf .pytest_cache

fclean:		clean
			@echo "$(YELLOW)Cleaning .venv...$(RESET)"
			rm -rf .venv

lint:
			@clear
			@echo "$(BMAGENTA)Running standard linting...$(RESET)"
			@status=0; \
			$(FLAKE8) $(LINT_TESTER) || status=$$?; \
			$(MYPY) $(LINT_TESTER) $(MYPY_FLAGS) || status=$$?; \
			exit $$status

lint-strict:
			@clear
			@echo "$(BMAGENTA)Running strict linting...$(RESET)"
			@status=0; \
			$(FLAKE8) $(LINT_TESTER) || status=$$?; \
			$(MYPY) $(LINT_TESTER) $(MYPY_FLAGS) --strict || status=$$?; \
			exit $$status

# ===================
# =		COLORS		=
# ===================

RESET		=	\033[0m
BGREEN		=	\033[92m
BMAGENTA	=	\033[95m
YELLOW		=	\033[93m
BRED		=	\033[91m
