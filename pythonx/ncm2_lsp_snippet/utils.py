
# convert lsp snippet into snipmate snippet
def match_formalize(ctx, item):
    ud = item['user_data']

    # fix data pass from LanguageClient
    if 'is_snippet' in item and 'is_snippet' not in ud:
        ud['is_snippet'] = item['is_snippet']
    if 'snippet' in item and 'snippet' not in ud:
        ud['snippet'] = item['snippet']
    if 'text_edit' in item and 'text_edit' not in ud:
        ud['text_edit'] = item['text_edit']

    # default is_snippet
    if 'is_snippet' not in ud:
        ud['is_snippet'] = 0
    if 'snippet' not in ud:
        ud['snippet'] = ''

    is_snippet = ud['is_snippet']

    # fix data pass from LanguageClient, we don't want snippet in word
    if is_snippet and item['word'] == ud['snippet']:
        item['word'] = item['abbr']

    # fix data pass from LanguageClient
    lnum, ccol, startccol = ctx['lnum'], ctx['ccol'], ctx['startccol']
    text_edit = ud.get('text_edit', None)
    if text_edit:
        # camel case -> underscore
        if 'new_text' not in text_edit and 'newText' in text_edit:
            text_edit['new_text'] = text_edit['newText']
            del text_edit['newText']
        # prefer text_edit
        testart = text_edit['range']['start']
        teend = text_edit['range']['end']
        new_text = text_edit['new_text']
        if (testart['line'] == lnum - 1 and
            testart['character'] == startccol - 1 and
            teend['character'] == ccol - 1):
            if is_snippet:
                ud['snippet'] = new_text
            else:
                ud['word'] = new_text

    if is_snippet and 'snippet_word' not in ud:
        ud['snippet_word'] = item['word']

    return item

