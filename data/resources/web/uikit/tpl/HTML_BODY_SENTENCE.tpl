<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
    <h3 id="SENTENCE">Sentence</h3>
    <p class="uk-text-lead">${var['sentence']['text']}</p>
    <p>
        ${var['sentence']['svg']}
    </p>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->

<div class="uk-section"><!-- UK-SECTION :: START -->
    <div class="uk-container"> <!-- UK-CONTAINER :: START -->
    <h3 id="TOKENS">Tokens</h3>
    <ul class="uk-list uk-list-striped uk-list-primary">
% for token_id in var['sentence']['tokens']:
        <% token_name = var['tokens'][token_id]['title'] %>

        <li>
            <a class="uk-link-text" href="Token_${token_id}.html">${token_name}</a>
        </li>
% endfor
    </ul>
    </div><!-- UK-CONTAINER :: END -->
</div><!-- UK-SECTION :: END -->

<% filenames = ', '.join(var['sentence']['filename']) %>
<p class="uk-text-meta">Seen in: ${filenames}</p>


