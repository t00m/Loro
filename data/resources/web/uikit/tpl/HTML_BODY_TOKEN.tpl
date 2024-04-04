<%! from loro.backend.services.nlp import spacy %>
<%
    app = var['app']
    token = var['token']['name']
    postag = app.nlp.explain_term(var['token']['properties']['postags'][0]).title()
    lemma = var['token']['properties']['lemmas'][0]
    source = var['workbook']['source']
%>

<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
    <h3 id="TOKEN">${postag}: ${var['token']['name']}</h3>

    <ul class="uk-list uk-list-striped uk-list-primary">
% for key in var['token']['duden']:
    <%
    try:
        value = var['token']['duden'][key]
        if value is None:
            text = ''
        elif isinstance(value, str):
            text = value
        elif isinstance(value, list):
            text = ', '.join(value)
        elif isinstance(value, dict):
            text = ''
            for key in value:
                text += "%s (%s)<br/>" % (key, ', '.join(value[key]))
        else:
            text = str(value)
    except:
        text = str(value)
    %>
    <li><span class="uk-text-bold">${key}</span>: ${text}</a></li>
% endfor
    </ul>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->


<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
    <h3 id="SENTENCES">Sentences</h3>
    <ul class="uk-list uk-list-striped uk-list-primary">
% for sid in var['workbook']['cache']['tokens']['data'][token]['sentences']:
        <li>
            <a class="uk-link-text" href="Sentence_${sid}.html">
                ${var['workbook']['cache']['sentences']['data'][sid][source]}
            </a>
        </li>
% endfor
    </ul>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->

