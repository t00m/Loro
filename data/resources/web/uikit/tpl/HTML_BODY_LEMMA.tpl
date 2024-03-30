<%! from loro.backend.services.nlp import spacy %>

<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
    <h3 id="LEMMA">Lemma: ${var['lemma']['name']}</h3>
    <span class="uk-text-bold">${var['lemma']['name']}</span> is the lemma for the follwing tokens:
    <ul class="uk-list uk-list-striped uk-list-primary">
% for token in var['lemma']['tokens']:
<%
postag = spacy.explain_term(var['workbook']['cache']['tokens']['data'][token]['postags'][0]).title()
%>
        <li>
            <a class="uk-link-text" href="Token_${token}.html">${token}</a> (${postag})
        </li>
% endfor
    </lu>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->

<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
    <h3 id="SENTENCES">Sentences</h3>
    <ul class="uk-list uk-list-striped uk-list-primary">
<%
source = var['workbook']['source']
lemma = var['lemma']['name']
%>
% for sid in var['workbook']['cache']['lemmas']['data'][lemma]:
        <li>
            <a class="uk-link-text" href="Sentence_${sid}.html">
                ${var['workbook']['cache']['sentences']['data'][sid][source]}
            </a>
        </li>
% endfor
    </ul>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->
