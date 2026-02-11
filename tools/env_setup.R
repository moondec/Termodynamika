library(reticulate)

# ## CONDA
# # 1. Usuwamy stare środowisko 'termo' (jeśli istnieje), żeby zacząć na czysto
# try(conda_remove("termo"), silent = TRUE)
# try(virtualenv_remove("termo"), silent = TRUE) 
# 
# # 2. Tworzymy nowe środowisko CONDA z konkretną wersją Pythona (3.10 jest stabilna i nowoczesna)
# # To jest kluczowy moment - conda sama ściągnie nowszego Pythona!
# conda_create(envname = "termo", python_version = "3.10")
# 
# # 3. Instalujemy pakiety.
# # Uwaga: CoolProp najlepiej instalować przez pip (nawet wewnątrz condy), 
# # bo w kanałach conda-forge bywa z tym różnie.
# conda_install(envname = "termo", packages = c("numpy", "pandas", "matplotlib"), forge = TRUE)
# 
# # Instalacja CoolProp za pomocą pip wewnątrz środowiska conda 'termo'
# conda_install(envname = "termo", packages = "CoolProp", pip = TRUE)


# ## python ENV
# 1. To pobierze oficjalny, kompatybilny Python 3.10 (wersja Miniforge/Standalone)
# Może poprosić o zgodę na pobranie pliku (ok. 50-100MB)
install_python(version = "3.10")

# 2. Sprawdźmy, gdzie się zainstalował (powinien być w katalogu wirtualnym R)
# Zapamiętaj tę ścieżkę, choć reticulate powinien ją sam znaleźć
py_list <- virtualenv_starter(version = "3.10")
print(py_list)

# Tworzymy środowisko venv (nie conda!), używając pobranego Pythona
virtualenv_create("termo", version = "3.10")

# Instalujemy CoolProp i dodatki
virtualenv_install("termo", packages = c("numpy", "pandas", "CoolProp"))
