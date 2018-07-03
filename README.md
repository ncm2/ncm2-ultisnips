
This plugin contains snippet completion source, and a small tool to help
trigger snippet expansion of ncm2 completion item based on
[snipMate](https://github.com/msanders/snipmate.vim).

vimrc config:

```vim
" press enter key to trigger snippet expansion
imap <expr> <CR> ncm2_snipmate#expand_or("\<CR>")

" c-j c-k for moving in snippet
let g:snips_no_mappings = 1
vmap <c-j> <Plug>snipMateNextOrTrigger
vmap <c-k> <Plug>snipMateBack
imap <expr> <c-k> pumvisible() ? "\<c-y>\<Plug>snipMateBack" : "\<Plug>snipMateBack"
imap <expr> <c-k> pumvisible() ? "\<c-y>\<Plug>snipMateNextOrTrigger" : "\<Plug>snipMateNextOrTrigger"
```

`:help snipMate` for more information on using snipMate.
