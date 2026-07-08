<!-- ### How to startup virtual enviorment -->
<!-- source .venv/bin/activate -->

### To install flatpak
```sh
flatpak run org.flatpak.Builder \
    --force-clean \
    --user \
    --install-deps-from=flathub \
    build-dir \
    flatpak/manifest.json
```

### to install flatpak to system
```sh
flatpak run org.flatpak.Builder \
    --force-clean \
    --user \
    --install \
    --install-deps-from=flathub \
    build-dir \
    flatpak/manifest.json
```

### to generate dependencies
python3 -m flatpak_pip_generator requests


### generate requirements.txt
<!-- pip3 install pip-tools --user -->
python3 -m piptools compile pyproject.toml -o requirements.txt