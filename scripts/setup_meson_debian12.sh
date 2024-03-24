sudo apt install meson ninja-build blueprint-compiler libglib2.0-dev gettext python3-pip python3-openpyxl python3-rich python3-mako
pip3 install -U spacy --user --break-system-packages
pip3 install -U spacy_langdetect --user --break-system-packages
pip3 install -U $(spacy info de_core_news_sm --url) --user --break-system-packages
pip3 install -U $(spacy info de_core_news_lg --url) --user --break-system-packages

