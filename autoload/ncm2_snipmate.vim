if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let s:completed = {}

func! ncm2_snipmate#expand_or(or_key)
    if !pumvisible()
        return a:or_key
    endif
    let s:or_key = a:or_key
    return "\<c-y>\<Plug>(_ncm2_snipmate)"
endfunc

imap <expr> <Plug>(_ncm2_snipmate) ncm2_snipmate#_do_expand_or()

func! ncm2_snipmate#_do_expand_or()
    if ncm2_snipmate#completed_is_snippet()
        let s:completed = v:completed_item
        return  "\<Plug>snipMateTrigger"
    endif
    return s:or_key
endfunc

func! ncm2_snipmate#completed_is_snippet()
	if empty(v:completed_item)
		return 0
	endif
    silent! let ud = json_decode(v:completed_item.user_data)
    if empty(ud) || type(ud) != v:t_dict
        return 0
    endif
    return get(ud, 'is_snippet', 0)
endfunc

func! ncm2_snipmate#_snippets(scopes, trigger, result)
	if empty(s:completed)
		return
	endif
    if get(s:completed, 'user_data', '') == ''
        return
    endif
    try
        let ud = json_decode(s:completed.user_data)
        if ud.is_snippet && ud.snipmate_snippet != ''
            " use version 1 snippet syntax
            let word = s:completed.word
            let a:result[word] = {'default': [ud.snipmate_snippet, 1]}
        endif
    catch
        echom 'ncm2_snipmate failed feeding snippet data: ' .
                \ s:completed.user_data . ', ' . 
                \ v:exception
    endtry
endfunc

" completion source

let g:ncm2_snipmate#source = get(g:, 'ncm2_snipmate#source', {
            \ 'name': 'snipmate',
            \ 'priority': 7,
            \ 'mark': '',
            \ 'on_complete': 'ncm2_snipmate#on_complete',
            \ })

let g:ncm2_snipmate#source = extend(g:ncm2_snipmate#source,
            \ get(g:, 'ncm2_snipmate#source_override', {}),
            \ 'force')

func! ncm2_snipmate#init()
    call ncm2#register_source(g:ncm2_snipmate#source)
    let g:snipMateSources.ncm = funcref#Function('ncm2_snipmate#_snippets')
endfunc

func! ncm2_snipmate#on_complete(ctx)
	let word    = snipMate#WordBelowCursor()
	let matches = map(snipMate#GetSnippetsForWordBelowCursorForComplete(''),'extend(v:val,{"dup":1, "user_data": {"is_snippet": 1, "snippet": ""}})')
    let ccol = a:ctx['ccol']
    let startccol = a:ctx['ccol'] - strchars(word)
	call ncm2#complete(a:ctx, startccol, matches)
endfunc

" FIXME snipmate somehow don't play well when LanguageClient-neovim is auto
" applying text edits in
"    autocmd CompleteDone * call LanguageClient#handleCompleteDone()
augroup languageClient
    autocmd! CompleteDone
augroup END
