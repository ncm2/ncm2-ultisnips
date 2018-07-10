if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let s:ulft = 'ncm2'
let s:ulcmd = 'UltiSnips_Manager._added_snippets_source._snippets["' 
            \ . s:ulft
            \ . '"]._snippets = []'

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
        call ncm2_ultisnips#inject_completed_snippet()
        call feedkeys("\<Plug>(ncm2_ultisnips_expand)", "im")
        return ''
    endif
    call call('feedkeys', s:or_key)
    return ''
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

func! ncm2_ultisnips#inject_completed_snippet()
    exec g:_uspy 'UltiSnips_Manager._added_snippets_source._snippets["ncm"]._snippets = []'

    let ud = json_decode(v:completed_item.user_data)
    if has_key(ud, 'ultisnips_snippet')
        let w = ud.snippet_word
        let snippet = ud.ultisnips_snippet

        call UltiSnips#AddSnippetWithPriority(w, snippet, '', 'i', s:ulft, 1)
        return 1
    endif
    return 0
endfunc

func! ncm2_ultisnips#cleanup_injected_snippet()
    exec g:_uspy s:ulcmd
endfunc


" completion source

let g:ncm2_ultisnips#source = get(g:, 'ncm2_ultisnips#source', {
            \ 'name': 'ultisnips',
            \ 'priority': 7,
            \ 'mark': '',
            \ 'word_pattern': '\S+',
            \ 'on_warmup': 'ncm2_ultisnips#on_warmup',
            \ 'on_complete': 'ncm2_ultisnips#on_complete',
            \ })

let g:ncm2_ultisnips#source = extend(g:ncm2_ultisnips#source,
            \ get(g:, 'ncm2_ultisnips#source_override', {}),
            \ 'force')

func! ncm2_ultisnips#init()
    call ncm2#register_source(g:ncm2_ultisnips#source)
    exe 'imap' "<Plug>(ncm2_ultisnips_expand)" g:UltiSnipsExpandTrigger

    " FIXME UltiSnips somehow don't play well when LanguageClient-neovim is
    " auto applying text edits in
    "    autocmd CompleteDone * call LanguageClient#handleCompleteDone()
    augroup languageClient
        autocmd! CompleteDone
    augroup END
endfunc

func! ncm2_ultisnips#on_warmup(ctx)
    if get(b:, 'ncm2_ultisnips_setup', 0)
        return
    endif
    let b:ncm2_ultisnips_setup = 1
    if has("patch-8.0.1493")
        call UltiSnips#AddFiletypes(s:ulft)
        autocmd InsertLeave <buffer> call ncm2_ultisnips#cleanup_injected_snippet()
    else
        echohl ErrorMsg
        echom 'ncm2-ultisnips requires has("patch-8.0.1493")'
            \  ' https://github.com/neovim/neovim/pull/8003'
        echohl None
    endif
endfunc

func! ncm2_ultisnips#on_complete(ctx)
	let snips = UltiSnips#SnippetsInCurrentScope()
	let matches = map(keys(snips),'{"word":v:val, "dup":1, "icase":1, "info": l:snips[v:val], "user_data": {"is_snippet": 1}}')
	call ncm2#complete(a:ctx, a:ctx['startccol'], matches)
endfunc
