# -*- coding: utf-8 -*-

def wrap():
    from ncm2_core import ncm2_core
    from ncm2 import getLogger
    import vim

    if not vim.eval("get(g:, 'ncm2_snipmate#completed_expand_enable', 1)"):
        return

    old_matches_decorate = ncm2_core.matches_decorate

    def new_matches_decorate(data, matches):
        matches = old_matches_decorate(data, matches)

        has_snippet = False

        for m in matches:
            ud = m['user_data']
            if not ud.get('is_snippet', False):
                continue
            has_snippet = True

        if has_snippet:
            for m in matches:
                ud = m['user_data']
                if ud.get('is_snippet', False):
                    # [+] sign indicates that this completion item is
                    # expandable
                    m['menu'] = '[+] ' + m['menu']
                else:
                    m['menu'] = '[ ] ' + m['menu']

        return matches

    ncm2_core.matches_decorate = new_matches_decorate

    vim.command(r'''
        let g:snipMateSources.ncm = funcref#Function('ncm2_snipmate#_snippets')
    ''')

wrap()

