if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

inoremap <silent> <Plug>(ncm2_ultisnips_expand_completed) <c-r>=ncm2_ultisnips#_do_expand_completed()<cr>

func! ncm2_ultisnips#expand_or(...)
    if !pumvisible()
        call call('feedkeys', a:000)
        return ''
    endif
    let s:or_key = a:000
    return "\<c-y>\<c-r>=ncm2_ultisnips#_do_expand_or()\<cr>"
endfunc

func! ncm2_ultisnips#_do_expand_or()
    if ncm2_ultisnips#completed_is_snippet()
        call feedkeys("\<Plug>(ncm2_ultisnips_expand_completed)", "m")
        return ''
    endif
    call call('feedkeys', s:or_key)
    return ''
endfunc

func! ncm2_ultisnips#_do_expand_completed()
    if !ncm2_ultisnips#completed_is_snippet()
        echom "v:completed_item is not a snippet"
        return ''
    endif
    let completed = deepcopy(v:completed_item)
    let ud = json_decode(completed.user_data)
    let completed.user_data = ud
    if ud.snippet == ''
        " ultisnips builtin snippet
        call feedkeys("\<Plug>(_ncm2_ultisnips_expand)", "im")
        return ''
    endif
    let &undolevels = &undolevels
    py3 from ncm2_lsp_snippet.utils import apply_additional_text_edits
    py3 import vim
    py3 apply_additional_text_edits(vim.eval('json_encode(l:completed)'))
    let snippet = ud.ultisnips_snippet
    let trigger = ud.snippet_word
    let ret = UltiSnips#Anon(snippet, trigger, 'i', 'i')
    call feedkeys("\<Plug>(ncm2_skip_auto_trigger)", "m")
    return ret
endfunc

if !has("patch-8.0.1493")
    func! ncm2_ultisnips#_do_expand_or()
        call call('feedkeys', s:or_key)
        return ''
    endfunc
endif

func! ncm2_ultisnips#completed_is_snippet()
	if empty(v:completed_item)
		return 0
	endif
    silent! let ud = json_decode(v:completed_item.user_data)
    if empty(ud) || type(ud) != v:t_dict
        return 0
    endif
    return get(ud, 'is_snippet', 0)
endfunc

" completion source

let g:ncm2_ultisnips#source = extend(get(g:, 'ncm2_ultisnips#source', {}), {
            \ 'name': 'ultisnips',
            \ 'priority': 7,
            \ 'mark': 'us',
            \ 'word_pattern': '\S+',
            \ 'on_complete': 'ncm2_ultisnips#on_complete',
            \ }, 'keep')

func! ncm2_ultisnips#init()
    call ncm2#register_source(g:ncm2_ultisnips#source)

    exec 'imap <Plug>(_ncm2_ultisnips_expand)' g:UltiSnipsExpandTrigger

    if !has("patch-8.0.1493")
        echohl ErrorMsg
        echom 'ncm2-ultisnips requires has("patch-8.0.1493")'
            \  ' https://github.com/neovim/neovim/pull/8003'
        echohl None
    endif
endfunc

func! ncm2_ultisnips#on_complete(ctx)
	let snips = UltiSnips#SnippetsInCurrentScope()
	let matches = map(keys(snips),'{"word":v:val, "dup":1, "icase":1, "menu": l:snips[v:val], "user_data": {"is_snippet": 1}}')
	call ncm2#complete(a:ctx, a:ctx['startccol'], matches)
endfunc
