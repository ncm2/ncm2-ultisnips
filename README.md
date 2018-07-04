[snipMate](https://github.com/msanders/snipmate.vim) integration for
[ncm2](https://github.com/ncm2/ncm2).

## Features

- snippet completion source
- trigger dynamic snippet of completed item, e.g. parameter expansion.

## Install

```vim
" based on snipmate
Plug 'ncm2/ncm2-snipmate'

" snipmate dependencies
Plug 'tomtom/tlib_vim'
Plug 'marcweber/vim-addon-mw-utils'
Plug 'garbas/vim-snipmate'
```

## Vimrc Example

```vim
" Press enter key to trigger snippet expansion
" The parameters are the some as `:help feedkeys()`
inoremap <silent> <expr> <CR> ncm2_snipmate#expand_or("\<CR>", 'n')

" c-j c-k for moving in snippet
let g:snips_no_mappings = 1
vmap <c-j> <Plug>snipMateNextOrTrigger
vmap <c-k> <Plug>snipMateBack
imap <expr> <c-k> pumvisible() ? "\<c-y>\<Plug>snipMateBack" : "\<Plug>snipMateBack"
imap <expr> <c-j> pumvisible() ? "\<c-y>\<Plug>snipMateNextOrTrigger" : "\<Plug>snipMateNextOrTrigger"
```

`:help snipMate` for more information on using snipMate.
