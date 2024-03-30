<h2>Sentence</h2>
<p class="uk-text-lead">${var['sentence']['text']}</p>
<p>
    <h4>Tokens</h4>
    <ul class="uk-list uk-list-disc">
% for token in var['sentence']['properties']['tokens']:
        <li>
            <a class="uk-link-text" href="Token_${token}.html">${token}</a>
        </li>
% endfor
    </ul>
</p>

<% filenames = ', '.join(var['sentence']['properties']['filename']) %>
<p class="uk-text-meta">Seen in: ${filenames}</p>

