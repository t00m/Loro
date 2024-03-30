<%! from loro.backend.services.nlp import spacy %>

<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
        <h3 id="POS">Parts of the speech</h3>
        <!-- WORDCLOUD :: START -->
        <div class="uk-grid-small uk-flex-middle uk-child-width-expand" uk-grid>
            <div class="uk-width-expand">
                <div class="uk-flex uk-flex-center uk-flex-wrap">
% for postag in var['workbook']['stats']['postags']:
                    <a class="uk-card uk-card-small uk-border-rounded uk-card-hover uk-card-body" href="#${postag}" uk-toggle>${spacy.explain_term(postag).title()}</a>

                    <div id="${postag}" uk-modal>
                        <div class="uk-modal-dialog">
                            <button class="uk-modal-close-default" type="button" uk-close></button>
                            <div class="uk-modal-header">
                                <h2 class="uk-modal-title">${spacy.explain_term(postag).title()}</h2>
                            </div>
                            <div class="uk-modal-body">
                                <div class="uk-grid-small uk-flex-middle uk-child-width-expand" uk-grid>
                                    <div class="uk-width-expand">
                                        <div class="uk-flex uk-flex-center uk-flex-wrap">

% for lemma in var['workbook']['stats']['postags'][postag]['lemmas']:
                                <a class="uk-card uk-card-small uk-border-rounded uk-card-hover uk-card-body" href="${postag}_${lemma}.html" uk-toggle>${lemma}</a>
% endfor
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="uk-modal-footer uk-text-right">
                                <button class="uk-button uk-button-default uk-modal-close" type="button">Close</button>
                            </div>
                        </div>
                    </div>
% endfor
                </div>
            </div>
        </div><!-- WORDCLOUD :: END -->
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->

<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
        <h3 id="FILES">Workbook files</h3>
        <ul class="uk-list">
% for filename in var['workbook']['files']:
            <li>
                <a class="uk-link-text" href="File_${filename}.html">${filename}</a>
            </li>
% endfor
        </ul>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->
