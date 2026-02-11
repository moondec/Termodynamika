# Wymuszamy użycie nowego środowiska CONDA
# use_condaenv("termo", required = TRUE)

# Aktywujemy środowisko
use_virtualenv("termo", required = TRUE)

# Sprawdzamy wersję (powinno być 3.10.x)
py_config()

# Test CoolProp
# py_run_string("import CoolProp; print('Wersja CoolProp:', CoolProp.__version__)")

# Test biblioteki
py_run_string("import CoolProp.CoolProp as CP; print(CP.get_global_param_string('version'))")
