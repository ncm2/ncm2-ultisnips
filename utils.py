
def apply_additional_text_edits(completed):
    import vim
    import json
    if type(completed) is str:
        completed = json.loads(completed)
    ud = completed['user_data']
    additional_text_edits = ud.get('additional_text_edits', None)
    completion_item = ud.get('completion_item', {})
    data = completion_item.get('data', None)

    if not additional_text_edits and data:
        resolved = vim.call('LanguageClient_runSync', 'LanguageClient#completionItem_resolve', completion_item)
        vim.vars['completed'] = completed
        vim.vars['completion_item'] = completion_item
        vim.vars['resolved'] = resolved
        additional_text_edits = resolved.get('additionalTextEdits', None)

    if not additional_text_edits:
        return

    additional_text_edits.sort(key=lambda e: [- e['range']['start']['line'], - e['range']['start']['character']])

    buf = vim.current.buffer
    for edit in additional_text_edits:
        start = edit['range']['start']
        end = edit['range']['end']
        new_text = edit['newText']
        lines = buf[start['line']: end['line'] + 1]
        prefix = lines[0][: start['character']]
        postfix = lines[-1][end['character']: ]
        new_text = prefix + new_text + postfix
        vim.vars['new_text'] = new_text.split("\n")
        buf[start['line']: end['line'] + 1] = new_text.split("\n")

def snippet_escape_text(txt):
    txt = txt.replace('\\', '\\\\')
    txt = txt.replace('$', r'\$')
    txt = txt.replace('}', r'\}')
    return txt

# convert lsp snippet into snipmate snippet
def match_formalize(ctx, item):
    ud = item['user_data']
    lnum = ctx['lnum']
    ccol = ctx['ccol']

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
    text_edit = ud.get('text_edit', None)
    if text_edit:
        # prefer text_edit
        testart = text_edit['range']['start']
        teend = text_edit['range']['end']
        new_text = text_edit['newText']
        if (testart['line'] == lnum - 1 and
            teend['character'] == ccol - 1):
            if is_snippet:
                ud['snippet'] = new_text
            else:
                item['word'] = new_text
                item['abbr'] = new_text
            ud['startccol'] = testart['character'] + 1

        # we don't need text_edit anymore, in case LanguageClient-neovim
        # is messing with it in CompleteDone
        del ud['text_edit']

    if 'completion_item' in ud:
        completion_item = ud['completion_item']
        if 'data' in completion_item:
            # snippet with additionalTextEdits after resolve
            if not is_snippet:
                ud['is_snippet'] = is_snippet = 1
                ud['snippet'] = snippet_escape_text(item['word'])

    if is_snippet and 'snippet_word' not in ud:
        ud['snippet_word'] = item['word']

    return item
