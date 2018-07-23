
def apply_additional_text_edits(completed):
    import vim
    import json
    if type(completed) is str:
        completed = json.loads(completed)
    ud = completed['user_data']
    lspitem = ud.get('ncm2_lspitem', None)
    if lspitem:
        apply_lsp_additional_text_edits(lspitem)


def apply_lsp_additional_text_edits(lspitem):
    import vim
    import json

    additional_text_edits = lspitem.get('additionalTextEdits', None)

    data = lspitem.get('data', None)
    if not additional_text_edits and data:
        # for vim8 compatibility
        vim.vars['_ncm2_lsp_snippet_tmp'] = json.dumps(lspitem)
        expr = r"json_encode(LanguageClient_runSync('LanguageClient#completionItem_resolve', json_decode(g:_ncm2_lsp_snippet_tmp), {}))"
        resolved = json.loads(vim.eval(expr))
        additional_text_edits = resolved.get('additionalTextEdits', None)

    if not additional_text_edits:
        return

    additional_text_edits.sort(
        key=lambda e: [- e['range']['start']['line'],
                       - e['range']['start']['character']])

    buf = vim.current.buffer
    for edit in additional_text_edits:
        start = edit['range']['start']
        end = edit['range']['end']
        new_text = edit['newText']
        lines = buf[start['line']: end['line'] + 1]
        prefix = lines[0][: start['character']]
        postfix = lines[-1][end['character']:]
        new_text = prefix + new_text + postfix
        buf[start['line']: end['line'] + 1] = new_text.split("\n")

        # this is super stupid but I'm not sure there's a safe escape
        # function for vim, and I don't want external dependency either.
        vim.vars['_ncm2_lsp_snippet_tmp'] = "auto edit: " + edit['newText']
        vim.command("echom g:_ncm2_lsp_snippet_tmp")
        del vim.vars['_ncm2_lsp_snippet_tmp']


def snippet_escape_text(txt):
    txt = txt.replace('\\', '\\\\')
    txt = txt.replace('$', r'\$')
    txt = txt.replace('}', r'\}')
    return txt


def match_formalize_from_lspitem(ctx, item, lspitem):
    ud = item['user_data']
    label = lspitem['label']
    item['abbr'] = label

    is_snippet = lspitem.get('insertTextFormat', 1) == 2
    ud['is_snippet'] = is_snippet

    if 'insertText' in lspitem:
        item['word'] = lspitem['insertText']
    else:
        item['word'] = label

    if is_snippet:
        item['word'] = label

    ud['snippet'] = lspitem.get('insertText', label)

    # prefer text_edit
    te = lspitem.get('textEdit', None)
    if te:
        testart = te['range']['start']
        teend = te['range']['end']
        new_text = te['newText']
        # Note from spec:
        # *Note:* The range of the edit must be a single line range and
        # it must contain the position at which completion has been
        # requested.
        if (testart['line'] == ctx['lnum'] - 1 and
                teend['character'] <= ctx['ccol'] - 1):
            if is_snippet:
                ud['snippet'] = new_text
            else:
                item['word'] = new_text
            ud['startccol'] = testart['character'] + 1

    if 'data' in lspitem:
        # snippet with additionalTextEdits after resolve
        ud['is_snippet'] = 1
        is_snippet = 1
        if not ud.get('snippet', None):
            ud['snippet'] = snippet_escape_text(item['word'])

    # we don't need lspitem anymore, in case LanguageClient-neovim. is
    # messing with it in CompleteDone
    if 'lspitem' in ud:
        ud['ncm2_lspitem'] = ud['lspitem']
        del ud['lspitem']


def match_formalize(ctx, item):
    ud = item['user_data']  # type: dict
    lnum = ctx['lnum']
    ccol = ctx['ccol']

    if 'lspitem' in ud:
        match_formalize_from_lspitem(ctx, item, ud['lspitem'])

    ud.setdefault('snippet', '')
    is_snippet = ud.setdefault('is_snippet', 0)

    if is_snippet:
        ud.setdefault('snippet_word', item['word'])
    return item
