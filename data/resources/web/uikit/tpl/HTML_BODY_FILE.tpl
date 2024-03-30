<h2>${var['html']['title']}</h2>
<p>
    <h3 id="SENTENCES">Sentences</h3>
    <ul class="uk-list uk-list-striped uk-list-primary">
<%  source = var['workbook']['source'] %>
% for sid in var['filename']['sentences']:
        <li>
            <a class="uk-link-text" href="Sentence_${sid}.html">
                ${var['workbook']['cache']['sentences']['data'][sid][source]}
            </a>
        </li>
% endfor
    </ul>
</p>
