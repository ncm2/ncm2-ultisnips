
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
        echom "snippet trigger"
        return  "\<Plug>snipMateTrigger"
    endif
    echom "snippet not trigger"
    return s:or_key
endfunc

func! ncm2_snipmate#completed_is_snippet()
	if empty(v:completed_item)
		return 0
	endif
    if get(v:completed_item, 'user_data', '') == ''
        return 0
    endif
    
    try
        let ud = json_decode(v:completed_item.user_data)
        return ud.is_snippet
    catch
        return 0
    endtry
endfunc

func! ncm2_snipmate#_snippets(scopes, trigger, result)
	if empty(v:completed_item)
		return
	endif
    if get(v:completed_item, 'user_data', '') == ''
        return
    endif
    try
        let ud = json_decode(v:completed_item.user_data)
        if ud.is_snippet
            " use version 1 snippet syntax
            let word = v:completed_item.word
            let a:result[word] = {'default': [ud.snippet, 1]}
        endif
    catch
        echom 'ncm2_snipmate failed feeding snippet data: ' .
                \ v:completed_item.user_data . ', ' . 
                \ v:exception
    endtry
endfunc
